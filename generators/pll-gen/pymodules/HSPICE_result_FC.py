###### resmap test ############
import HSPICE_mds
import matplotlib.pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
#import xlsxwriter


#index=1       #exist:1 no:0
#num_meas=2     #measurements
#skip_line=2   #default titles


def gen_resultfc(ncell,ndrv,nfc,stg_start,stg_swp,Ncf,fcidx,num_meas,index,show,A_CC,A_FC):
	skip_line=2   #default titles
	
	num_var=nfc+ncell+1
	num_words=num_var+num_meas+1   #+1 is +alter# index not included

	workbook = xlsxwriter.Workbook('./pymodules/XL_result/%dDCO%d_result%d.xlsx'%(ncell,ndrv,nfc))
	worksheet = workbook.add_worksheet()


	il=0
	iw=1
	k=0
	rm=HSPICE_mds.resmap(stg_swp,num_words,index)
	set_tb=0
	for j in range(stg_swp):
		#if index:
		#	rm.get_var(j,'index')
		#	print('got index')
		if nfc==128 and ndrv==32 and ncell==8:
			res_path='./HSPICE/DUMP_result_FC/tb_%dring%d_osc%d_FC_dp/'%(ndrv,ncell,stg_start+j)
		else:
			res_path='./HSPICE/DUMP_result_FC/tb_%dring%d_osc%d_FC%d_dp/'%(ndrv,ncell,stg_start+j,nfc)
		#res_path='./HSPICE/DUMP_result_FC/tb_%dring8_osc%d_FC_dp/'%(ndrv,stg_start+j)
		#res_path='./HSPICE/old_DUMP_result_FC/tb_%dring8_osc%d_FC_dp/'%(ndrv,stg_start+j)  ###here!!!!
		for i in os.listdir(res_path):
			if i[0:6]=='worker' and i[0:7]!='worker.':
				if nfc==128 and ndrv==32 and ncell==8:
					r_result=open(res_path+i+'/tb_%dring8_osc%d_FC.mt0'%(ndrv,j+stg_start))
				else:
					r_result=open(res_path+i+'/tb_%dring8_osc%d_FC%d.mt0'%(ndrv,j+stg_start,nfc))
				for line in r_result.readlines():
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								if iw<num_words+index+1:
									rm.get_var(j,word)
								#	print("got %s"%(word))
								else:
									rm.add(j,word)
								iw+=1
					elif il>skip_line+round(float(num_words)/3+float(1)/3)-1:    #change here!!!
						words=line.split()
						for word in words:
							rm.add(j,word)
							iw+=1
					il+=1
				set_tb=1
				il=0
				iw=1
				k+=1
		set_tb=0
		k=0
		
		
	#print rm.vr
	#print rm.vl[]
	#print rm.vl[1]
		
	fc=0
	cc=0
	freq_per=0
	freq=0
	kacc=0
	kavg=0
	kidx=0
	
	cc_d=0
	fc_d=0
	Kc_d=0
	Kc=0    ##const
	rm2=HSPICE_mds.resmap(stg_swp,5,0)   #result map for cleaner data

	row=0
	col=0
	worksheet.write(0,0,'#Stages')
	worksheet.write(0,1,'Ndrv')
	worksheet.write(0,2,'Nc-total')
	worksheet.write(0,3,'Nf-total')
	worksheet.write(0,4,'Fmax')
	worksheet.write(0,5,'Fmin')
	worksheet.write(0,6,'Fres')
	worksheet.write(0,7,'Area')
	row=row+1
	
	#print ('len(rm.vr)=%d'%(len(rm.vr)))
	#print ('len(rm.vl[0][0])=%d'%(len(rm.vl[0][0])))
	for ntb in range(stg_swp):    # for all netlist
		rm2.get_var(ntb,'FC')
		rm2.get_var(ntb,'CC')
		rm2.get_var(ntb,'freq_per')
		rm2.get_var(ntb,'freq')
		rm2.get_var(ntb,'TW')
		#print ("ntb=%d"%(ntb))
		for j in range(len(rm.vl[ntb][0])):       # for all command word (testbenchs)
			for i in range(len(rm.vr)):       # for all variables
				if rm.vr[i][0:2]=='vf':   ###here!!!!
					fc=fc+float(rm.vl[ntb][i][j])
				if rm.vr[i][0:2]=='vc':   ###here!!!!
					cc=cc+float(rm.vl[ntb][i][j])
				if rm.vr[i][0:3]=='per':
					freq_per=25/float(rm.vl[ntb][i][j])	
				if rm.vr[i][0:3]=='fre':
					freq=float(rm.vl[ntb][i][j])
			rm2.add(ntb,fc)			
			rm2.add(ntb,cc)			
			rm2.add(ntb,freq_per)			
			rm2.add(ntb,freq)
			rm2.add(ntb,fc+Ncf*cc)
			if (fc==nfc and cc==0) or (fc==0 and cc==8):
				if (fc==nfc and cc==0): 
					worksheet.write(row,5,float(freq_per))   #Fmin
				if (fc==0 and cc==8): 
					worksheet.write(row,4,float(freq_per))   #Fmax
				worksheet.write(row,0,stg_start+ntb)
				worksheet.write(row,1,ndrv)
				worksheet.write(row,2,ncell)
				worksheet.write(row,3,nfc)
				worksheet.write(row,7,A_CC*(ncell+ndrv)*(stg_start+ntb)+A_FC*nfc*(stg_start+ntb))
			fc=0
			cc=0
		row+=1
				
		
	row=1	
	#print rm2.vr
	#print rm2.vl
	rm2.sort('TW')
	#print rm2.svar[0]
	dKavg=[0]*stg_swp
	idKavg=[0]*stg_swp
	dKavgcc=0
	dFavgcc=0
	dFavg=0
	dF=0
	freq_d=0
	Mstg=[0]*stg_swp
	dKcc=[0]*stg_swp
	icc=0
	idk=0
	tws=sorted(rm2.svar[0])
	mdl_map=HSPICE_mds.resmap(stg_swp,6,0)   #result map for model 
	for ntb in range(stg_swp):
		mdl_map.get_var(ntb,'NSTG')
		mdl_map.get_var(ntb,'TW')
		mdl_map.get_var(ntb,'Kf')
		mdl_map.get_var(ntb,'dK')
		mdl_map.get_var(ntb,'dFf/dFc')
		mdl_map.get_var(ntb,'idK')
		dKcc[ntb]={}
		for i in range(len(tws)):       # for all command word
			fc=rm2.svar[ntb][tws[i]][0]   #fc
			cc=rm2.svar[ntb][tws[i]][1]   #cc
			freq=rm2.svar[ntb][tws[i]][2]   #freq
			##for fc mdl##
			Kf=(freq*(stg_start+ntb)/(ndrv+cc))
			if cc==cc_d and fc_d-fc!=0 and Kf_d!=0:
				dK=(Kf-Kf_d)/(fc-fc_d)
				dF=(freq-freq_d)/(fc-fc_d)
				print('dF='),
				print dF
				idK=(1/Kf-1/Kf_d)/(fc_d-fc)
				dKavgcc=dKavgcc+dK
				dFavgcc=dFavgcc+dF
				#print('dKavgcc=%e, dK=%e'%(dKavgcc,dK))
				dKcc[ntb][cc]=[]   #dictionary flag
				icc+=1			
			else:    ## cc transition
				dK=0
				idK=0
				if icc!=0:
					dKavgcc=dKavgcc/(icc)
					dFavg=dFavgcc/(icc)
					print('dFavg='),
					print dFavg
					if cc_d==0:
						worksheet.write(row,6,dF)
					dKcc[ntb][cc_d].append(dKavgcc)
					dKavgcc=0
					dFavgcc=0
					#print('icc=%d, cc=%d'%(icc,cc_d))
				icc=0
			mdl_map.add(ntb,stg_start+ntb)
			mdl_map.add(ntb,fc+Ncf*cc)
			mdl_map.add(ntb,Kf)
			mdl_map.add(ntb,dK)
			mdl_map.add(ntb,dK*nfc*(ndrv+cc)/Kf)
			mdl_map.add(ntb,idK)
			Kf_d=Kf
			freq_d=freq
			fc_d=fc
			cc_d=cc
			dKavg[ntb]=dKavg[ntb]+dK
			idKavg[ntb]=idKavg[ntb]+idK
			if dK!=0:
				idk+=1
			#print('dKavg=%e, ntb=%d, idk=%d'%(dKavg[ntb],ntb,idk))
		dKcc[ntb][cc_d].append(dKavgcc/(icc))
		#print('last icc=%d, cc=%d'%(icc,cc_d))
		icc=0
		Kf_d=0
		fc_d=0
		cc_d=0
		dKavgcc=0
		dFavgcc=0
		dKavg[ntb]=dKavg[ntb]/(idk)
		idKavg[ntb]=idKavg[ntb]/(idk)
		idk=0
		Mstg[ntb]=stg_start+ntb
		row+=1
		
	
	#print('idK='),
	#print mdl_map.vr[5]
	#print mdl_map.vl[0][5]	

	#------------------------------------------------------------------------------
	# Check idK maximum error 
	#------------------------------------------------------------------------------
	Err_idK=[[]]*stg_swp
	Err_idK_max=[[]]*stg_swp
	Err_idK_min=[[]]*stg_swp
	for ntb in range(stg_swp):
		varidx=mdl_map.vr.index('idK')
		for i in range(1,len(mdl_map.vl[ntb][varidx])):
			if mdl_map.vl[ntb][varidx][i]==0:
				pass
			else:	
				Err_idK[ntb].append((mdl_map.vl[ntb][varidx][i]-idKavg[ntb])/idKavg[ntb]*100)
		Err_idK_max[ntb]=max(Err_idK[ntb])
		Err_idK_min[ntb]=min(Err_idK[ntb])
	#	Err_idK[ntb]=max(abs(max(mdl_map.vl[ntb][varidx])-idKavg[ntb])/idKavg[ntb],abs(min(mdl_map.vl[ntb][varidx])-idKavg[ntb])/idKavg[ntb])*100
	#print('Err_idK_max=')
	#print Err_idK_max
	#print('Err_idK_min=')
	#print Err_idK_min

	
	#========== fine tuning model ===============
	#x=np.array(Mstg)
	#y=np.array(dKavg)
	#z=np.polyfit(x,y,18)
	#dK_mdl=[0]*stg_swp
	#dK_err=[0]*stg_swp
	#for i in range(stg_swp):
	#	dK_mdl[i]=np.polyval(z,x[i])
	#	dK_err[i]=100*(dK_mdl[i]-dKavg[i])/dKavg[i]    # % scale
	#Ycc=[0]*len(dKcc)
	#Ycc0=[0]*len(dKcc)
	#Ycc4=[0]*len(dKcc)
	#Xcc=[0]*len(dKcc)
	#for i in range(len(dKcc)):
	#	Ycc[i]=dKcc[i][8][0]
	#	Ycc0[i]=dKcc[i][0][0]
	#	Ycc4[i]=dKcc[i][4][0]
	#	Xcc[i]=stg_start+i
	##for i in range(len(dKcc)):
	##	Ycc[i]=dKcc[i][8][0]
	##	Ycc0[i]=dKcc[i][0][0]
	##	Xcc[i]=stg_start+i
	#
	#plt.plot(Xcc,Ycc,'r',label='dK CC==8')
	#plt.plot(Xcc,Ycc0,'g',label='dK CC==0')
	#plt.plot(Xcc,Ycc4,'k',label='dK CC==4')  ###here!!
	#plt.plot(Xcc,dKavg,'b',label='dKavg')
	#plt.xlabel('#stages')
	#plt.ylabel('delta K')
	#legend=plt.legend(loc='upper right',fontsize='medium')
	#
	##print ('dK max error:%f%%'%(max(dK_err)))
	#if show==1:
	#	plt.show()
	return dKavg,idKavg
	



