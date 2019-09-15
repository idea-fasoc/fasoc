#======================================================================================
# module that finds the design solution for given specs
# Alpha release supports only nominal frequency
#======================================================================================
import Math_model

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
