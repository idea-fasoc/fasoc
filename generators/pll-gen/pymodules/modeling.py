import math
import run_pre_sim
import run_pex_sim
import txt_mds
import sys

#===============================================================================================
# pass_flag, spec_range added
#	pass_flag: 1(passed), 0(failed)
#	spec_range: provide spec range in the spec order of spec_priority
#	spec_priority: ex) [Fnom, IB_PN, dco_PWR,Fmax,....]
#			Fnom includes Fnom_*
#===============================================================================================

def design_solution(spec_priority,Fmax,Fmin,Fres,Fnom_min,Fnom_max,FCR_min,IB_PN,dco_PWR,CF,Cf,Cc,mult_Con,mult_Coff,Iavg_const,PN_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC,modelVersion, FC_half, dead_CC, ND):
	pass_flag=0
	passed_designs=[]
	passed_specs=[]
	spec_ranges=[]

	num_Ndrv=int((Ndrv_range[1]-Ndrv_range[0])/Ndrv_range[2])+1	
	num_Nfc=int((Nfc_range[1]-Nfc_range[0])/Nfc_range[2])+1	
	num_Ncc=int((Ncc_range[1]-Ncc_range[0])/Ncc_range[2])+1	
	num_Nstg=int((Nstg_range[1]-Nstg_range[0])/Nstg_range[2])+1
	
	Ndrv_list=[]	
	Nfc_list=[]	
	Ncc_list=[]	
	Nstg_list=[]	
	for i in range(num_Ndrv):
		Ndrv_list.append(Ndrv_range[0]+i*Ndrv_range[2])
	for i in range(num_Nfc):
		Nfc_list.append(Nfc_range[0]+i*Nfc_range[2])
	for i in range(num_Ncc):
		Ncc_list.append(Ncc_range[0]+i*Ncc_range[2])
	for i in range(num_Nstg):
		Nstg_list.append(Nstg_range[0]+i*Nstg_range[2])
	#===============================================================
	# generate dictionary list for input specs 
	#===============================================================
	if modelVersion=='Beta':
		inSpecDic={"Fmax":Fmax,"Fnom_max":Fnom_max,"Fnom_min":Fnom_min,"Fmin":Fmin,"Fres":Fres,"FCR":FCR_min,"dco_PWR":dco_PWR,"IB_PN":IB_PN}					
	elif modelVersion=='Alpha' or modelVersion=='Alpha_pex':
		inSpecDic={"Fmax":Fmax,"Fnom_max":Fnom_max,"Fnom_min":Fnom_min,"Fmin":Fmin,"Fres":Fres,"FCR":FCR_min,"dco_PWR":dco_PWR}					
	#===============================================================
	# generate dictionary list for failed spec ranges
	#===============================================================
	fst_pass=[]
	fst_fail=[]
	specRangeDic={}
	empty_specRangeDic={}
	for spec in spec_priority:
		specRangeDic[spec]=[]
		empty_specRangeDic[spec]=[]
	#===============================================================
	# search the design space and filter the satisfying ones 
	#===============================================================
	#-- pex effect --
	Cc_pre=Cc
	Cf_pre=Cf
	if modelVersion=='Beta' or modelVersion=='Alpha_pex':
		Cc=mult_Con*Cc
		Cf=mult_Con*Cf
	max_spec_depth=0
	for Nd in Ndrv_list:
		for Nc in Ncc_list:
			for Nf in Nfc_list:
				for M in Nstg_list:
					itr_pass_flag=1  # pass_flag for one iteration
					fst_spec_flag=0 
					Fref=10e6 # reference clock freq fixed to 10MHz
					#===============================================================
					# calculate the model expected spec vals 
					#===============================================================
					Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal,Pwr_mdl,IB_PN_mdl,Area_mdl=spec_cal(Nd,Nc,Nf,M,Cc,Cf,CF,Iavg_const,PN_const,Fref,A_CC,A_FC,vdd, FC_half, ND)
					#===============================================================
					# generate dictionary list for specs
					# and filter the ones that satisfy input spec in the order in 
					# spec_priority
					#===============================================================
					print ("#=================================================================================")
					print ('INFO: model specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, pwr_mdl=%.2e, FCR=%.2f'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,Pwr_mdl,freqCoverRatio))
					print ('INFO: model design: ndrv=%d, ncrs=%d, nfine=%d, nstg=%d'%(Nd,Nc,Nf,M))
					if modelVersion=='Beta':
						specDic={"Fnom":Fnom_mdl,"Fmax":Fmax_mdl,"Fmin":Fmin_mdl,"Fres":Fres_mdl,"FCR":freqCoverRatio,"dco_PWR":Pwr_mdl,"IB_PN":IB_PN_mdl}
					elif modelVersion=='Alpha' or modelVersion=='Alpha_pex':
						specDic={"Fnom":Fnom_mdl,"Fmax":Fmax_mdl,"Fmin":Fmin_mdl,"Fres":Fres_mdl,"FCR":freqCoverRatio,"dco_PWR":Pwr_mdl}
					spec_depth=0
					for spec in spec_priority:
						#print("checking for spec:%s" %(spec))
						if spec=="Fnom":
							if Fnom_mdl < Fnom_max and Fnom_mdl > Fnom_min:
								#specRangeDic["Fnom"].append("passed")
								#specRangeDic["Fnom"].append(Fnom_mdl)
								fst_spec_flag=1
								fst_pass.append(Fnom_mdl)
								#print ('!!Fnom passed model specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, FCR=%.2e, IB_PN=%.2f, dco_PWR=%.2e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,freqCoverRatio,IB_PN_mdl,Pwr_mdl))
							else:
								itr_pass_flag=0
								fst_fail.append(Fnom_mdl)
								#print ('!!model specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, FCR=%.2e, IB_PN=%.2f, dco_PWR=%.2e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,freqCoverRatio,IB_PN_mdl,Pwr_mdl))
								#specRangeDic[spec].append(Fnom_mdl)
								#max_spec_depth, specRangeDic = depth_check(spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec)
						elif fst_spec_flag==1 and itr_pass_flag==1:   # record only the first failed spec's value to specRangeDic
							if spec_priority[spec]=="lo":
								if specDic[spec] < inSpecDic[spec]:
									#specRangeDic[spec].append("passed")
									#specRangeDic[spec].append(specDic[spec])
									pass
								else:
									itr_pass_flag=0 
									#specRangeDic[spec].append(specDic[spec])
									max_spec_depth, specRangeDic = depth_check(spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec,spec_priority)
							elif spec_priority[spec]=="hi": 
								if specDic[spec] > inSpecDic[spec]:
									#specRangeDic[spec].append("passed")
									#specRangeDic[spec].append(specDic[spec])
									pass
								else:
									itr_pass_flag=0 
									#specRangeDic[spec].append(specDic[spec])
									max_spec_depth, specRangeDic = depth_check(spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec,spec_priority)
						else:
							itr_pass_flag=0
						spec_depth=spec_depth+1
					if itr_pass_flag==1:  # all specs passed
						passed_designs.append([Nd,Nc,Nf,M])
						#passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,Pwr_mdl,Area_mdl])
						if modelVersion=='Beta':
							passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,freqCoverRatio,Pwr_mdl,Area_mdl,IB_PN_mdl])
							print ('INFO: passed model specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2f, pwr_mdl=%.2e, FCR=%.2e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,IB_PN_mdl,Pwr_mdl,freqCoverRatio))
						elif modelVersion=='Alpha' or  modelVersion=='Alpha_pex':
							passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,freqCoverRatio,Pwr_mdl,Area_mdl])
							print ("#=================================================================================")
							print ('INFO: passed model specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, pwr_mdl=%.2e, FCR=%.2e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,Pwr_mdl,freqCoverRatio))
							print ('INFO: passed model design: ndrv=%d, ncrs=%d, nfine=%d, nstg=%d'%(Nd,Nc,Nf,M))
						pass_flag=1
					#print('%e'%(Fnom_mdl))	
					#print(freqCoverRatio)
	#print('mult_Con=%e'%(mult_Con))
	if pass_flag==0:
		print("!!! design solution searching failed !!!")
		for spec in spec_priority:
			#if specRangeDic[spec]!=[] and spec!='Fnom': # not passed
			if specRangeDic[spec]!=[]: # not passed
				spec_min=min(specRangeDic[spec])	
				spec_max=max(specRangeDic[spec])	
				specRangeDic[spec]=[spec_min,spec_max]
		#sys.exit(1)
	if fst_pass==[]:
		print('!!! first spec failed !!!')
		print('first spec range: %e ~ %e' %(min(fst_fail),max(fst_fail)))
		sys.exit(1)


	return pass_flag, passed_designs, passed_specs, specRangeDic

# =======================================================================================
# update the max_spec_depth => empty the specRangeDic
# append/create specRangeDic for the certain spec 

def depth_check (spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec,spec_priority):
	if max_spec_depth <= spec_depth:
		if max_spec_depth < spec_depth: # new max depth
			max_spec_depth=spec_depth
			#specRangeDic=empty_specRangeDic
			for spec in spec_priority:
				specRangeDic[spec]=[]
		specRangeDic[spec].append(specDic[spec])
	#print('failed: max_spec_depth=%d'%(max_spec_depth))
	#print('specRangeDic=')
	#print(specRangeDic)
	return max_spec_depth, specRangeDic 			

def spec_cal_freq(Nd,Nc,Nf,M,Cc,Cf,CF):
	Np=Nd+Nc
	CB=(Np)*Cc+Nf*Cf
	Fnom_fcmax=(Nd+Nc/2)/(CB*M)
	Fnom_fcmin=(Nd+Nc/2)/((CB+Nf*CF)*M)
	dFf_mdl=Fnom_fcmax-Fnom_fcmin
	#dFc_mdl=1/CB/M/Nc    # is this right?
	dFc_mdl=((Nd+Nc/2+1/M)/((CB+Nf*CF)*M))-Fnom_fcmin    # is this right?
	freqCoverRatio=dFf_mdl/dFc_mdl
	Fres_mdl=(Fnom_fcmax-Fnom_fcmin)/Nf/M
	Fmin_mdl=1/(CB+Nf*CF)*(Nd)/M
	Fmax_mdl=1/(CB)*(Nd+Nc)/M
	Fnom_mdl=(Nd+Nc/2)/(CB*M)
	Ctotal=Cc*(Nd+Nc/2)+Cf*Nf+CF*Nf/2
	return Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal
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
		Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal=spec_cal_freq(N_drv,N_cc,N_fc,N_stg,Cc,Cf,CF)
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
		print ('*Model accuracy result(in percentage): Fnom_err_mean,max=%f,%f, Fmax=%f,%f, Fmin=%f,%f, Fres=%f,%f, Iavg=%f,%f'%(Fnom_err_mean,Fnom_err_max,Fmax_err_mean,Fmax_err_max,Fmin_err_mean,Fmin_err_max,Fres_err_mean,Fres_err_max,Iavg_err_mean,Iavg_err_max)) 

	#--- write the model.json ---
	r_model=open(formatDir+'form_model.json','r')
	nm1=txt_mds.netmap()
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

def math_model_gen(vm1,netlist_dir,format_dir,vdd,temp,platform,resultrf_dir,num_core,result_dir,index,show,num_meas):
	idK,Kg,freq,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=run_pre_sim.gen_result(result_dir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],num_meas,index,show,vdd,temp)
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
					CF1_temp,Cc1_temp,Cf1_temp=C_solve(Kg[i],Kg[j],idK[i],idK[j],cf1,cf2)
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


