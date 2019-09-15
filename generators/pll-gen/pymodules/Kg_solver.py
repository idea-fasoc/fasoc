#======== derive the value of Cc/I, Cf/I, CF/I ======

#=========================================================
# solves for cap values using inputs
# v2 has vdd, temp configuration
# inputs: 2sets of design params, each result
# cf idK are lists
# Kg is constant when TW=N_ctrl_cc//2+N_ctrl_fc//2 
#=========================================================
def C_solve_v2(Kg1_list,Kg2_list,idK1,idK2,cf1,cf2):
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

#=========================================================
# solves for cap values using inputs
# inputs: 2sets of design params, each result
# cf,idK are lists, dK not used
# Kg is just value  
#=========================================================
def C_solve(Kg1,Kg2,dK1,dK2,idK1,idK2,cf1,cf2):
	CF=(sum(idK1)+sum(idK2))/(len(idK1)+len(idK2))
	maxE=max(max(idK2),max(idK2))-CF
	minE=CF-min(min(idK2),min(idK1))
	Emax_CF=max(maxE,minE)/CF*100
	const1=1/Kg1-1/Kg2
	if cf1[0]==cf2[0]:
		Cf=(const1-(cf1[2]-cf2[2])*CF)/(cf1[1]-cf2[1])
		Cc1=(1/Kg1-cf1[1]*Cf-cf1[2]*CF)/cf1[0]
		Cc2=(1/Kg2-cf2[1]*Cf-cf2[2]*CF)/cf2[0]
		Cc_err=abs(Cc1-Cc2)/(Cc1+Cc2)*2*100
		#print ('max idK=%e'%(max(max(idK2),max(idK2))))
		#print ('max error idK=%e'%(maxE))
		#print ('min error idK=%e'%(minE))
		return CF,Emax_CF,Cc1,Cf
	elif cf1[1]==cf2[1]:
		Cc=(const1-(cf1[2]-cf2[2])*CF)/(cf1[0]-cf2[0])
		Cf1=(1/Kg1-cf1[0]*Cc-cf1[2]*CF)/cf1[1]
		Cf2=(1/Kg2-cf2[0]*Cc-cf2[2]*CF)/cf2[1]
		Cf_err=abs(Cf1-Cf2)/(Cf1+Cf2)*2*100
		#print ('max idK=%e'%(max(max(idK2),max(idK2))))
		#print ('max error idK=%e'%(maxE))
		#print ('min error idK=%e'%(minE))
		return CF,Emax_CF,Cc,Cf1
		


