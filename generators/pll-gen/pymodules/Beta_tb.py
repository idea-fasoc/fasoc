### HSPICE tb generation ###

import HSPICE_mds
import sys

#=======================================================
#     vdd[0] is the nominal vdd 
#     temp[0] is the nominal temp
#     8 points of sim: CC+FC= 0+0,0+Nfc,1+0,1+Nfc
#		 (Ncc-1)+0, (Ncc-1)+Nfc, Ncc+0, Ncc+Nfc 
#=======================================================

def gen_tb_pex(CF,Cc,Cf,PDK,finesim,tb_dir,format_dir,ncell,ndrv,nfc,nstg_start,nstg_end,nstg_step,vdd,temp,nper,design_name,sav):
	#=====================================================
	# model constants for trans simulation time calculation 
	#=====================================================
#	CF=3.805743e-13      
#	Cc=1.865344e-11      
#	Cf=1.781383e-12
	CB=Cc*(ndrv+ncell)+Cf*nfc      


	vm1=HSPICE_mds.varmap()   ###modify here!!
	vm1.get_var('ncell',ncell,ncell,1)
	vm1.get_var('nstage',nstg_start,nstg_end,nstg_step) #vm1.comblist[1]=nstg
	vm1.get_var('ndrive',ndrv,ndrv,1)
	vm1.cal_nbigcy()
	vm1.combinate()
	num_var=1
	nstg_swp=nstg_end-nstg_start+1

	N_recur=5*3*len(vdd)*len(temp)*4
#	sys.setrecursionlimit(N_recur+1)  #expand the recursion limit if exceeded

	if len(vdd)>1 and len(temp)>1:
		vdd_min,vdd_max=HSPICE_mds.mM(vdd)  #generate function of minMax step
		vdd.remove(vdd_min)
		temp_min,temp_max=HSPICE_mds.mM(temp)
		temp.remove(temp_min)	
	elif len(vdd)==1 and len(temp)==1:
		vdd_min=vdd[0]
		vdd_max=vdd[0]
		temp_min=temp[0]
		temp_max=temp[0]

	#r_file=open("./tb_ring_osc_FC.sp","r")
	if finesim==0:
		if sav==0:
			r_file=open(format_dir+"form_pex_tb_ring_osc.sp","r")
		else:
			r_file=open(format_dir+"form_pex_tb_ring_osc_sav.sp","r")
	elif finesim==1:	
		r_file=open(format_dir+"form_fs_pex_tb_ring_osc.sp","r")
	
	lines=list(r_file.readlines())
	
	for i in range(1,len(vm1.comblist[0])):
		#===============================================
		#  transient sim time calculation 
		#===============================================
		Fmin_mdl=1/(CB+nfc*CF)*(ndrv)/vm1.comblist[1][i] 
		print('estimated Fmin=%e'%(Fmin_mdl)) 
		#per_max_mdl=vm1.comblist[1][i]*(CB+nfc*CF)/ndrv
		per_max_mdl=1/Fmin_mdl
		print('estimated sim_time=%e'%(per_max_mdl*25)) 
		TD=00e-9
		#===============================================
		# writing  
		#===============================================
		L_lines=[]
		L_flag=0
		netmap1=HSPICE_mds.netmap()  #35
		netmap1.get_net('Ti',None,TD+per_max_mdl*25,TD+per_max_mdl*25,1)
		netmap1.get_net('TE',None,TD+per_max_mdl*(25+nper),TD+per_max_mdl*(25+nper),1)
		netmap1.get_net('vd',None,vdd[0],vdd[0],1)
		netmap1.get_net('DN',design_name,None,None,None)
		#----- only string -----------
		netmap1.get_net('PK',PDK,None,None,None)
		#===============================================
		#   number of control node definition for v2
		#===============================================
		N_ctrl_fc=vm1.comblist[1][i]*nfc
		N_ctrl_cc=vm1.comblist[1][i]*ncell
		#===============================================
		#  generate variable maps: FCWs to sweep
		#  (CC,FC)=(0,0),(0,Nfc),(1,0),(Ncc//2,0)
		#          (Ncc//2,Nfc//2),(Ncc//2,Nfc)
		#	   (Ncc,Nfc) 
		#===============================================
		vm2=HSPICE_mds.varmap()
		vm2.get_var('vdd',vdd[0],vdd[0],1)     #vm2.comblist[0]=vdd   #???? why like this? because of get_var 
		if len(vdd)>1:
			for i in range(1,len(vdd)):
				vm2.add_val('vdd',vdd[i],vdd[i],1)
		vm2.get_var('temp',temp[0],temp[0],1)  #vm2.comblist[1]=temp
		if len(temp)>1:
			for i in range(1,len(temp)):
				vm2.add_val('temp',temp[i],temp[i],1)
		vm2.cal_nbigcy()
		vm2.combinate()  #vdd/temp combination
		var_list=[[[] for x in range(7)] for y in range(len(vm2.comblist[0])-1)]
		for i in range(1,len(vm2.comblist[0])):
			var_list[i-1][0]=[0,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][1]=[0,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][2]=[1,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][3]=[N_ctrl_cc//2,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][4]=[N_ctrl_cc//2,N_ctrl_fc//2,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][5]=[N_ctrl_cc//2,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][6]=[N_ctrl_cc,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]

		#===================================================================
		#   DATA table gen for parametric sweep
		#===================================================================
		#----- lateral stuffs: names --------
		netmap1.get_net('vf','vf',0,N_ctrl_fc-1,1) #for v2
		netmap1.get_net('vc','vc',0,N_ctrl_cc-1,1) #for v2

		#----- lateral stuffs: FCW values --------
		with open(tb_dir+"tb_"+design_name+".sp","w") as w_file:
			for line in lines:
				if line[0:4]=='@L@W':
					line=line[2:len(line)-1]
					for ivt in range(len(var_list)):
						for ifcw in range(len(var_list[0])):
							netmap2=HSPICE_mds.netmap()
							netmap2.get_net('f1',None,'d2o',N_ctrl_fc,var_list[ivt][ifcw][1])	 
							netmap2.get_net('c1',None,'d2o',N_ctrl_cc,var_list[ivt][ifcw][0])	 
							netmap2.get_net('vd',None,var_list[ivt][ifcw][2],var_list[ivt][ifcw][2],1)	 
							netmap2.get_net('tm',None,var_list[ivt][ifcw][3],var_list[ivt][ifcw][3],1)	 
							netmap2.printline(line,w_file)
							w_file.write('\n')	 
	
					#for j in range(1,len(vm2.comblist[0])):
					##	print('one line')
					#	#print vm2.comblist[0][j]
					#	netmap2=HSPICE_mds.netmap()
					#	#netmap2.get_net('f1',None,'d2o',nfc,vm2.comblist[0][j])	 
					#	netmap2.get_net('f1',None,'d2o',N_ctrl_fc,vm2.comblist[0][j])	 
					#	netmap2.get_net('c1',None,'d2o',N_ctrl_cc,vm2.comblist[1][j])	 
					#	netmap2.get_net('vd',None,vm2.comblist[2][j],vm2.comblist[2][j],1)	 
					#	netmap2.get_net('tm',None,vm2.comblist[3][j],vm2.comblist[3][j],1)
					#	netmap2.printline(line,w_file)
					#	w_file.write('\n')	 
				else:
					netmap1.printline(line,w_file)
	
		#	print("tb nstg=%d"%(i+nstg_start-1))