def pex_math_model_gen(vm1,netlist_dir,format_dir,vdd,temp,platform,num_core,result_dir,index,show,num_meas,fc_en_type):
	idK,Kg,freq,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=run_pex_sim.gen_result(result_dir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],num_meas,index,show,vdd,temp, fc_en_type)
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
					CF1_temp,Cc1_temp,Cf1_temp=C_solve(Kg[i],Kg[j],idK[i],idK[j],cf1,cf2)
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
	print ('CF_avg=%e'%(CF_avg))
	print ('Cc_avg=%e'%(Cc_avg))
	print ('Cf_avg=%e'%(Cf_avg))
	print ('CF_max_err=%f (in percentage)'%(CF_max_err))
	print ('Cc_max_err=%f (in percentage)'%(Cc_max_err))
	print ('Cf_max_err=%f (in percentage)'%(Cf_max_err))
	return CF_avg,Cc_avg,Cf_avg,CF_max_err,Cc_max_err,Cf_max_err	

#=====================================================================
# calculate math mdl specs according to design params 
#=====================================================================
def spec_cal(Nd,Nc,Nf,M,Cc,Cf,CF,Iavg_const,PN_const,Fref,A_CC,A_FC,vdd,FC_half, ND):
	Np=Nd+Nc
	CB=(Np+ND)*Cc+Nf*Cf
	Fnom_fcmax=(Nd+Nc/2)/(CB*M)
	Fnom_fcmin=(Nd+Nc/2)/((CB+Nf*CF)*M)
	dFf_mdl=Fnom_fcmax-Fnom_fcmin
	#dFc_mdl=1/CB/M/Nc    # is this right?
	dFc_mdl=((Nd+Nc/2+1/M)/((CB+Nf*CF)*M))-Fnom_fcmin    # is this right?
	freqCoverRatio=dFf_mdl/dFc_mdl
	Fres_mdl=(Fnom_fcmax-Fnom_fcmin)/Nf/M
	if FC_half==1:
		Fres_mdl=Fres_mdl/2
	Fmin_mdl=1/(CB+Nf*CF)*(Nd)/M
	Fmax_mdl=1/(CB)*(Nd+Nc)/M
	Fnom_mdl=(Nd+Nc/2)/(CB*M)
	Ctotal=Cc*(Nd+Nc/2)+Cf*Nf+CF*Nf/2
	Iavg=Ctotal*Iavg_const
	Pwr_mdl=Iavg*vdd[0]
	tdcn_mdl=((2*math.pi)**2)/12*(1/M/4)**2/Fref #--TDC quantization noise model
	dcon_mdl=(2*math.pi)**2*(Fres_mdl/1e6)/10e6  #-- DCO quantization noise model
	pn_mdl=(PN_const/math.sqrt((Nd+Nc/2)*1e6/(Fnom_mdl*Fnom_mdl)))**2 #-- PN model
	IB_PN_mdl=10*math.log10(tdcn_mdl+dcon_mdl+pn_mdl) #in dBc, adding quantization noises
	Area_mdl=(Nd+Nc)*M*A_CC+Nf*M*A_FC		
	return Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal,Pwr_mdl,IB_PN_mdl,Area_mdl

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
 
