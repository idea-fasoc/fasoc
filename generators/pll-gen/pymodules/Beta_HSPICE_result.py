###### resmap test ############
import HSPICE_mds
import matplotlib.pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

#================================================================================================
# gen_result_v2,v3 is the updated version that deals with VDD, TEMP parameters,
# v2: 8 TWs, v3: 7TWs with nominal Freq 
# receives all design parameters as array,
# tbrf is generated for only nominal vdd, temp for now
# returns input/output pair for machine learning
# all design params should have the same length
#================================================================================================
def gen_result_v3(result_dir,design_name,ncell,ndrv,nfc,nstg,num_meas,index,show,VDD,TEMP):

	#======================================================================================
	#  set initial variables
	#======================================================================================
	skip_line=2   #default titles
	il=0
	iw=1
	k=0
	#--- result map definition ---
	rm=[None]*len(ncell)
	#--- design map definition ---
	dm=[None]*len(ncell)

	set_tb=0
	result_exist=[]
	result_failed=[]
	for j in range(len(ncell)-1):
		i=j+1 #because ncell[0]=='ncell'
		num_var=nfc[i]*nstg[i]+ncell[i]*nstg[i]+1
		num_words=num_var+num_meas+3 #temper
	
		rm[j]=HSPICE_mds.resmap(1,num_words,index) #only one resmap per design	
		dm[j]=[None]*4 #4 design params
		dm[j][0]=ndrv[i]
		dm[j][1]=ncell[i]
		dm[j][2]=nstg[i]
		dm[j][3]=nfc[i]
		fail_flag=0
		res_path=result_dir+'tb'+design_name+'/'    #removed the exception for FC==128
		#--- save the [j] of the ones that success try and use for later ---
		try:
			for worker in os.listdir(res_path):
				if worker[0:6]=='worker' and worker[0:7]!='worker.':
					r_result=open(res_path+worker+design_name+'.mt0')
					for line in r_result.readlines():
						if set_tb==0:
							if il>skip_line-1:
								words=line.split()
								for word in words:
									if word=='failed':
										fail_flag=1
									if iw<num_words+index+1:
										rm[j].get_var(0,word)  #because only one result map per design
									else:
										rm[j].add(0,word)
									iw+=1
						elif il>skip_line+round(float(num_words)/3+float(1)/3)-1:    #change here!!!  ????
							words=line.split()
							for word in words:
								if word=='failed':
									fail_flag=1
								rm[j].add(0,word)
								iw+=1
						il+=1
					set_tb=1
					il=0
					iw=1
					k+=1
			set_tb=0
			k=0
			if fail_flag==0:
				result_exist.append(j)
			else:
				result_failed.append(j)
		except:
#			print('couldnt find:  '+res_path+'worker'+'/tb_%dring%d_osc%d_FC%d.mt0'%(ndrv[i],ncell[i],nstg[i],nfc[i]))
			pass

	#print('???? is : %d'%(round(num_words/3+1/3)))	
	#print('num word is : %d'%(num_words))	
	#print (rm[0].vr)
	print (rm[0].vl[0][len(rm[0].vl[0])-4])
	#print (rm[1].vl[0][len(rm[1].vl[0])-4])
	#print (rm[2].vl[0][len(rm[2].vl[0])-4])
	print ("result_exist:")
	print (result_exist)	
	print ("result_failed:"),
	print (result_failed)	
	fc=0
	cc=0
	freq_per=0
	freq=0
	ktemp=0
	kacc=0
	kavg=0
	Kg=0   #general const
	Kgacc=0   #general const
	kidx=0
	freq_cc=[None]*len(ncell)
	vdd=0
	temp=0
	iavg=0
	
	#print ('len(rm.vr)=%d'%(len(rm.vr)))
	#print ('len(rm.vl[0][0])=%d'%(len(rm.vl[0][0])))
	#========================================
	# cut out the last result   
	#========================================
	#result_exist=result_exist[0:len(result_exist)-1]
	result_exist=result_exist[0:len(result_exist)]
	#========================================
	# checking failed results vdd,temp   
	#========================================
	for fn in result_failed:
		#========================================
		# store all vales in temp_var   
		# this procedure is to merge all fc, cc   
		#========================================
		for j in range(len(rm[fn].vl[0][0])):       # for all command word
			for i in range(len(rm[fn].vr)):       # for all variables
				if rm[fn].vr[i][0:3]=='vvd':
					vdd=float(rm[fn].vl[0][i][j])
				if rm[fn].vr[i][0:3]=='tem':
					temp=float(rm[fn].vl[0][i][j])

	
	#========================================
	# spec definition 
	#========================================
	#Fmax=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	Fmax=[[[] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	Fmin=[[[] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	Fnom=[[[] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFfdFc=[[[] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFf_nom=[[[] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	Iavg=[[[] for y in range(len(VDD))] for z in range(len(ncell)-1)]

	Kg=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	idK=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]

	#for nd in range(len(ncell)-1):
	#for nd in range(1):
	for nd in result_exist:
		#print ("nd=%d"%(nd))
		#========================================
		# cc scaler for TW 
		#========================================
		#N_ctrl_fc=nfc[nd+1]*nstg[nd+1]	#total number of fine cells	
		N_ctrl_fc=dm[nd][3]*dm[nd][2]	#total number of fine cells	
		#N_ctrl_cc=ncell[nd+1]*nstg[nd+1]	#total number of coarse cells
		N_ctrl_cc=dm[nd][1]*dm[nd][2]	#total number of coarse cells
		N_drv=dm[nd][0]
		N_stg=dm[nd][2]
		cc_fc_scale=round(np.log10(N_ctrl_fc))+2	# scale factor for TW=CC*10**scale+FC
		cc_fc_scale=10**cc_fc_scale
		#========================================
		# set temporary variables  
		#========================================
		FC=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		CC=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		TW=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		FREQ=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		IAVG=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		K_ind=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]   # constant for individual points
		K_ind_pex=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]   # constant for individual points
		#========================================
		# store all vales in temp_var   
		# this procedure is to merge all fc, cc   
		#========================================
		for j in range(len(rm[nd].vl[0][0])):       # for all command word
			for i in range(len(rm[nd].vr)):       # for all variables
				if rm[nd].vr[i][0:2]=='vf':    ##here!!!!! 0:3 vvf  <---> 0:2 vf
					fc=fc+float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:2]=='vc':
					cc=cc+float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='per':
					freq_per=25/float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='fre':
					freq=float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='vvd':
					vdd=float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='tem':
					temp=float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='iav':
					iavg=float(rm[nd].vl[0][i][j])
			#========================================
			# store specs in [vdd][temp] form 
			# spec[0][0] is for nominal vdd, temp   
			#========================================
			vddIdx=VDD.index(vdd)
			tempIdx=TEMP.index(temp)
			nom_tIdx=TEMP.index(TEMP[0])
			max_tIdx=TEMP.index(max(TEMP))
			min_tIdx=TEMP.index(min(TEMP))
			nomVDD=VDD[0]
			nomTEMP=TEMP[0]
			FC[vddIdx][tempIdx].append(fc)
			CC[vddIdx][tempIdx].append(cc)
			TW[vddIdx][tempIdx].append(cc*cc_fc_scale+fc)
			FREQ[vddIdx][tempIdx].append(freq_per)
			IAVG[vddIdx][tempIdx].append(iavg)
			K_ind[vddIdx][tempIdx].append(freq_per*float(N_stg)/(N_drv+cc/float(N_stg)))  #point individual constants 
			K_ind_pex[vddIdx][tempIdx].append(freq_per*float(N_stg))  #point individual constants: assuming Con dominates 
			fc=0
			cc=0
		#print("unsorted TW=")
		#print(TW)
		#print("unsorted FREQ=")
		#print(FREQ)
		#========================================
		# store design, spec per vdd, temp  
		# only works for 7 sets of TW  
		#========================================
		num_FCW=len(FC[0][0])
		for ivdd in range(len(VDD)):
			for itemp in range(len(TEMP)):
				#TW_temp=list(TW[ivdd][itemp])  #save temp for nominal values
				#========================================
				# sort via tuning word
				#========================================
				HSPICE_mds.sort_via_1d_mult(TW[ivdd][itemp],FREQ[ivdd][itemp],IAVG[ivdd][itemp],K_ind[ivdd][itemp],K_ind_pex[ivdd][itemp])
			#print("sorted TW=")
			#print(TW)
			#print("sorted FREQ=")
			#print(FREQ)
			#--- Fnom ---
			Fnom_tmp=FREQ[ivdd][0][num_FCW-3]
			SFnom_tmp1=FREQ[ivdd][max_tIdx][num_FCW-3]
			SFnom_tmp2=FREQ[ivdd][min_tIdx][num_FCW-3]
			Fnom[nd][ivdd]=[Fnom_tmp,SFnom_tmp1,SFnom_tmp2]
			#--- Fmax ---
			Fmax_tmp=FREQ[ivdd][0][num_FCW-1]
			SFmax_tmp1=FREQ[ivdd][max_tIdx][num_FCW-1]
			SFmax_tmp2=FREQ[ivdd][min_tIdx][num_FCW-1]
			Fmax[nd][ivdd]=[Fmax_tmp,SFmax_tmp1,SFmax_tmp2]
			#--- Fmin ---
			Fmin_tmp=FREQ[ivdd][0][0]
			SFmin_tmp1=FREQ[ivdd][max_tIdx][0]
			SFmin_tmp2=FREQ[ivdd][min_tIdx][0]
			Fmin[nd][ivdd]=[Fmin_tmp,SFmin_tmp1,SFmin_tmp2]
			#--- dFf1/dFc1 ---
				#--- dFf1 ---
			dFf1_tmp=FREQ[ivdd][0][1]-FREQ[ivdd][0][0]
			SdFf1_tmp1=FREQ[ivdd][max_tIdx][1]-FREQ[ivdd][max_tIdx][0]
			SdFf1_tmp2=FREQ[ivdd][min_tIdx][1]-FREQ[ivdd][min_tIdx][0]
				#--- dFc1 ---
			dFc1_tmp=FREQ[ivdd][0][2]-FREQ[ivdd][0][0]
			SdFc1_tmp1=FREQ[ivdd][max_tIdx][2]-FREQ[ivdd][max_tIdx][0]
			SdFc1_tmp2=FREQ[ivdd][min_tIdx][2]-FREQ[ivdd][min_tIdx][0]
			dFfdFc[nd][ivdd]=[dFf1_tmp/dFc1_tmp,SdFf1_tmp1/SdFc1_tmp1,SdFf1_tmp2/SdFc1_tmp2]
			#--- dFf_nom ---
			dFf_nom_tmp=(FREQ[ivdd][0][5]-FREQ[ivdd][0][3])/N_ctrl_fc
			SdFf_nom_tmp1=FREQ[ivdd][max_tIdx][5]-FREQ[ivdd][max_tIdx][3]
			SdFf_nom_tmp2=FREQ[ivdd][min_tIdx][5]-FREQ[ivdd][min_tIdx][3]
			dFf_nom[nd][ivdd]=[dFf_nom_tmp,SdFf_nom_tmp1,SdFf_nom_tmp2]
			#--- Pavg for nominal freq ---	
			Iavg_tmp=IAVG[ivdd][0][num_FCW-3]
			SIavg_tmp1=IAVG[ivdd][max_tIdx][num_FCW-3]
			SIavg_tmp2=IAVG[ivdd][min_tIdx][num_FCW-3]
			Iavg[nd][ivdd]=[Iavg_tmp,SIavg_tmp1,SIavg_tmp2]
			for itemp in range(len(TEMP)):
				#--- Kg for math model ---
				Kg[nd][ivdd][itemp]=K_ind[ivdd][itemp][4]  #Kg on nominal
				idK_temp=1/K_ind[ivdd][itemp][3]-1/K_ind[ivdd][itemp][5]
				idK[nd][ivdd][itemp]=idK_temp*float(N_stg)/float(N_ctrl_fc)
				#--- for test purpose ---
				idK_C0=1/K_ind[ivdd][itemp][0]-1/K_ind[ivdd][itemp][1]
				#print("idK comparison:")
				#print idK_C0*float(N_stg)/float(N_ctrl_fc)	
				#print idK_temp*float(N_stg)/float(N_ctrl_fc)
		#print ("NDRV,NCC, NSTG,NFC cc_fc_scale= %d, %d, %d, %d, %e"%(ndrv[nd+1],ncell[nd+1],nstg[nd+1],nfc[nd+1],cc_fc_scale))
		#print ("Fnom="),
		#print (Fnom[nd])
		#print ("Fmax="),
		#print (Fmax[nd])
		#print ("Fmin="),
		#print (Fmin[nd])
		#print ("TW="),
		#print (TW)	
		#print ("K_ind="),
		#print (K_ind)
		#print ("K_ind_pex="),
		#print (K_ind_pex)
		#print ("dFfdFc="),
		#print (dFfdFc[nd]),
		#print ("dFf_nom="),
		#print (dFf_nom[nd]),
		#print ("Kg="),
		#print (Kg)
		#print ("idK="),
		#print (idK)
		 



	return idK,Kg,Fnom,Fmax,Fmin,dFf_nom,dFfdFc,Iavg,result_exist,dm


