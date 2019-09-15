#==================================================================
# this is a function for generating mathematical model of DCO,
# mostly for transient simulation run time estimation
#==================================================================

import argparse
import sys
import math
import subprocess as sp
import fileinput
import re
import os
import shutil

import HSPICE_mds
import HSPICE_netlist
import HSPICE_tb
import HSPICE_result
#import HSPICE_result_FC
#import HSPICErf_result
import HSPICE_tbrf
import MKfile 
import HSPICE_Kwrt 
import HSPICE_Kpnwrt 
import imp
#Kg_solver=imp.load_source('Kg_solver','./model/Kg_solver.py')
import Kg_solver

#===========================================================
# prints out the error rate of math model
#===========================================================
def math_model_verify(formatDir,write_model_file,CF,Cc,Cf,dm,result_exist,freq,Fmax,Fmin,Fres,Iavg,print_error):
	Fnom_err=[]    
	Fmax_err=[]    
	Fmin_err=[]    
	Fres_err=[]    
	Iavg_const=[]    
	for nd in result_exist:
		N_fc=dm[nd][3]	  
		N_cc=dm[nd][1]	
		N_drv=dm[nd][0]
		N_stg=dm[nd][2]
		Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal=spec_cal(N_drv,N_cc,N_fc,N_stg,Cc,Cf,CF)
		Fnom_err.append(abs(Fnom_mdl-freq[nd][0][0])/freq[nd][0][0]*100)
		Fmax_err.append(abs(Fmax_mdl-Fmax[nd][0][0])/Fmax[nd][0][0]*100)
		Fmin_err.append(abs(Fmin_mdl-Fmin[nd][0][0])/Fmin[nd][0][0]*100)
		Fres_err.append(abs(Fres_mdl-Fres[nd][0][0])/Fres[nd][0][0]*100)
		#--- Iavg constant gen ---
		Ctotal=Cc*(N_drv+N_cc/2)+Cf*N_fc+CF*N_fc/2
		Iavg_const.append(Iavg[nd][0][0]/Ctotal)