def C_solve(Kg1_list,Kg2_list,idK1,idK2,cf1,cf2):
	#--- extract nominal vdd, temp values ---
	Kg1=Kg1_list[0][0]   #3e9
	Kg2=Kg2_list[0][0]   #1.8e9
	CF=(idK1[0][0]+idK2[0][0])/2   
	#--- calculate error rate --- 
	const1=1/Kg1-1/Kg2    #neg
	#--- case 1 when Ndrv+Ncc is same ---
	if cf1[0]==cf2[0]:
		Cf=(const1-(cf1[2]-cf2[2])*CF)/(cf1[1]-cf2[1])    
		Cc1=(1/Kg1-cf1[1]*Cf-cf1[2]*CF)/cf1[0]
		Cc2=(1/Kg2-cf2[1]*Cf-cf2[2]*CF)/cf2[0]
		Cc_err=abs(Cc1-Cc2)/(Cc1+Cc2)*2*100
		#print ('max idK=%e'%(max(max(idK2),max(idK2))))
		#print ('max error idK=%e'%(maxE))
		#print ('min error idK=%e'%(minE))
		return CF,Cc1,Cf
	#--- case 2 when Nfc is same ---
	elif cf1[1]==cf2[1]:
		Cc=(const1-(cf1[2]-cf2[2])*CF)/(cf1[0]-cf2[0])     #(const1)/(-8)
		Cf1=(1/Kg1-cf1[0]*Cc-cf1[2]*CF)/cf1[1]
		Cf2=(1/Kg2-cf2[0]*Cc-cf2[2]*CF)/cf2[1]
		Cf_err=abs(Cf1-Cf2)/(Cf1+Cf2)*2*100
		#print ('max idK=%e'%(max(max(idK2),max(idK2))))
		#print ('max error idK=%e'%(maxE))
		#print ('min error idK=%e'%(minE))
		return CF,Cc,Cf1
