#=====================================================================================================
#  generates 2 outputs
#	1. dco_Nstg.pex.netlist: with modified input sequence
#	2. pex_XringX_oscX.sp: netlist wrapper with all the voltage source name defined
#=====================================================================================================
import txt_mds
import re
import subprocess as sp
import shutil

def gen_pll_pex_wrapper(switch,buf,PD,raw_pex_dir,design_name,netlist_dir,format_dir,input_array,vdd):
	if PD==1:
		if buf==1:
			if switch==0:
				r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll_buf.sp","r")
			elif switch==1:
				r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll_buf_switch.sp","r")
		else:
			r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll2.sp","r")
	else:
		r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())

	
	netmap1=txt_mds.netmap() 
	### register all the inputs to netmap ###
	netmap1.get_net('nd',netlist_dir,None,None,None)
	netmap1.get_net('dn',design_name,None,None,None)
	netmap1.get_net('fm','pex.netlist',None,None,None)
	for i in range(len(input_array)):
		bin_val=bin(input_array[i][4])
		bin_len=len(bin_val)-2
		num_zero=input_array[i][0]-bin_len
		bin_fin='0'*num_zero+bin_val[2:len(bin_val)]
		print("%s's bin_fin=%s"%(input_array[i][2],bin_fin))	
		print("%s's len(bin_fin)=%d, given length=%d"%(input_array[i][2],len(bin_fin),input_array[i][0]))	
		netmap1.get_net(input_array[i][1],None,i*100,i*100+len(bin_fin)-1,1)	# v#	
		netmap1.get_net(input_array[i][2],None,0,len(bin_fin)-1,1)  # bit#		
		for j in range(len(bin_fin)):
#			print(int(bin_fin[len(bin_fin)-j-1]))
			netmap1.get_net(input_array[i][3],None,int(bin_fin[len(bin_fin)-j-1])*vdd,int(bin_fin[len(bin_fin)-j-1])*vdd,1) #vdd or 0	

	r_raw_netlist=open(raw_pex_dir+"/"+design_name+".pex.netlist","r")
	w_raw_netlist=open(netlist_dir+"/"+design_name+".pex.netlist","w")

	raw_lines=list(r_raw_netlist.readlines())
	nm2=txt_mds.netmap()	
	### modify the .include file path in pex.netlist ###
	for line in raw_lines:
		if line[0:8]=='.include':
			line='.include '+ '"./../../'+netlist_dir+line[10:len(line)]
			nm2.printline(line,w_raw_netlist)	
		else:
			nm2.printline(line,w_raw_netlist)	
			

	### copies the first defined instant into inst_def for matching input sequence of pex.netlist###
	inst_def=[]
	inst_start=0
	for line in raw_lines:
		if inst_start==1 and line[0:1]!='+': #instance def end
			inst_start=0	
		elif line[0:7]=='.subckt':
			inst_start=1	
			print('found subckt')
			inst_def.append(line)
		elif inst_start==1 and line[0:1]=='+':
			inst_def.append(line)

	### cut out '.SUBCKT test_synth_pll2' ###
	inst_def_words=inst_def[0].split()
	inst_def_words=inst_def_words[2:len(inst_def_words)]

	### write down the 'wrapped_test_synth_pll2.sp' ###
	for line in lines:
		if line[0:3]=='xi4':
			line=line+'+ '+' '.join(inst_def_words)+'\n'
			netmap1.printline(line,w_netlist)	
			for inst_def_line in inst_def[1:len(inst_def)]:
				netmap1.printline(inst_def_line,w_netlist)
			netmap1.printline('+ '+design_name,w_netlist)		
		else:
			netmap1.printline(line,w_netlist)	
	