def gen_result_v2(result_dir,ncell,ndrv,nfc,nstg,num_meas,index,show,VDD,TEMP):

	#======================================================================================
	#  set initial variables
	#======================================================================================
	skip_line=2   #default titles
	#N_ctrl_fc=nfc*nstg	#total number of fine cells	
	#N_ctrl_cc=ncell*nstg	#total number of coarse cells
	#cc_fc_scale=round(np.log10(N_ctrl_cc))-round(np.log10(N_ctrl_fc))+2	# scale factor for TW=CC*10**scale+FC
	#cc_fc_scale=10**cc_fc_scale
	il=0
	iw=1
	k=0
	#--- result map definition ---
	rm=[None]*len(ncell)
	#--- design map definition ---
	dm=[None]*len(ncell)

	set_tb=0

	for j in range(len(ncell)-1):
		i=j+1 #because ncell[0]=='ncell'
		num_var=nfc[i]*nstg[i]+ncell[i]*nstg[i]+1
		num_words=num_var+num_meas+3 #temper
	
		rm[j]=HSPICE_mds.resmap(1,num_words,index) #only one resmap per design	
		dm[j]=[None]*4 #4 design params
		dm[j][0]=ncell[i]
		dm[j][1]=ndrv[i]
		dm[j][2]=nfc[i]
		dm[j][3]=nstg[i]

		res_path=result_dir+'tb_%dring%d_osc%d_FC%d_dp/'%(ndrv[i],ncell[i],nstg[i],nfc[i])    #removed the exception for FC==128
		for worker in os.listdir(res_path):
			if worker[0:6]=='worker' and worker[0:7]!='worker.':
				r_result=open(res_path+worker+'/tb_%dring%d_osc%d_FC%d.mt0'%(ndrv[i],ncell[i],nstg[i],nfc[i]))
				for line in r_result.readlines():
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								if iw<num_words+index+1:
									rm[j].get_var(0,word)  #because only one result map per design
								else:
									rm[j].add(0,word)
								iw+=1
					elif il>skip_line+round(float(num_words)/3+float(1)/3)-1:    #change here!!!  ????
						words=line.split()
						for word in words:
							rm[j].add(0,word)
							iw+=1
					il+=1
				set_tb=1
				il=0
				iw=1
				k+=1
		set_tb=0
		k=0

	#print('???? is : %d'%(round(num_words/3+1/3)))	
	#print('num word is : %d'%(num_words))	
	#print rm[0].vr
	#print rm[0].vl[0][0]
	#print rm[0].vl[0][1]
	#print rm[0].vl[0][2]
		
	fc=0
	cc=0
	freq_per=0
	freq=0
	ktemp=0
	kacc=0
	kavg=0
	Kg=0   #general const
	Kgacc=0   #general const
	kidx=0
	freq_cc=[None]*len(ncell)
	vdd=0
	temp=0
	iavg=0
	
	#print ('len(rm.vr)=%d'%(len(rm.vr)))
	#print ('len(rm.vl[0][0])=%d'%(len(rm.vl[0][0])))
	rm2=HSPICE_mds.resmap(len(ncell),13,0)   #result map for cleaner data
	
	Fmax=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	Fmin=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFf1=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFf2=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFf3=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFf4=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFc1=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	dFc2=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]
	Iavg=[[[[] for x in range(len(TEMP))] for y in range(len(VDD))] for z in range(len(ncell)-1)]

	for nd in range(len(ncell)-1):
		#========================================
		# cc scaler for TW 
		#========================================
		N_ctrl_fc=nfc[nd+1]*nstg[nd+1]	#total number of fine cells	
		N_ctrl_cc=ncell[nd+1]*nstg[nd+1]	#total number of coarse cells
		cc_fc_scale=round(np.log10(N_ctrl_fc))+2	# scale factor for TW=CC*10**scale+FC
		cc_fc_scale=10**cc_fc_scale
		#========================================
		# set rm2 variables 
		#========================================
		#--- design variables ---
		rm2.get_var(nd,'NCC') 
		rm2.get_var(nd,'Ndrv') 
		rm2.get_var(nd,'NFC') 
		rm2.get_var(nd,'Nstg') 
		rm2.get_var(nd,'VDD') 
		#--- spec variables ---
		rm2.get_var(nd,'Fmax') 
		rm2.get_var(nd,'Fmin') 
		rm2.get_var(nd,'dFf/dFc') 
		rm2.get_var(nd,'PWR') 
		rm2.get_var(nd,'Stemp_Fmax')	#Temperature Sensitivity 
		rm2.get_var(nd,'Stemp_Fmin') 
		rm2.get_var(nd,'Stemp_dFf/dFc') 
		rm2.get_var(nd,'Stemp_PWR') 
		#========================================
		# set temporary variables  
		#========================================
		FC=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		CC=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		TW=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		FREQ=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		IAVG=[[[] for x in range(len(TEMP))] for y in range(len(VDD))]
		#========================================
		# store all vales in tem_var   
		# this procedure is to merge all fc, cc   
		#========================================
		for j in range(len(rm[nd].vl[0][0])):       # for all command word
			for i in range(len(rm[nd].vr)):       # for all variables
				if rm[nd].vr[i][0:2]=='vf':    ##here!!!!! 0:3 vvf  <---> 0:2 vf
					fc=fc+float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:2]=='vc':
					cc=cc+float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='per':
					freq_per=25/float(rm[nd].vl[0][i][j])	
				if rm[nd].vr[i][0:3]=='fre':
					freq=float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='vvd':
					vdd=float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='tem':
					temp=float(rm[nd].vl[0][i][j])
				if rm[nd].vr[i][0:3]=='iav':
					iavg=float(rm[nd].vl[0][i][j])
			#========================================
			# store specs in [vdd][temp] form 
			# spec[0][0] is for nominal vdd, temp   
			#========================================
			vddIdx=VDD.index(vdd)
			tempIdx=TEMP.index(temp)
			max_tIdx=TEMP.index(max(TEMP))
			min_tIdx=TEMP.index(min(TEMP))
			nomVDD=VDD[0]
			nomTEMP=TEMP[0]
			FC[vddIdx][tempIdx].append(fc)
			CC[vddIdx][tempIdx].append(cc)
			TW[vddIdx][tempIdx].append(cc*cc_fc_scale+fc)
			FREQ[vddIdx][tempIdx].append(freq_per)
			IAVG[vddIdx][tempIdx].append(iavg)
			fc=0
			cc=0
		#========================================
		# store design, spec per vdd, temp  
		# only works for 8 sets of TW  
		#========================================
		num_FCW=len(FC[0][0])
		for ivdd in range(len(VDD)):
			for itemp in range(len(TEMP)):
				#TW_temp=list(TW[ivdd][itemp])  #save temp for nominal values
				HSPICE_mds.sort_via_1d_mult(TW[ivdd][itemp],FREQ[ivdd][itemp],IAVG[ivdd][itemp])
				#--- Fmax ---
				Fmax_tmp=FREQ[ivdd][0][num_FCW-1]
				SFmax_tmp1=FREQ[ivdd][max_tIdx][num_FCW-1]/Fmax_tmp
				SFmax_tmp2=FREQ[ivdd][min_tIdx][num_FCW-1]/Fmax_tmp
				Fmax[nd][ivdd]=[Fmax_tmp,SFmax_tmp1,SFmax_tmp2]
				#--- Fmin ---
				Fmin_tmp=FREQ[ivdd][0][0]
				SFmin_tmp1=FREQ[ivdd][max_tIdx][0]/Fmin_tmp
				SFmin_tmp2=FREQ[ivdd][min_tIdx][0]/Fmin_tmp
				Fmin[nd][ivdd]=[Fmin_tmp,SFmin_tmp1,SFmin_tmp2]
				#--- dFf1 ---
				dFf1_tmp=FREQ[ivdd][0][1]-FREQ[ivdd][0][0]
				dFf2_tmp=FREQ[ivdd][0][3]-FREQ[ivdd][0][2]
				dFf3_tmp=FREQ[ivdd][0][5]-FREQ[ivdd][0][4]   ### change here!!! 
				dFf4_tmp=FREQ[ivdd][0][7]-FREQ[ivdd][0][6]   ### change here!!! 
				dFf1[nd][ivdd]=[dFf1_tmp]
				dFf2[nd][ivdd]=[dFf2_tmp]
				dFf3[nd][ivdd]=[dFf3_tmp]
				dFf4[nd][ivdd]=[dFf4_tmp]
				#--- dFc ---
				dFc1_tmp=FREQ[ivdd][0][2]-FREQ[ivdd][0][0]
				dFc2_tmp=FREQ[ivdd][0][6]-FREQ[ivdd][0][4]
				dFc1[nd][ivdd]=[dFc1_tmp]
				dFc2[nd][ivdd]=[dFc2_tmp]
				#--- Pavg ---	
				Iavg_tmp=FREQ[ivdd][0][2]-FREQ[ivdd][0][0]
				Iavg[nd][ivdd]=[Iavg_tmp]
		#print ("NCC, NDRV, NFC, NSTG, cc_fc_scale= %d, %d, %d, %d, %e"%(ncell[nd+1]*nstg[nd+1],ndrv[nd+1],nfc[nd+1]*nstg[nd+1],nstg[nd+1],cc_fc_scale))
		#print ("Fmax/Fmin="),
		#print (Fmax[nd][0][0]/Fmin[nd][0][0])
		#print ("TW="),
		#print (TW)	
		#print ("dFf=")
		#print (dFf1[nd])
		#print (dFf2[nd])
		#print (dFf3[nd])
		#print (dFf4[nd])
		#print ("dFc=")
		#print (dFc1[nd])
		#print (dFc2[nd])



