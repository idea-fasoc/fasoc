import math
import Math_model

#===============================================================================================
# v2 has pass_flag, spec_range added
#	pass_flag: 1(passed), 0(failed)
#	spec_range: provide spec range in the spec order of spec_priority
#	spec_priority: ex) [Fnom, IB_PN, dco_PWR,Fmax,....]
#			Fnom includes Fnom_*
#===============================================================================================

def ds_Fnom_v2(spec_priority,Fmax,Fmin,Fres,Fnom_min,Fnom_max,FCR_min,IB_PN,dco_PWR,CF,Cf,Cc,mult_Con,mult_Coff,Iavg_const,PN_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC):
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
	inSpecDic={"Fmax":Fmax,"Fnom_max":Fnom_max,"Fnom_min":Fnom_min,"Fmin":Fmin,"Fres":Fres,"FCR":FCR_min,"dco_PWR":dco_PWR,"IB_PN":IB_PN}					
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
					Np=Nd+Nc
					##CF=mult_Con*CF
					CB=(Np)*Cc+Nf*Cf
					CB_pre=(Np)*Cc_pre+Nf*Cf_pre
					Fnom_fcmax=(Nd+Nc/2)/(CB*M)
					Fnom_fcmin=(Nd+Nc/2)/((CB+Nf*CF)*M)
					dFf_mdl=Fnom_fcmax-Fnom_fcmin
					dFc_mdl=1/CB/M/Nc    # is this right?
					freqCoverRatio=dFf_mdl/dFc_mdl
					Fres_mdl=(Fnom_fcmax-Fnom_fcmin)/Nf/M
					Fmin_mdl=1/(CB+Nf*CF)*(Nd)/M
					Fmax_mdl=1/(CB)*(Nd+Nc)/M
					#Fnom_mdl=(Nd+Nc/2)/(CB*M+Nf/2*Cf*M)
					Fnom_mdl=(Nd+Nc/2)/(CB*M)
					
					Fnom_mdl_pre=(Nd+Nc/2)/(CB_pre*M+Nf/2*Cf_pre*M) # pre-pex model
					Ctotal=Cc*(Nd+Nc/2)+Cf*Nf+CF*Nf/2
					Iavg=Ctotal*Iavg_const
					Pwr_mdl=Iavg*vdd[0]
					#=== overwrite with spec_cal ===	
					#Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal=Math_model.spec_cal_pex65_test(Nd,Nc,Nf,M,Cc,Cf,CF,mult_Con,mult_Coff) #post-pex
					#IB_PN_mdl=20*math.log10(PN_const/math.sqrt((Nd+Nc/2)*1e6/(Fnom_mdl*Fnom_mdl))) #in dBc
					#---TDC, DCO Qnoise---
					tdcn_mdl=((2*math.pi)**2)/12*(1/M/4)**2/Fref #--TDC quantization noise model
					dcon_mdl=(2*math.pi)**2*(Fres_mdl/1e6)/10e6  #-- DCO quantization noise model
					#print('Fnom_mdl=%e'%(Fnom_mdl))
					pn_mdl=(PN_const/math.sqrt((Nd+Nc/2)*1e6/(Fnom_mdl*Fnom_mdl)))**2 #-- PN model
					#print('pn_mdl=%e'%(pn_mdl))
					IB_PN_mdl=10*math.log10(tdcn_mdl+dcon_mdl+pn_mdl) #in dBc, adding quantization noises
					Area_mdl=(Nd+Nc)*M*A_CC+Nf*M*A_FC		
					#===============================================================
					# generate dictionary list for specs
					# and filter the ones that satisfy input spec in the order in 
					# spec_priority
					#===============================================================
					specDic={"Fnom":Fnom_mdl,"Fmax":Fmax_mdl,"Fmin":Fmin_mdl,"Fres":Fres_mdl,"FCR":freqCoverRatio,"dco_PWR":Pwr_mdl,"IB_PN":IB_PN_mdl}
					spec_depth=0
					for spec in spec_priority:
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
								max_spec_depth, specRangeDic = depth_check(spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec)
						elif fst_spec_flag==1 and itr_pass_flag==1:   # record only the first failed spec's value to specRangeDic
							if spec_priority[spec]=="lo":
								if specDic[spec] < inSpecDic[spec]:
									#specRangeDic[spec].append("passed")
									#specRangeDic[spec].append(specDic[spec])
									pass
								else:
									itr_pass_flag=0 
									#specRangeDic[spec].append(specDic[spec])
									max_spec_depth, specRangeDic = depth_check(spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec)
							elif spec_priority[spec]=="hi": 
								if specDic[spec] > inSpecDic[spec]:
									#specRangeDic[spec].append("passed")
									#specRangeDic[spec].append(specDic[spec])
									pass
								else:
									itr_pass_flag=0 
									#specRangeDic[spec].append(specDic[spec])
									max_spec_depth, specRangeDic = depth_check(spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec)
						else:
							itr_pass_flag=0
						spec_depth=spec_depth+1
					if itr_pass_flag==1:  # all specs passed
						passed_designs.append([Nd,Nc,Nf,M])
						#passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,Pwr_mdl,Area_mdl])
						passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,freqCoverRatio,Pwr_mdl,Area_mdl,IB_PN_mdl])
						print ('** passed model specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2f, pwr_mdl=%.2e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,IB_PN_mdl,Pwr_mdl))
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
	if fst_pass==[]:
		print('!!! first spec failed !!!')
		print('first spec range: %e ~ %e' %(min(fst_fail),max(fst_fail)))


	return pass_flag, passed_designs, passed_specs, specRangeDic

def depth_check (spec_depth,max_spec_depth,specDic,specRangeDic,empty_specRangeDic,spec):
	if max_spec_depth <= spec_depth:
		if max_spec_depth < spec_depth:
			max_spec_depth=spec_depth
			specRangeDic=empty_specRangeDic
		specRangeDic[spec].append(specDic[spec])
	return max_spec_depth, specRangeDic 			
#======================================================================================
# module that finds the design solution for given specs
# Alpha release supports only nominal frequency
#======================================================================================

def ds_Fnom_pex(Fnom_min,Fnom_max,FCR_min,CF,Cf,Cc,Iavg_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC,mult_Con,mult_Coff,print_specs):
	passed_designs=[]
	passed_specs=[]
	found_design=0

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
		

	for Nd in Ndrv_list:
		for Nc in Ncc_list:
			for Nf in Nfc_list:
				for M in Nstg_list:
					Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal=Math_model.spec_cal_pex65(Nd,Nc,Nf,M,Cc,Cf,CF,mult_Con,mult_Coff)
					Iavg=Ctotal*Iavg_const
					Pwr_mdl=Iavg*vdd[0]	
					Area_mdl=(Nd+Nc)*M*A_CC+Nf*M*A_FC			
					if Fnom_mdl < Fnom_max and Fnom_mdl > Fnom_min and freqCoverRatio > FCR_min:
						passed_designs.append([Nd,Nc,Nf,M])
						passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,freqCoverRatio,Pwr_mdl,Area_mdl])
						found_design=1
					if print_specs==1:
						print('Fnom_mdl=%e'%(Fnom_mdl))	
						print('frequency cover ratio = %f'%(freqCoverRatio))
	if found_design==0:
		print('couldnt find the design')	
	return passed_designs, passed_specs