#		if print_error==1:
#			print ("N_cc= %d,N_drv=%d, Nfc= %d, Nstg=%d"%(N_cc,N_drv,N_fc,N_stg)),
#			print (abs(Iavg[nd][0][0])),
#			print (abs(Iavg[nd][0][0]/Ctotal))
		Kg_mdl=1/((N_drv+N_cc)*Cc+N_fc*Cf+N_fc/2*CF)
		#print (Kg[nd][0][0]/Kg_mdl)  #checking if Kg is okay	
		#print (Fnom_mdl,freq[nd][0][0])
	Fnom_err_mean=sum(Fnom_err)/len(Fnom_err)
	Fnom_err_max=max(Fnom_err)	
	Fmax_err_mean=sum(Fmax_err)/len(Fmax_err)
	Fmax_err_max=max(Fmax_err)	
	Fmin_err_mean=sum(Fmin_err)/len(Fmin_err)
	Fmin_err_max=max(Fmin_err)	
	Fres_err_mean=sum(Fres_err)/len(Fres_err)
	Fres_err_max=max(Fres_err)
	Iavg_const_avg=sum(Iavg_const)/len(Iavg_const)
	#print (Iavg_const)
	Iavg_err=[]
	for i in Iavg_const:
		Iavg_err.append(abs(i-Iavg_const_avg)/abs(i)*100)
		
	Iavg_err_mean=sum(Iavg_err)/len(Iavg_err)
	Iavg_err_max=max(Iavg_err)
	if print_error==1:	
		print ('Fnom_err_mean,max=%f,%f, Fmax=%f,%f, Fmin=%f,%f, Fres=%f,%f, Iavg=%f,%f'%(Fnom_err_mean,Fnom_err_max,Fmax_err_mean,Fmax_err_max,Fmin_err_mean,Fmin_err_max,Fres_err_mean,Fres_err_max,Iavg_err_mean,Iavg_err_max)) 

	#--- write the model.json ---
	r_model=open(formatDir+'form_model.json','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('CF',None,CF,CF,1)	
	nm1.get_net('Cc',None,Cc,Cc,1)	
	nm1.get_net('Cf',None,Cf,Cf,1)
	nm1.get_net('Ic',None,abs(Iavg_const_avg),abs(Iavg_const_avg),1)
	with open(write_model_file,'w') as w_model:
		lines=list(r_model.readlines())
		for line in lines:
			nm1.printline(line,w_model)
		print('model file generated: '+write_model_file)	
		#w_model.write('Fnom_err_mean,max=%f,%f, Fmax=%f,%f, Fmin=%f,%f, Fres=%f,%f, Iavg=%f,%f'%(Fnom_err_mean,Fnom_err_max,Fmax_err_mean,Fmax_err_max,Fmin_err_mean,Fmin_err_max,Fres_err_mean,Fres_err_max,Iavg_err_mean,Iavg_err_max)) 

	return Iavg_const

def math_model_gen(vm1,netlist_dir,format_dir,vdd,temp,tech_node,resultrf_dir,num_core,result_dir,index,show,num_meas):
	#------------------------------------------------------------------------------
	#  netlist.sp, tb.sp generation 
	#------------------------------------------------------------------------------
	#for i in range(1,len(vm1.comblist[0])):
	#	netlist=HSPICE_netlist.gen_netlist(netlist_dir,format_dir,vm1.comblist[0][i],vm1.comblist[1][i],vm1.comblist[2][i],vm1.comblist[3][i],vm1.comblist[3][i],1)
	#	tb=HSPICE_tb.gen_tb(PDK,tb_dir,format_dir,vm1.comblist[0][i],vm1.comblist[1][i],vm1.comblist[2][i],vm1.comblist[3][i],vm1.comblist[3][i],1,vdd,temp,500)
	
	#------------------------------------------------------------------------------
	# Makefile generation for hspice simulation 
	#------------------------------------------------------------------------------
	#form_mkfile=MKfile.gen_mkfile_form(tech_node,format_dir,tb_dir,result_dir,tbrf_dir,resultrf_dir,num_core)
	#mkfile=MKfile.gen_mkfile_v2(format_dir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],0,0)
	#format_dir,ncell,ndrv,nfc,nstg,rf_ready,result_exist
	
	#------------------------------------------------------------------------------
	# Run HSPICE sim 
	#------------------------------------------------------------------------------
	#p=sp.Popen(['make','hspicesim'])
	#p.wait()
	
	
	#------------------------------------------------------------------------------
	# Read transient sim result, receive nominal frequencies
	#------------------------------------------------------------------------------
#	idK,Kg,freq,result_exist,dm=HSPICE_result.gen_result_v3(result_dir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],num_meas,index,show,vdd,temp)
	idK,Kg,freq,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=HSPICE_result.gen_result_v3(result_dir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],num_meas,index,show,vdd,temp)
	CF=[]	
	Cc=[]	
	Cf=[]
	for i in result_exist:
		for j in result_exist:
			if i<j:
				Ncell_1=dm[i][1]+dm[i][0]  #Nc+Nd
				Nfc_1=dm[i][3]
				Ncell_2=dm[j][1]+dm[j][0]  #Nc+Nd
				Nfc_2=dm[j][3]
				cf1=[Ncell_1,Nfc_1,Nfc_1//2]
				cf2=[Ncell_2,Nfc_2,Nfc_2//2]
				#cf1=[16,16,16//2]
				#cf2=[16,32,32//2]
				if (Ncell_1==Ncell_2 and Nfc_1!=Nfc_2) or (Ncell_1!=Ncell_2 and Nfc_1==Nfc_2):
					CF1_temp,Cc1_temp,Cf1_temp=Kg_solver.C_solve_v2(Kg[i],Kg[j],idK[i],idK[j],cf1,cf2)
					CF.append(CF1_temp)				
					Cc.append(Cc1_temp)				
					Cf.append(Cf1_temp)
					#print ("Ncell= %d, %d, Nfc= %d, %d, Kg[i]=%e,Kg[j]=%e, idK=%e, %e"%(Ncell_1,Ncell_2,Nfc_1,Nfc_2,Kg[i][0][0],Kg[j][0][0],idK[i][0][0],idK[j][0][0]))
	CF_avg=sum(CF)/len(CF)
	CF_max_err=max(abs(CF_avg-min(CF)),abs(CF_avg-max(CF)))/CF_avg*100
	Cc_avg=sum(Cc)/len(Cc)
	Cc_max_err=max(abs(Cc_avg-min(Cc)),abs(Cc_avg-max(Cc)))/Cc_avg*100
	Cf_avg=sum(Cf)/len(Cf)
	Cf_max_err=max(abs(Cf_avg-min(Cf)),abs(Cf_avg-max(Cf)))/Cf_avg*100
	#print ('CF_avg=%e'%(CF_avg))
	#print ('Cc_avg=%e'%(Cc_avg))
	#print ('Cf_avg=%e'%(Cf_avg))
	#print ('CF_max_err=%f'%(CF_max_err))
	#print ('Cc_max_err=%f'%(Cc_max_err))
	#print ('Cf_max_err=%f'%(Cf_max_err))
	return CF_avg,Cc_avg,Cf_avg,CF_max_err,Cc_max_err,Cf_max_err	



#=====================================================================
# calculate math mdl specs according to design params 
#=====================================================================
def spec_cal(Nd,Nc,Nf,M,Cc,Cf,CF):
	Np=Nd+Nc
	CB=(Np)*Cc+Nf*Cf
	Fnom_fcmax=(Nd+Nc/2)/(CB*M)
	Fnom_fcmin=(Nd+Nc/2)/((CB+Nf*CF)*M)
	Fres_mdl=(Fnom_fcmax-Fnom_fcmin)/Nf/M
	dFf_mdl=Fnom_fcmax-Fnom_fcmin
	dFc_mdl=1/CB/M/Nc    # is this right?
	freqCoverRatio=dFf_mdl/dFc_mdl
	Ctotal=Cc*(Nd+Nc/2)+Cf*Nf+CF*Nf/2
	Fmin_mdl=1/(CB+Nf*CF)*(Nd)/M
	Fmax_mdl=1/(CB)*(Nd+Nc)/M
	Fnom_mdl=(Nd+Nc/2)/(CB*M)
	return Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal

#--- this model should be improved ---	
def spec_cal_pex65(Nd,Nc,Nf,M,Cc,Cf,CF,mult_Con,mult_Coff):
	Np=Nd+Nc
	Cc_on_pex=Cc*mult_Con
	Cc_off_pex=Cc*mult_Coff
	Cf_on_pex=Cf*mult_Con

	CF_on_pex=CF*mult_Con
	CB=Nd*Cc_on_pex

	#Fnom_fcmax=(Nd+Nc/2)/((CB+Nc/2*Cc_on_pex+Nc/2*Cc_off_pex)*M)
	#Fnom_fcmin=(Nd+Nc/2)/(((CB+Nc/2*Cc_on_pex+Nc/2*Cc_off_pex)+Nf*CF_on_pex)*M)
	#dFf_mdl=Fnom_fcmax-Fnom_fcmin
	#dFc_mdl=(1/CB-1/(CB+Cc_on_pex))/M/Nc    # is this right?
	#freqCoverRatio=dFf_mdl/dFc_mdl
	#Fres_mdl=(Fnom_fcmax-Fnom_fcmin)/Nf/M
	#Fres_mdl=(1/(CB)-1/(CB+CF))*(Nd+Nc)/M

	Fmin_mdl=1/(CB+Cc_off_pex*Nc+Nf*CF)*(Nd)/M
	Fmax_mdl=1/(CB+Nc*Cc_on_pex)*(Nd+Nc)/M
	Fnom_mdl=(Nd+Nc/2)/((CB+Nc/2*Cc_on_pex+Nc/2*Cc_off_pex)*M)
	Ctotal=(CB+Nc/2*Cc_on_pex+Nc/2*Cc_off_pex)+Cf*Nf+CF*Nf/2

	Fmax_pre,Fmin_pre,Fres_pre,Fnom_pre,FCR_pre,Ctotal_pre=spec_cal(Nd,Nc,Nf,M,Cc,Cf,CF)
	Fres_mdl=Fres_pre/(Fmin_pre/Fmin_mdl)	
	dFf_mdl=Fres_mdl*M*Nf	
	dFc_mdl=dFf_mdl*FCR_pre/(Fmin_pre/Fmin_mdl)
	freqCoverRatio=dFf_mdl/dFc_mdl

	return Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal
 