def gen_pll_pre_wrapper2(switch,buf,PD,raw_sp_dir,design_name,netlist_dir,format_dir,input_array,vdd):
	if PD==1:
		if buf==1:
			if switch==0:
				r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll_buf.sp","r")
			elif switch==1:
				r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll_buf_switch.sp","r")
		else:
			r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll2.sp","r")
	else:
		r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll.sp","r")
	#if PD==1:
	#	r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll2.sp","r")  # the one with VDD_DCO
	#else:
	#	r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=txt_mds.netmap() 
	#==== input_array[0]: bitwidth, [1]: flag1, [2]: flag 2, [3]: flag3, [4]: dec_val ===
	### register all the inputs to netmap ###
	netmap1.get_net('nd',netlist_dir,None,None,None)
	netmap1.get_net('dn',design_name,None,None,None)
	netmap1.get_net('fm','sp',None,None,None)
	for i in range(len(input_array)):
		bin_val=bin(input_array[i][4])
		bin_len=len(bin_val)-2
		num_zero=input_array[i][0]-bin_len
		bin_fin='0'*num_zero+bin_val[2:len(bin_val)]
		print("%s's bin_fin=%s"%(input_array[i][2],bin_fin))	
		print("%s's len(bin_fin)=%d, given length=%d"%(input_array[i][2],len(bin_fin),input_array[i][0]))	
		netmap1.get_net(input_array[i][1],None,i*100,i*100+len(bin_fin)-1,1)	# v#	
		netmap1.get_net(input_array[i][2],None,0,len(bin_fin)-1,1)  # bit#		
		for j in range(len(bin_fin)):
#			print(int(bin_fin[len(bin_fin)-j-1]))
			netmap1.get_net(input_array[i][3],None,int(bin_fin[len(bin_fin)-j-1])*vdd,int(bin_fin[len(bin_fin)-j-1])*vdd,1) #vdd or 0	

	r_raw_netlist=open(raw_sp_dir+"/"+design_name+".sp","r")
	w_raw_netlist=open(netlist_dir+"/"+design_name+".sp","w")

	raw_lines=list(r_raw_netlist.readlines())
	nm2=txt_mds.netmap()	
	dffchk=0
	inst_def=[]
	inst_start=0
	### modify the .include file path in pex.netlist ###
	for line in raw_lines:
		if dffchk==0:
			if line[8:11]=='DFF':
				dffchk=1
				nm2.printline(line,w_raw_netlist)	
			else:
				print('unwanted subckt def found. will be eliminated.')
		else:
			words=line.split()
			if len(words)>1 and words[1]==design_name:
				inst_start=1
				inst_def.append(line)
			elif inst_start==1 and line[0:1]=='+':
				inst_def.append(line)
			elif inst_start==1 and line[0:1]!='+':
				inst_start=0
			nm2.printline(line,w_raw_netlist)	

	### cut out '.SUBCKT test_synth_pll2' ###
	inst_def_words=inst_def[0].split()
	inst_def_words=inst_def_words[2:len(inst_def_words)]

	### write down the 'wrapped_test_synth_pll2.sp' ###
	for line in lines:
		if line[0:3]=='xi4':
			line=line+'+ '+' '.join(inst_def_words)+'\n'
			netmap1.printline(line,w_netlist)	
			for inst_def_line in inst_def[1:len(inst_def)]:
				netmap1.printline(inst_def_line,w_netlist)
			netmap1.printline('+ '+design_name,w_netlist)		
		else:
			netmap1.printline(line,w_netlist)	


def gen_pll_prepex_wrapper(design_name,netlist_dir,format_dir,input_array,vdd):
	r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=txt_mds.netmap() 
	#==== input_array[0]: bitwidth, [1]: flag1, [2]: flag 2, [3]: flag3, [4]: dec_val ===
	netmap1.get_net('nd',netslit_dir,None,None,None)
	netmap1.get_net('dn',design_name,None,None,None)
	netmap1.get_net('fm','sp',None,None,None)

	netmap1.get_net('dn',design_name,None,None,None)
	for i in range(len(input_array)):
		bin_val=bin(input_array[i][4])
		bin_len=len(bin_val)-2
		num_zero=input_array[i][0]-bin_len
		bin_fin='0'*num_zero+bin_val[2:len(bin_val)]
		print("%s's bin_fin=%s"%(input_array[i][2],bin_fin))	
		print("%s's len(bin_fin)=%d, given length=%d"%(input_array[i][2],len(bin_fin),input_array[i][0]))	
		netmap1.get_net(input_array[i][1],None,i*100,i*100+len(bin_fin)-1,1)	# v#	
		netmap1.get_net(input_array[i][2],None,0,len(bin_fin)-1,1)  # bit#		
		for j in range(len(bin_fin)):