def ds_Fnom(Fnom_min,Fnom_max,FCR_min,CF,Cf,Cc,Iavg_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC):
	passed_designs=[]
	passed_specs=[]

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
		

	for Nd in Ndrv_list:
		for Nc in Ncc_list:
			for Nf in Nfc_list:
				for M in Nstg_list:
					Np=Nd+Nc
					CB=(Np)*Cc+Nf*Cf
					Fnom_fcmax=(Nd+Nc/2)/(CB*M)
					Fnom_fcmin=(Nd+Nc/2)/((CB+Nf*CF)*M)
					dFf_mdl=Fnom_fcmax-Fnom_fcmin
					dFc_mdl=1/CB/M/Nc    # is this right?
					freqCoverRatio=dFf_mdl/dFc_mdl
					
					Fres_mdl=(Fnom_fcmax-Fnom_fcmin)/Nf/M
					Fmin_mdl=1/(CB+Nf*CF)*(Nd)/M
					Fmax_mdl=1/(CB)*(Nd+Nc)/M
					Fnom_mdl=(Nd+Nc/2)/(CB*M)
					Ctotal=Cc*(Nd+Nc/2)+Cf*Nf+CF*Nf/2
					Iavg=Ctotal*Iavg_const
					Pwr_mdl=Iavg*vdd[0]	
					Area_mdl=(Nd+Nc)*M*A_CC+Nf*M*A_FC			
					if Fnom_mdl < Fnom_max and Fnom_mdl > Fnom_min and freqCoverRatio > FCR_min:
						passed_designs.append([Nd,Nc,Nf,M])
						passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,Pwr_mdl,Area_mdl])
					#print('%e'%(Fnom_mdl))	
					#print(freqCoverRatio)	
	return passed_designs, passed_specs
		
#temporary function for quick check				 	
def ds_Fnom_tempPex(Fnom_min,Fnom_max,FCR_min,CF,Cf,Cc,Iavg_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC):
	passed_designs=[]
	passed_specs=[]

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
		

	for Nd in Ndrv_list:
		for Nc in Ncc_list:
			for Nf in Nfc_list:
				for M in Nstg_list:
					Np=Nd+Nc
					CB=(Np)*Cc+Nf*Cf
					Fnom_fcmax=(Nd+Nc/2)/(CB*M)
					Fnom_fcmin=(Nd+Nc/2)/((CB+Nf*CF)*M)
					dFf_mdl=Fnom_fcmax-Fnom_fcmin
					dFc_mdl=1/CB/M/Nc    # is this right?
					freqCoverRatio=dFf_mdl/dFc_mdl
					
					Fres_mdl=(Fnom_fcmax-Fnom_fcmin)/Nf/M/2.2
					Fmin_mdl=1/(CB+Nf*CF)*(Nd)/M/2.2
					Fmax_mdl=1/(CB)*(Nd+Nc)/M/2.2
					Fnom_mdl=(Nd+Nc/2)/(CB*M)/2.2
					Ctotal=Cc*(Nd+Nc/2)+Cf*Nf+CF*Nf/2
					Iavg=Ctotal*Iavg_const
					Pwr_mdl=Iavg*vdd[0]*1.08	
					Area_mdl=(Nd+Nc)*M*A_CC+Nf*M*A_FC			
					if Fnom_mdl < Fnom_max and Fnom_mdl > Fnom_min and freqCoverRatio > FCR_min:
						passed_designs.append([Nd,Nc,Nf,M])
						passed_specs.append([Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,freqCoverRatio,Pwr_mdl,Area_mdl])
					#print('%e'%(Fnom_mdl))	
					#print(freqCoverRatio)	
	return passed_designs, passed_specs