def gen_result(ncell,ndrv,nfc,stg_start,stg_swp,Ncf,fcidx,num_meas,index,show):
	skip_line=2   #default titles
	
	num_var=nfc+ncell+1
	num_words=num_var+num_meas+1   #+1 is +alter# index not included
	
	
	il=0
	iw=1
	k=0
	rm=HSPICE_mds.resmap(stg_swp,num_words,index)
	
	res_dir=[]
	
	set_tb=0
	for j in range(stg_swp):
		#res_path='./HSPICE/DUMP_result/tb_%dring8_osc%d_dp/'%(ndrv,stg_start+j)    ### here!!!
		if nfc==128 and ndrv==32 and ncell==8:
			res_path='./HSPICE/DUMP_result_FC/tb_%dring8_osc%d_FC_dp/'%(ndrv,stg_start+j)
		else:
			res_path='./HSPICE/DUMP_result/tb_%dring8_osc%d_FC%d_dp/'%(ndrv,stg_start+j,nfc)
		res_dir=[]
		for i in os.listdir(res_path):
			if i[0:6]=='worker' and i[0:7]!='worker.':
				if nfc==128 and ndrv==32 and ncell==8:
					#r_result=open(res_path+i+'/tb_%dring8_osc%d.mt0'%(ndrv,j+stg_start))  ###here!!!
					r_result=open(res_path+i+'/tb_%dring8_osc%d_FC.mt0'%(ndrv,j+stg_start))
				else:
					r_result=open(res_path+i+'/tb_%dring8_osc%d_FC%d.mt0'%(ndrv,j+stg_start,nfc))
				for line in r_result.readlines():
					#---- only read variable names of the first testbench per each netlist ----
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								#---- read variable names ----
								if iw<num_words+index+1:  
									rm.get_var(j,word)
								#---- read value names ----
								else:
									rm.add(j,word)
								iw+=1
					#---- from second mt0, read only values ----
					elif il>skip_line+round(float(num_words)/3+float(1)/3)-1:    #change here!!!  ????
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
		
	#print('???? is : %d'%(round(num_words/3+1/3)))	
	#print('num word is : %d'%(num_words))	
	#print rm.vr
	#print rm.vl[0]
		
	fc=0
	cc=0
	freq_per=0
	freq=0
	kacc=0
	kavg=0
	Kg=0   #general const
	Kgacc=0   #general const
	kidx=0
	rm2=HSPICE_mds.resmap(stg_swp,5,0)   #result map for cleaner data
	freq_cc=[None]*stg_swp
	
	#print ('len(rm.vr)=%d'%(len(rm.vr)))
	#print ('len(rm.vl[0][0])=%d'%(len(rm.vl[0][0])))
	mdl_map=HSPICE_mds.resmap(stg_swp,3,0)   #result map for model 
	for ntb in range(stg_swp):
		rm2.get_var(ntb,'FC')
		rm2.get_var(ntb,'CC')
		rm2.get_var(ntb,'freq_per')
		rm2.get_var(ntb,'freq')
		rm2.get_var(ntb,'TW')
		mdl_map.get_var(ntb,'NSTG')
		mdl_map.get_var(ntb,'Kstg')
		mdl_map.get_var(ntb,'Kgen')
		freq_cc[ntb]={}
		#print ntb
		for j in range(len(rm.vl[ntb][0])):       # for all command word
			for i in range(len(rm.vr)):       # for all variables
				if rm.vr[i][0:2]=='vf':    ##here!!!!! 0:3 vvf  <---> 0:2 vf
					fc=fc+float(rm.vl[ntb][i][j])
				if rm.vr[i][0:2]=='vc':
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
			if fc==fcidx:     #calculate model constant for only fcindx=nfc//2 Fnom? cc doesn't matter 
				kidx+=1
				kacc=kacc+(freq_per/(ndrv+cc))   #without effect of Nstg
				kavg=kacc/(kidx)
				freq_cc[ntb][int(cc)]=freq_per
			fc=0
			cc=0
		mdl_map.add(ntb,stg_start+ntb)
		mdl_map.add(ntb,kavg)
		mdl_map.add(ntb,kavg*(stg_start+ntb))
		Kgacc=Kgacc+kavg*(stg_start+ntb)
		Kg=Kgacc/(ntb+1)
		kacc=0
		kidx=0
				
	#print ('Kg=%e'%(Kg))		
	#print rm2.vr
	#print rm2.vl
	rm2.sort('TW')
	#print rm2.svar[0]
	#print rm2.vl[1]
	tws=sorted(rm2.svar[0])
	
	
	
	#######  plot CC  ########
	xaxis=[]
	yaxis=sorted(rm2.svar[0])  #TW 
	ymod=sorted(rm2.svar[0])  #TW
	Ymod=[]
	for i in range(len(ymod)):
		if ymod[i]%Ncf==fcidx:     ### !!!!!!!!!here !!!!!!!!!!!
			Ymod.append(ymod[i])   ### for only fc=nfc//2
	#print yaxis
	for i in range(stg_swp):
		xaxis.append(stg_start+i)     #num of stages
	Y,X=np.meshgrid(yaxis,xaxis)
	Ymod2,Xmod=np.meshgrid(Ymod,xaxis)
	Z=[None]*len(xaxis)
	Zmod=[None]*len(xaxis)
	Zerr=[None]*len(xaxis)
	err=[]
	
	for i in range(len(xaxis)):      #sweep x (stages)
		Z[i]=[] 
		Zmod[i]=[] 
		Zerr[i]=[] 
		for j in range(len(Ymod)):  #sweep y (TW)
			Z[i].append(rm2.svar[i][Ymod[j]][2])
			fmod=Kg*(ndrv+Ymod[j]//Ncf)/xaxis[i]
			Zmod[i].append(fmod)
			fsim=rm2.svar[i][Ymod[j]][2]
			Zerr[i].append(fsim-fmod)
			err.append(100*(fsim-fmod)/fsim)
	
	Errmax=max(err)
	#print err
	print('Kg:%f'%(Kg))
	print('Kg max error:%f%%'%(Errmax))
	#print mdl_map.vl
	fig=plt.figure()
	ax=fig.gca(projection='3d')
	ax_mod=fig.gca(projection='3d')
	ax_err=fig.gca(projection='3d')
	
	ax.plot_wireframe(Xmod, Ymod2, Z,color='b',label='sim result', rstride=1, cstride=1)
	ax.set_xlabel('num_stages')
	ax.set_ylabel('10*CC+FC')
	ax.set_zlabel('frequency')
	ax_mod.plot_wireframe(Xmod, Ymod2, Zmod,color='r',label='model', rstride=1, cstride=1)
	ax_err.plot_wireframe(Xmod, Ymod2, Zerr,color='g',label='error', rstride=1, cstride=1)
	legend=plt.legend(loc='upper right',fontsize='medium')

	if show==1:	
		plt.show()
	return Kg,freq_cc,Errmax	
	
	
	
	
	
	
#================================================================================================
# gen_result2 is the updated version that deals with VDD, TEMP parameters
# tbrf is generated for only nominal vdd, temp for now
# model constant (Kg) calculation takes vdd, temp into account
# Kg is a constant s.t freq=Kg*(Ndrv+Ncc)/Nstg
#================================================================================================

def gen_result2(ncell,ndrv,nfc,stg_start,stg_swp,Ncf,fcidx,num_meas,index,show,VDD,TEMP):
	skip_line=2   #default titles
	
	num_var=nfc+ncell+1
	num_words=num_var+num_meas+1   #+1 is +alter# index not included
	
	
	il=0
	iw=1
	k=0
	rm=HSPICE_mds.resmap(stg_swp,num_words,index)
	
	res_dir=[]
	
	set_tb=0
	for j in range(stg_swp):
		#res_path='./HSPICE/DUMP_result/tb_%dring8_osc%d_dp/'%(ndrv,stg_start+j)    ### here!!!
		res_path='./HSPICE/DUMP_result/tb_%dring%d_osc%d_FC%d_dp/'%(ndrv,ncell,stg_start+j,nfc)    #removed the exception for FC==128
		res_dir=[]
		for i in os.listdir(res_path):
			if i[0:6]=='worker' and i[0:7]!='worker.':
				r_result=open(res_path+i+'/tb_%dring%d_osc%d_FC%d.mt0'%(ndrv,ncell,j+stg_start,nfc))
				for line in r_result.readlines():
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								if iw<num_words+index+1:
									rm.get_var(j,word)
								else:
									rm.add(j,word)
								iw+=1
					elif il>skip_line+round(float(num_words)/3+float(1)/3)-1:    #change here!!!  ????
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
		
	#print('???? is : %d'%(round(num_words/3+1/3)))	
	#print('num word is : %d'%(num_words))	
	#print rm.vr
	#print rm.vl[0]
		
	fc=0
	cc=0
	freq_per=0
	freq=0
	ktemp=0
	kacc=0
	kavg=0
	Kg=0   #general const
	Kgacc=0   #general const
	kidx=0
	freq_cc=[None]*stg_swp
	vdd=0
	temp=0
	iavg=0	
	#---generate dicts for Kg cal---
	kavg={}
	kacc={}
	Kgacc={}
	Kg={}
	for V in VDD:
		Kgacc[V]={}
		Kg[V]={}
		for T in TEMP:
			Kgacc[V][T]=0
			Kg[V][T]=0

	#print ('len(rm.vr)=%d'%(len(rm.vr)))
	#print ('len(rm.vl[0][0])=%d'%(len(rm.vl[0][0])))
	mdl_map=HSPICE_mds.resmap(stg_swp,3,0)   #result map for model 
	rm2=HSPICE_mds.resmap(stg_swp,8,0)   #result map for cleaner data
	for ntb in range(stg_swp):
		rm2.get_var(ntb,'FC')
		rm2.get_var(ntb,'CC')
		rm2.get_var(ntb,'freq_per')
		rm2.get_var(ntb,'freq')
		rm2.get_var(ntb,'TW')
		rm2.get_var(ntb,'vdd')
		rm2.get_var(ntb,'temp')
		rm2.get_var(ntb,'iavg')
		mdl_map.get_var(ntb,'NSTG')
		mdl_map.get_var(ntb,'Kgen')
		freq_cc[ntb]={}  #dict format
		#print ntb
		for V in VDD:
			kavg[V]={}
			kacc[V]={}
			for T in TEMP:
				kavg[V][T]=0
				kacc[V][T]=0
		for j in range(len(rm.vl[ntb][0])):       # for all command word
			for i in range(len(rm.vr)):       # for all variables
				if rm.vr[i][0:2]=='vf':    ##here!!!!! 0:3 vvf  <---> 0:2 vf
					fc=fc+float(rm.vl[ntb][i][j])
				if rm.vr[i][0:2]=='vc':
					cc=cc+float(rm.vl[ntb][i][j])
				if rm.vr[i][0:3]=='per':
					freq_per=25/float(rm.vl[ntb][i][j])	
				if rm.vr[i][0:3]=='fre':
					freq=float(rm.vl[ntb][i][j])
				if rm.vr[i][0:3]=='vvd':
					vdd=float(rm.vl[ntb][i][j])
				if rm.vr[i][0:3]=='tem':
					temp=float(rm.vl[ntb][i][j])
				if rm.vr[i][0:3]=='iav':
					iavg=float(rm.vl[ntb][i][j])
			rm2.add(ntb,fc)
			rm2.add(ntb,cc)			
			rm2.add(ntb,freq_per)			
			rm2.add(ntb,freq)
			rm2.add(ntb,fc+Ncf*cc)
			rm2.add(ntb,vdd)
			rm2.add(ntb,temp)
			rm2.add(ntb,iavg)
			if fc==fcidx:              
				kidx+=1
				ktemp=(stg_start+ntb)*(freq_per/(ndrv+cc))
				kacc[vdd][temp]=kacc[vdd][temp]+ktemp
				kavg[vdd][temp]=kacc[vdd][temp]/kidx
				if vdd==VDD[0] and temp==TEMP[0]:  #only for nominal values
					freq_cc[ntb][int(cc)]=freq_per
			fc=0
			cc=0
		mdl_map.add(ntb,stg_start+ntb)
		mdl_map.add(ntb,kavg)
		for V in VDD:
			for T in TEMP:
				Kgacc[V][T]=Kgacc[V][T]+kavg[V][T]
				Kg[V][T]=Kgacc[V][T]/(ntb+1)  
		#kacc=0
		kidx=0
				
	#print ('Kg=%e'%(Kg))		
	#print rm2.vr
	#print rm2.vl[0]
	#rm2.sort('TW')
	
 	#print rm2.svar[0]
	#print rm2.vl[1]
	#tws=sorted(rm2.svar[0])

	#print ('Kg=')
	#print Kg	

	Errmax=0	
	
	#######  plot CC  ########
	#xaxis=[]
	#yaxis=sorted(rm2.svar[0])  #TW 
	#ymod=sorted(rm2.svar[0])  #TW
	#Ymod=[]
	#for i in range(len(ymod)):
	#	if ymod[i]%Ncf==fcidx:     ### !!!!!!!!!here !!!!!!!!!!!
	#		Ymod.append(ymod[i])
	##print yaxis
	#for i in range(stg_swp):
	#	xaxis.append(stg_start+i)     #num of stages
	#Y,X=np.meshgrid(yaxis,xaxis)
	#Ymod2,Xmod=np.meshgrid(Ymod,xaxis)
	#Z=[None]*len(xaxis)
	#Zmod=[None]*len(xaxis)
	#Zerr=[None]*len(xaxis)
	#err=[]
	#
	#for i in range(len(xaxis)):      #sweep x (stages)
	#	Z[i]=[] 
	#	Zmod[i]=[] 
	#	Zerr[i]=[] 
	#	for j in range(len(Ymod)):  #sweep y (TW)
	#		Z[i].append(rm2.svar[i][Ymod[j]][2])
	#		fmod=Kg*(ndrv+Ymod[j]//Ncf)/xaxis[i]
	#		Zmod[i].append(fmod)
	#		fsim=rm2.svar[i][Ymod[j]][2]
	#		Zerr[i].append(fsim-fmod)
	#		err.append(100*(fsim-fmod)/fsim)
	#
	#Errmax=max(err)
	##print err
	#print('Kg:%f'%(Kg))
	#print('Kg max error:%f%%'%(Errmax))
	##print mdl_map.vl
	#fig=plt.figure()
	#ax=fig.gca(projection='3d')
	#ax_mod=fig.gca(projection='3d')
	#ax_err=fig.gca(projection='3d')
	#
	#ax.plot_wireframe(Xmod, Ymod2, Z,color='b',label='sim result', rstride=1, cstride=1)
	#ax.set_xlabel('num_stages')
	#ax.set_ylabel('10*CC+FC')
	#ax.set_zlabel('frequency')
	#ax_mod.plot_wireframe(Xmod, Ymod2, Zmod,color='r',label='model', rstride=1, cstride=1)
	#ax_err.plot_wireframe(Xmod, Ymod2, Zerr,color='g',label='error', rstride=1, cstride=1)
	#legend=plt.legend(loc='upper right',fontsize='medium')

	#if show==1:	
	#	plt.show()
	return Kg,freq_cc,Errmax	