#			print(int(bin_fin[len(bin_fin)-j-1]))
			netmap1.get_net(input_array[i][3],None,int(bin_fin[len(bin_fin)-j-1])*vdd,int(bin_fin[len(bin_fin)-j-1])*vdd,1) #vdd or 0	
		
	for line in lines:
		netmap1.printline(line,w_netlist)

	
def gen_dco_pex_wrapper(extDir,netlistDir,format_dir,ncc,ndrv,nfc,nstg,ninterp,designName,fc_en_type):
	r_netlist=open(format_dir+"/form_pex_dco.sp","r")
	w_netlist=open(netlistDir+"/"+"wrapped_"+designName+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=txt_mds.netmap() 
	### include pex.netlist ###
	netmap1.get_net('dn',designName,None,None,None)
	### edge_sel voltage pulses ###
	netmap1.get_net('ve',None,1,nstg*4-1,1)	
	netmap1.get_net('ES',None,1,nstg*4-1,1) # for edge sel	
	
	### enable voltages for CC,FC ###
	netmap1.get_net('vf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('nf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('Vf','vf',0,nfc*nstg-1,1) #for v2	
	netmap1.get_net('vc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('nc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('Vc','vc',0,ncc*nstg-1,1) #for v2

	r_raw_netlist=open(extDir+"run/"+designName+".pex.netlist","r")
	w_raw_netlist=open(netlistDir+"/"+designName+".pex.netlist","w")
	raw_lines=list(r_raw_netlist.readlines())
	
	nm2=txt_mds.netmap()	
	### modify the .include file path in pex.netlist ###
	for line in raw_lines:
		if line[0:8]=='.include':
			line='.include '+ '"'+netlistDir+line[10:len(line)] #--- absolute path ---
			nm2.printline(line,w_raw_netlist)	
		else:
			nm2.printline(line,w_raw_netlist)	


	### copies the first defined instant into inst_def for matching input sequence of pex.netlist###
	inst_def=[]
	inst_start=0
	for line in raw_lines:
		if inst_start==1 and line[0:1]!='+': #instance def end
			inst_start=0	
		elif line[0:7]=='.SUBCKT' or line[0:7]=='.subckt':
			inst_start=1	
			print('found subckt')
			inst_def.append(line)
		elif inst_start==1 and line[0:1]=='+':
			inst_def.append(line)

	### cut out '.SUBCKT test_synth_pll2' ###
	inst_def_words=inst_def[0].split()
	inst_def_words=inst_def_words[2:len(inst_def_words)]

	### write down the 'wrapped_test_synth_pll2.sp' ###
	for line in lines:
		if line[0:3]=='xi4':
			line=line+'+ '+' '.join(inst_def_words)+'\n'
			netmap1.printline(line,w_netlist)	
			for inst_def_line in inst_def[1:len(inst_def)]:
				netmap1.printline(inst_def_line,w_netlist)
			netmap1.printline('+ '+designName,w_netlist)		
		else:
			netmap1.printline(line,w_netlist)	
	#-------------------------------------------
	# copy .pxi, .pex
	#-------------------------------------------
	try:
		shutil.copyfile(extDir+'/run/'+designName+'.pex.netlist.pxi',netlistDir+'/'+designName+'.pex.netlist.pxi')
		#p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.pxi',netlistDir+'/'+designName+'.pex.netlist.pxi'])
		#p.wait()
	except:
		shutil.copyfile(extDir+'/run/'+designName+'.pex.netlist.'+designName+'.pxi',netlistDir+'/'+designName+'.pex.netlist.'+designName+'.pxi')
		#p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.'+designName+'.pxi',netlistDir+'/'+designName+'.pex.netlist.'+designName+'.pxi'])
		#p.wait()
	shutil.copyfile(extDir+'/run/'+designName+'.pex.netlist.pex',netlistDir+'/'+designName+'.pex.netlist.pex')
	#p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.pex',netlistDir+'/'+designName+'.pex.netlist.pex'])
	#p.wait()

def gen_tb_wrapped(hspiceModel,tb_dir,format_dir,ncell,ndrv,nfc,nstg,vdd,temp,fc_en_type,sim_time,corner_lib,designName,netlistDir):
	#=====================================================
	# model constants for trans simulation time calculation 
	#=====================================================
	if len(vdd)>1 and len(temp)>1:
		vdd_min,vdd_max=txt_mds.mM(vdd)  #generate function of minMax step
		vdd.remove(vdd_min)
		temp_min,temp_max=txt_mds.mM(temp)
		temp.remove(temp_min)	
	elif len(vdd)==1 and len(temp)==1:
		vdd_min=vdd[0]
		vdd_max=vdd[0]
		temp_min=temp[0]
		temp_max=temp[0]

	r_file=open(format_dir+"form_tb_ring_osc.sp","r")
	lines=list(r_file.readlines())
	
	#===============================================
	# writing  
	#===============================================
	L_lines=[]
	L_flag=0
	netmap1=txt_mds.netmap()  #35
	netmap1.get_net('Ti',None,sim_time,sim_time,1)
	netmap1.get_net('TE',None,sim_time,sim_time,1)
	netmap1.get_net('vd',None,vdd[0],vdd[0],1)
	netmap1.get_net('ND',netlistDir,None,None,1)
	netmap1.get_net('dn','wrapped_'+designName,None,None,1)
	#----- only string -----------
	netmap1.get_net('hm',hspiceModel,None,None,None)
	netmap1.get_net('cr',corner_lib,None,None,None)
	#===============================================
	#   number of control node definition for v2
	#===============================================
	N_ctrl_fc=nstg*nfc
	N_ctrl_cc=nstg*ncell
	#===============================================
	#  generate variable maps: FCWs to sweep
	#  (CC,FC)=(0,0),(0,Nfc),(1,0),(Ncc//2,0)
	#          (Ncc//2,Nfc//2),(Ncc//2,Nfc)
	#	   (Ncc,Nfc) 
	#===============================================
	vm2=txt_mds.varmap()
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
	if fc_en_type==1:
		for i in range(1,len(vm2.comblist[0])):
			var_list[i-1][0]=[0,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][1]=[0,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][2]=[1,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][3]=[N_ctrl_cc//2,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][4]=[N_ctrl_cc//2,N_ctrl_fc//2,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][5]=[N_ctrl_cc//2,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][6]=[N_ctrl_cc,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
	else:
		for i in range(1,len(vm2.comblist[0])):
			var_list[i-1][0]=[0,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][1]=[0,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][2]=[1,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][3]=[N_ctrl_cc//2,N_ctrl_fc,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][4]=[N_ctrl_cc//2,N_ctrl_fc//2,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][5]=[N_ctrl_cc//2,0,vm2.comblist[0][i],vm2.comblist[1][i]]
			var_list[i-1][6]=[N_ctrl_cc,0,vm2.comblist[0][i],vm2.comblist[1][i]]
	#===================================================================
	#   DATA table gen for parametric sweep
	#===================================================================
	#----- lateral stuffs: names --------
	netmap1.get_net('vf','vf',0,N_ctrl_fc-1,1) #for v2
	netmap1.get_net('vc','vc',0,N_ctrl_cc-1,1) #for v2

	#----- lateral stuffs: FCW values --------
	#with open(tb_dir+"tb_%dring%d_osc%d_FC%d.sp"%(ndrv,ncell,nstg,nfc),"w") as w_file:
	with open(tb_dir+"tb_"+designName+".sp","w") as w_file:
		for line in lines:
			if line[0:4]=='@L@W':
				line=line[2:len(line)-1]
				for ivt in range(len(var_list)):
					for ifcw in range(len(var_list[0])):
						netmap2=txt_mds.netmap()
						netmap2.get_net('f1',None,'d2o',N_ctrl_fc,var_list[ivt][ifcw][1])	 
						netmap2.get_net('c1',None,'d2o',N_ctrl_cc,var_list[ivt][ifcw][0])	 
						netmap2.get_net('vd',None,var_list[ivt][ifcw][2],var_list[ivt][ifcw][2],1)	 
						netmap2.get_net('tm',None,var_list[ivt][ifcw][3],var_list[ivt][ifcw][3],1)	 
						netmap2.printline(line,w_file)
						w_file.write('\n')	 
	
			else:
				netmap1.printline(line,w_file)

def gen_tb_pex(CF,Cc,Cf,PDK,finesim,tb_dir,format_dir,ncell,ndrv,nfc,nstg_start,nstg_end,nstg_step,vdd,temp,nper,design_name,sav):
	#=====================================================
	# model constants for trans simulation time calculation 
	#=====================================================
	CB=Cc*(ndrv+ncell)+Cf*nfc      


	vm1=txt_mds.varmap()   ###modify here!!
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
		vdd_min,vdd_max=txt_mds.mM(vdd)  #generate function of minMax step
		vdd.remove(vdd_min)
		temp_min,temp_max=txt_mds.mM(temp)
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
		netmap1=txt_mds.netmap()  #35
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
		vm2=txt_mds.varmap()
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
							netmap2=txt_mds.netmap()
							netmap2.get_net('f1',None,'d2o',N_ctrl_fc,var_list[ivt][ifcw][1])	 
							netmap2.get_net('c1',None,'d2o',N_ctrl_cc,var_list[ivt][ifcw][0])	 
							netmap2.get_net('vd',None,var_list[ivt][ifcw][2],var_list[ivt][ifcw][2],1)	 
							netmap2.get_net('tm',None,var_list[ivt][ifcw][3],var_list[ivt][ifcw][3],1)	 
							netmap2.printline(line,w_file)
							w_file.write('\n')	 
	
					#for j in range(1,len(vm2.comblist[0])):
					##	print('one line')
					#	#print vm2.comblist[0][j]
					#	netmap2=txt_mds.netmap()
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

#===================================================================
# gen_mkfile_pex: generates pex_makefile for pex hspice sim 
# receives inputs as a list
#===================================================================
def gen_mkfile_pex(formatDir,hspiceDir,hspiceResDir,tbDir,num_core,designNames,tech_node):
	r_file=open(formatDir+"form_pex_hspicesim.mk","r")

	netmap1=txt_mds.netmap()
	#----- stuffs for transient sim ------ 
	#----- get_net is okay since it's same as add_val when the variable is already in the list -------
	netmap1.get_net('TN',tech_node,None,None,1)   
	for designName in designNames:
		netmap1.get_net('s2','	cd',None,None,1)  #exclude ncell[0] name
		netmap1.get_net('Rd',hspiceResDir,None,None,1)  #exclude ncell[0] name
		netmap1.get_net('mp',None,None,num_core,1)   #number of core
		netmap1.get_net('Td',tbDir,None,None,1)  #exclude ncell[0] name
		netmap1.get_net('dn',designName,None,None,1)

	lines=list(r_file.readlines())
	with open(hspiceDir+"pex_hspicesim.mk","w") as w_file:
		for line in lines:
			netmap1.printline(line,w_file)	
	print('pex_hspicesim.mk ready')

def gen_result(result_dir,design_name,ncell,ndrv,nfc,nstg,num_meas,index,show,VDD,TEMP):

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
	
		rm[j]=txt_mds.resmap(1,num_words,index) #only one resmap per design	
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
				txt_mds.sort_via_1d_mult(TW[ivdd][itemp],FREQ[ivdd][itemp],IAVG[ivdd][itemp],K_ind[ivdd][itemp],K_ind_pex[ivdd][itemp])
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
