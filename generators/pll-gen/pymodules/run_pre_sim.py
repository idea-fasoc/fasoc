import txt_mds
import numpy as np

#====================================================================================
# DCO netlist generation
#====================================================================================
def gen_netlist(netlist_dir,format_dir,ncell,ndrv,nfc,nstg_start,nstg_end,nstg_step,wellpin,designName):
	vm1=txt_mds.varmap()
	vm1.get_var('ncell',ncell,ncell,1)
	vm1.get_var('nstage',nstg_start,nstg_end,nstg_step)
	vm1.get_var('ndrv',ndrv,ndrv,1)
	vm1.cal_nbigcy()
	vm1.combinate()
	for i in range(1,len(vm1.comblist[0])):
		if wellpin==0:
			r_netlist=open(format_dir+"form_ring_osc.sp","r")
		else:
			r_netlist=open(format_dir+"form_ring_osc_wellpin.sp","r")
		lines=list(r_netlist.readlines())
	
		nstg=vm1.comblist[1][i]
		#print ("ntlst nstg=%d"%(nstg))
		npar=vm1.comblist[0][i]
		ndrv=vm1.comblist[2][i]
	
		netmap1=txt_mds.netmap() 
		### enable voltages for CC,FC ###
		netmap1.get_net('vf',None,0,nstg-1,1)	
		netmap1.get_net('nf',None,0,nstg-1,1)	
		#netmap1.get_net('Vf','vf',None,0,nstg)	
		netmap1.get_net('Vf','vf',0,nstg-1,1) #for v2	
		netmap1.get_net('vc',None,0,nstg-1,1)	
		netmap1.get_net('nc',None,0,nstg-1,1)	
		#netmap1.get_net('Vc','vc',None,0,nstg)
		netmap1.get_net('Vc','vc',0,nstg-1,1) #for v2
		###driver before last	
		netmap1.get_net('id',None,1,nstg-1,1)
		netmap1.get_net('Dn','n',1,nstg-1,1)
		netmap1.get_net('Dp','p',1,nstg-1,1)
		netmap1.get_net('dp','p',2,nstg,1)
		netmap1.get_net('dn','n',2,nstg,1)
		###driver last
		netmap1.get_net('iD',None,nstg-1,nstg-1,1)
		netmap1.get_net('DN','n',nstg,nstg,1)
		netmap1.get_net('DP','p',nstg,nstg,1)
		if nstg%2==1:
			netmap1.get_net('dP','p',1,1,1)
			netmap1.get_net('dN','n',1,1,1)
		if nstg%2==0:
			netmap1.get_net('dP','n',1,1,1)
			netmap1.get_net('dN','p',1,1,1)
		###CC before last
		netmap1.get_net('ic',None,1,nstg-1,1)
		netmap1.get_net('ni',None,0,nstg-2,1)
		netmap1.get_net('In','n',1,nstg-1,1)
		netmap1.get_net('Ip','p',1,nstg-1,1)
		netmap1.get_net('Op','p',2,nstg,1)
		netmap1.get_net('On','n',2,nstg,1)
		###CC last
		netmap1.get_net('IC',None,nstg-1,nstg-1,1)
		netmap1.get_net('NI',None,nstg-1,nstg-1,1)
		netmap1.get_net('IN','n',nstg,nstg,1)
		netmap1.get_net('IP','p',nstg,nstg,1)
		if nstg%2==1:
			netmap1.get_net('OP','p',1,1,1)
			netmap1.get_net('ON','n',1,1,1)
		if nstg%2==0:
			netmap1.get_net('OP','n',1,1,1)
			netmap1.get_net('ON','p',1,1,1)
		#-----------FC-----------------	
		netmap1.get_net('if',None,0,nstg-1,1)			
		netmap1.get_net('fn',None,0,nstg-1,1)			
		netmap1.get_net('in','n',1,nstg,1)			
		netmap1.get_net('ip','p',1,nstg,1)			
	
		#-----------adding for parallel drv------
		for ip in range(1,ndrv):
			netmap1.add_val('id',None,1+ip*nstg,(ip+1)*nstg-1,1)
			netmap1.add_val('Dn','n',1,nstg-1,1)
			netmap1.add_val('Dp','n',1,nstg-1,1)
			netmap1.add_val('dp','n',2,nstg,1)
			netmap1.add_val('dn','n',2,nstg,1)
			netmap1.add_val('iD',None,(ip+1)*nstg-1,(ip+1)*nstg-1,1)
			netmap1.add_val('DN','n',nstg,nstg,1)
			netmap1.add_val('DP','p',nstg,nstg,1)
			if nstg%2==1:
				netmap1.add_val('dP','p',1,1,1)
				netmap1.add_val('dN','n',1,1,1)
			if nstg%2==0:
				netmap1.add_val('dP','n',1,1,1)
				netmap1.add_val('dN','p',1,1,1)
	
		#-----------adding for parallel CC------
		for ip in range(1,npar):
			#--------control voltages for CC----------	
			netmap1.add_val('vc',None,ip*nstg,(ip+1)*nstg-1,1)	
			netmap1.add_val('nc',None,ip*nstg,(ip+1)*nstg-1,1)	
			#netmap1.add_val('Vc','vc',None,ip,nstg)
			netmap1.add_val('Vc','vc',ip*nstg,(ip+1)*nstg-1,1)
			#--------CC cells----------	
			netmap1.add_val('ic',None,1+ip*nstg,(ip+1)*nstg-1,1)
			netmap1.add_val('ni',None,ip*nstg,(ip+1)*nstg-2,1)
			netmap1.add_val('In','n',1,nstg-1,1)
			netmap1.add_val('Ip','n',1,nstg-1,1)
			netmap1.add_val('On','n',2,nstg,1)
			netmap1.add_val('Op','n',2,nstg,1)
			#--------CC last------------			
			netmap1.add_val('IC',None,(ip+1)*nstg-1,(ip+1)*nstg-1,1)
			netmap1.add_val('NI',None,(ip+1)*nstg-1,(ip+1)*nstg-1,1)
			netmap1.add_val('IN','n',nstg,nstg,1)
			netmap1.add_val('IP','p',nstg,nstg,1)
			if nstg%2==1:
				netmap1.add_val('OP','p',1,1,1)
				netmap1.add_val('ON','n',1,1,1)
			if nstg%2==0:
				netmap1.add_val('OP','n',1,1,1)
				netmap1.add_val('ON','p',1,1,1)
		#-----------add parallel FC-------------
		for ip in range(1,nfc):
			#----------control voltages for FC--------
			netmap1.add_val('vf',None,ip*nstg,(ip+1)*nstg-1,1)	
			netmap1.add_val('nf',None,ip*nstg,(ip+1)*nstg-1,1)	
			#netmap1.add_val('Vf','vf',None,ip,nstg)
			netmap1.add_val('Vf','vf',ip*nstg,(ip+1)*nstg-1,1)  #for v2
			#----------FC cells---------------
			netmap1.add_val('if',None,ip*nstg,(ip+1)*nstg-1,1)			
			netmap1.add_val('fn',None,ip*nstg,(ip+1)*nstg-1,1)			
			netmap1.add_val('in','n',1,nstg,1)			
			netmap1.add_val('ip','p',1,nstg,1)
		with open(netlist_dir+designName+".sp","w") as w_netlist:
			for line in lines:
				netmap1.printline(line,w_netlist)

def gen_tb(hspiceModel,tb_dir,format_dir,ncell,ndrv,nfc,nstg,vdd,temp,fc_en_type,sim_time,corner_lib,designName,netlistDir):
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
	netmap1.get_net('dn',designName,None,None,1)
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

def gen_result(result_dir,ncell,ndrv,nfc,nstg,num_meas,index,show,VDD,TEMP,fc_en_type):

	print("parsing through simulation results")
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
	for j in range(len(ncell)-1): # for all designs
		i=j+1 #because ncell[0]=='ncell'
		num_var=nfc[i]*nstg[i]+ncell[i]*nstg[i]+1 # 1 is temper 
		num_words=num_var+num_meas+3 # 3: vdd temp alter#
	
		rm[j]=txt_mds.resmap(1,num_words,index) #only one resmap per design	
		dm[j]=[None]*4 #4 design params
		dm[j][0]=ndrv[i]
		dm[j][1]=ncell[i]
		dm[j][2]=nstg[i]
		dm[j][3]=nfc[i]
		fail_flag=0
		res_path=result_dir+'tb_%dndrv_%dncc_%dnstg_%dnfc_dp/'%(ndrv[i],ncell[i],nstg[i],nfc[i])    #removed the exception for FC==128
		#--- save the [j] of the ones that success try and use for later ---
		try: # HSPICE/2016
			print("parsing: "+res_path)
			for worker in os.listdir(res_path):
				if worker[0:6]=='worker' and worker[0:7]!='worker.':
					r_result=open(res_path+worker+'/tb_%dndrv_%dncc_%dnstg_%dnfc.mt0'%(ndrv[i],ncell[i],nstg[i],nfc[i]))
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
		except: # HSPICE/2017
			print("failed => parsing: "+result_dir+'../tb_%dndrv_%dncc_%dnstg_%dnfc.mt0'%(ndrv[i],ncell[i],nstg[i],nfc[i]))
			try:
				r_result=open(result_dir+'../tb_%dndrv_%dncc_%dnstg_%dnfc.mt0'%(ndrv[i],ncell[i],nstg[i],nfc[i])) # for testing purpose
				for line in r_result.readlines():
					if il>skip_line-1:
						words=line.split()
						for word in words:
							if word=='failed':
								fail_flag=1
							if iw<=num_words+index:
								rm[j].get_var(0,word)  #because only one result map per design
							else:
								rm[j].add(0,word)
							iw+=1
					il+=1
				set_tb=1
				il=0
				iw=1
				k+=1
				if fail_flag==0:
					result_exist.append(j)
				else:
					result_failed.append(j)
			except:
				print("failed parsing result for tb_%dndrv_%dncc_%dnstg_%dnfc.mt0"%(ndrv[i],ncell[i],nstg[i],nfc[i]))
				pass
	print (rm[0].vl[0][len(rm[0].vl[0])-4])
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
					if fc_en_type==1:
						fc=fc+float(rm[nd].vl[0][i][j])
					else: # inversed 
						fc=fc+(dm[nd][3]-float(rm[nd].vl[0][i][j]))
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

#==============================================================
# v3 receives only nominal frequency, but receive vdd,temp, use [0]
# it receives design parameters as dm
# only generates tbrf for the ones are in "result_exist"
#==============================================================
def gen_tbrf(PDK,format_dir,tbrf_dir,dm,freq,result_exist,vdd,temp):
	r_file=open(format_dir+"/form_tbrf_ring_osc.sp","r")
	lines=list(r_file.readlines())
	for nd in result_exist:
		N_fc=dm[nd][3]	  
		N_cc=dm[nd][1]	
		N_drv=dm[nd][0]
		N_stg=dm[nd][2]
		N_ctrl_fc=N_stg*N_fc
		N_ctrl_cc=N_stg*N_cc
		per_tmp=1/freq[nd][0][0] #nominal freq, nominal temp
		freq_tmp=freq[nd][0][0]
		netmap1=txt_mds.netmap()  #35
		netmap1.get_net('ff',None,freq_tmp,freq_tmp,1)
		netmap1.get_net('ht',None,50*per_tmp,50*per_tmp,1)
		netmap1.get_net('nd',None,N_drv,N_drv,1)
		netmap1.get_net('nm',None,N_cc,N_cc,1)
		netmap1.get_net('nt','sc',N_stg,N_stg,1)
		netmap1.get_net('nf',None,N_fc,N_fc,1)
		#----- only string -----------
		netmap1.get_net('PK',PDK,None,None,None)
		#----- lateral stuffs --------
		netmap1.get_net('vf','vf',0,N_ctrl_fc-1,1)
		netmap1.get_net('vc','vc',0,N_ctrl_cc-1,1)
		netmap1.get_net('vd',None,vdd[0],vdd[0],1)
		netmap1.get_net('tm',None,temp[0],temp[0],1)
		netmap1.get_net('f1',None,'d2o',N_ctrl_fc,N_ctrl_fc//2)
		netmap1.get_net('c1',None,'d2o',N_ctrl_cc,N_ctrl_cc//2)
		with open(tbrf_dir+"/tbrf_%dring%d_osc%d_fc%d.sp"%(N_drv,N_cc,N_stg,N_fc),"w") as w_file:
			for line in lines:
			        netmap1.printline(line,w_file)
			print("tbrf nstg=%d"%(N_stg))
def write_K(ncell,ndrv,nfc,Kg,Kg_err,dK,idK): 
	wrkg=open("./model/%ddco_K%d_val_fc%d.py"%(ndrv,ncell,nfc),"w")
	readf=open("./formats/dco_K_val.py","r")
	lines=list(readf.readlines())
	Kmap=txt_mds.netmap()
	Kmap.get_net('kg',None,Kg,Kg,1)
	Kmap.get_net('ke',None,Kg_err,Kg_err,1)
	Kmap.get_net('dK',None,dK[0],dK[0],1)
	Kmap.get_net('iK',None,idK[0],idK[0],1)
	for i in range(1,len(dK)):
		Kmap.add_val('dK',None,dK[i],dK[i],1)
		Kmap.add_val('iK',None,idK[i],idK[i],1)
	for line in lines:
		Kmap.printline(line,wrkg)

def write_Kpn(ncell,ndrv,nfc,Kpn,Ekpn): 
	wrkg=open("./model/%ddco_Kpn%d_val_fc%d.py"%(ndrv,ncell,nfc),"w")
	readf=open("./formats/form_Kpn.py","r")
	lines=list(readf.readlines())
	Edb=10*np.log10(1+Ekpn/100)
	#print ('Edb='),
	#print Edb
	Kmap=txt_mds.netmap()
	Kmap.get_net('Kp',None,Kpn,Kpn,1)
	Kmap.get_net('Ek',None,Ekpn,Ekpn,1)
	Kmap.get_net('Ed',None,float(Edb),float(Edb),1)
	for line in lines:
		Kmap.printline(line,wrkg)
def write_Kpn(ncell,ndrv,nfc,Kpn,Ekpn): 
	wrkg=open("./model/%ddco_Kpn%d_val_fc%d.py"%(ndrv,ncell,nfc),"w")
	readf=open("./formats/form_Kpn.py","r")
	lines=list(readf.readlines())
	Edb=10*np.log10(1+Ekpn/100)
	#print ('Edb='),
	#print Edb
	Kmap=txt_mds.netmap()
	Kmap.get_net('Kp',None,Kpn,Kpn,1)
	Kmap.get_net('Ek',None,Ekpn,Ekpn,1)
	Kmap.get_net('Ed',None,float(Edb),float(Edb),1)
	for line in lines:
		Kmap.printline(line,wrkg)
def write_Kpn(ncell,ndrv,nfc,Kpn,Ekpn): 
	wrkg=open("./model/%ddco_Kpn%d_val_fc%d.py"%(ndrv,ncell,nfc),"w")
	readf=open("./formats/form_Kpn.py","r")
	lines=list(readf.readlines())
	Edb=10*np.log10(1+Ekpn/100)
	#print ('Edb='),
	#print Edb
	Kmap=txt_mds.netmap()
	Kmap.get_net('Kp',None,Kpn,Kpn,1)
	Kmap.get_net('Ek',None,Ekpn,Ekpn,1)
	Kmap.get_net('Ed',None,float(Edb),float(Edb),1)
	for line in lines:
		Kmap.printline(line,wrkg)
def write_Kpn(ncell,ndrv,nfc,Kpn,Ekpn): 
	wrkg=open("./model/%ddco_Kpn%d_val_fc%d.py"%(ndrv,ncell,nfc),"w")
	readf=open("./formats/form_Kpn.py","r")
	lines=list(readf.readlines())
	Edb=10*np.log10(1+Ekpn/100)
	#print ('Edb='),
	#print Edb
	Kmap=txt_mds.netmap()
	Kmap.get_net('Kp',None,Kpn,Kpn,1)
	Kmap.get_net('Ek',None,Ekpn,Ekpn,1)
	Kmap.get_net('Ed',None,float(Edb),float(Edb),1)
	for line in lines:
		Kmap.printline(line,wrkg)

def gen_resultrf(ncell,ndrv,nfc,stg_start,stg_swp,Ncf,fcidx,num_meas,index,freq_cc,len_ncell):
	skip_line=2   #default titles
	num_var=nfc+ncell+1
	num_words=num_var+num_meas+1   #+1 is +alter# index not included
	il=0
	iw=1
	k=0
	icc=0
	n_cc=0
	rm=txt_mds.resmap(stg_swp*3,num_words,index)
	#dvmap=[[0]*5]*(stg_swp*3)     # 3 is the number of 'cc' sweep
	dvmap=[]
	set_tb=0
	cnt=0
	for j in range(stg_swp):   #netlist
		for cc, freq in freq_cc[j].iteritems(): #testbench
			try:
				r_result=open('./HSPICE/DUMPrf_result/tbrf_%dring%d_osc%d_cc%d.mp0'%(ndrv,ncell,stg_start+j,cc),'r')
				dvmap.append([])
				dvmap[cnt].append(ndrv)
				dvmap[cnt].append(ncell)
				dvmap[cnt].append(stg_start+j)
				dvmap[cnt].append(cc)
				dvmap[cnt].append(nfc)
				dvmap[cnt].append(freq)
				#================================================================================================
				#    reading values, storing on rm.map 
				#================================================================================================
				for line in r_result.readlines():
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								if iw<num_words+index+1:
									rm.get_var(cnt,word)
								#	print("got %s"%(word))
								else:
									rm.add(cnt,word)
								iw+=1
					elif il>skip_line+round(float(num_words)/3+float(1)/3)-1:    #change here!!!
						words=line.split()
						for word in words:
							rm.add(cnt,word)
							iw+=1
					il+=1
				set_tb=1
				il=0
				iw=1
				k+=1
				cnt+=1
			except: 
				pass
			set_tb=0
			k=0
		
	fc=0
	cc=0
	freq_per=0
	kacc=0
	kavg=0
	kidx=0
	icc=0	
	cc_d=0
	fc_d=0
	Kc_d=0
	Kc=0    ##const
	Nstg=0    
	rm2=txt_mds.resmap(stg_swp*3,10,0)   #result map for cleaner data
#	for ntb in range(stg_swp):   #for all netlist
	#================================================================================================
	#    organizing data in rm.map and restoring it on rm2.map 
	#================================================================================================
	for ntb in range(len(dvmap)):   #for all mp0
		Nstg=dvmap[ntb][2] 
#		for Cc, freq in freq_cc[ntb-1].iteritems():
		rm2.get_var(ntb,'FC')
		rm2.get_var(ntb,'CC')
		rm2.get_var(ntb,'TW')
		rm2.get_var(ntb,'pn1meg')
		rm2.get_var(ntb,'perj')
		rm2.get_var(ntb,'rmsj')
#		rm2.get_var(ntb,'freq')
		rm2.get_var(ntb,'Kpn')
		rm2.get_var(ntb,'Kjt')
		rm2.get_var(ntb,'freq')
		rm2.get_var(ntb,'Nstg')
		#print ("ntb=%d"%(ntb))
		#for j in range(len(rm.vl[ntb+icc][0])):       # for all tuning word(testbench)
		for i in range(len(rm.vr)):       # for all variables
			if rm.vr[i][0:2]=='vf':   ###here!!!!
				fc=fc+float(rm.vl[ntb][i][icc])
			if rm.vr[i][0:2]=='vc':   ###here!!!!
				cc=cc+float(rm.vl[ntb][i][icc])
			if rm.vr[i][0:6]=='pn1meg':
				pn1meg=float(rm.vl[ntb][i][icc])	
			if rm.vr[i][0:4]=='perj':
				perj=float(rm.vl[ntb][i][icc])
			if rm.vr[i][0:4]=='rmsj':
				rmsj=float(rm.vl[ntb][i][icc])
		rm2.add(ntb,fc)			
		rm2.add(ntb,cc)			
		rm2.add(ntb,cc*Ncf+fc)			
		rm2.add(ntb,pn1meg)			
		rm2.add(ntb,perj)
		rm2.add(ntb,rmsj)
#		rm2.add(ntb,freq)
		#rm2.add(ntb,(10**(pn1meg/20))/freq/freq)
		#rm2.add(ntb,pn1meg+10*math.log10((stg_start+ntb)**2/(ndrv+cc)))
		rm2.add(ntb,10**(pn1meg/10)*(Nstg)**2.9/(ndrv+cc))   #Kpn
		#rm2.add(ntb,10**(pn1meg/10)/(freq**2)*(ndrv+cc))
		rm2.add(ntb,rmsj**2*(ndrv+cc)**2/Nstg)   #Kjitter
		rm2.add(ntb,dvmap[ntb][5])   #frequency
		rm2.add(ntb,Nstg)
		fc=0
		cc=0
		#print('icc=%d'%(icc))
	#	icc+=1
	#icc=0
	i=0
	#=======================================================================
	#  removing blanks in rm2 (due to the rf test errors...)
	#=======================================================================				
	for j in rm2.vl:
		if j[0]==None:
			i+=1
	
	for k in range(i):
		rm2.vl.remove([None,None,None,None,None,None,None,None])

	for k in range(stg_swp):
		for i in rm2.vl:
			if i[7][0]==stg_start+k:
				print (i)
	#=======================================================================
	# print the constants Kpn, Kjt 
	#=======================================================================				
	print('frequency,perJ,rmsJ,Nstg=')
	for j in rm2.vl:
		print (j[8])
		print (j[4][0])
		print (j[5][0])
		print (j[9])	
	#print rm2.vl
	print('end result_rf')

#================================================================================================
#    function for reading .pn0 file 
#================================================================================================
def gen_printpn(ncell,ndrv,nfc,stg_start,stg_swp,Kg,freq_cc):
	skip_line=3   #default titles
	num_words=4   # freq / phase noise 
	il=0
	iw=1
	k=0
	icc=0
	n_cc=0
	index=0
	rm=txt_mds.resmap(stg_swp*3,num_words,index)
	#dvmap=[[0]*5]*(stg_swp*3)     # 3 is the number of 'cc' sweep
	dvmap=[]  #design-variable map
	set_tb=0
	cnt=0
	#================================================================================================
	#    reading results with name of "tbrf_XXringXX_oscX(X)_ccX.printpn0 
	#================================================================================================
	for j in range(stg_swp):   #netlist
		for cc, freq in freq_cc[j].iteritems(): #testbench
			try:
				r_result=open('./HSPICE/DUMPrf_result/tbrf_%dring%d_osc%d_cc%d.printpn0'%(ndrv,ncell,stg_start+j,cc),'r')
				#print('found tbrf_%dring%d_osc%d_cc%d.printpn0'%(ndrv,ncell,stg_start+j,cc))
				dvmap.append([])
				dvmap[cnt].append(ndrv)         #0
				dvmap[cnt].append(ncell)        #1
				dvmap[cnt].append(stg_start+j)  #2
				dvmap[cnt].append(cc)		#3
				dvmap[cnt].append(nfc)		#4
				dvmap[cnt].append(freq)		#5
				#================================================================================================
				#    reading values and store in rm.map 
				#================================================================================================
				for line in r_result.readlines():
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								if iw<num_words+index+1:
									rm.get_var(cnt,word)
								#	print("got %s"%(word))
								else:
									rm.add(cnt,word)
								iw+=1
					elif il>skip_line:    #change here!!!
						words=line.split()
						for word in words:
							rm.add(cnt,word)
							iw+=1
					il+=1
				set_tb=1
				il=0
				iw=1
				k+=1
				cnt+=1
			except:
				print('failed to find tbrf_%dring%d_osc%d_cc%d.printpn0'%(ndrv,ncell,stg_start+j,cc))
			set_tb=0
			k=0
		
		
	print('printpn dvmap='),
	print (dvmap)

	#print rm.vr
	#print rm.vl[0]
	#print rm.vl[1]
	#print freq_cc
		
	fc=0
	cc=0
	freq_per=0
	freq=0
	freq_d=0
	logDF=0
	kacc=0
	kavg=0
	kidx=0
	icc=0	
	cc_d=0
	fc_d=0
	Kc_d=0
	Kc=0    ##const
	Nstg=0 
	PN_slope=[None]*len(dvmap)
	PN_last=[]
	Fo_Fc_PN=[None]*len(dvmap)
	Kpn_last=[]
	PN_d=0
	logDPN=0 
	f0=0
	Fc_flag=0
	#================================================================================================
	#    organizing values from rm.map and re-store at rm2.map  
	#================================================================================================
	rm2=txt_mds.resmap(len(dvmap),4,0)   #result map for cleaner data
	for ntb in range(len(dvmap)):   #for all mp0
		Nstg=dvmap[ntb][2]
		NI=dvmap[ntb][0]+dvmap[ntb][3]
		rm2.get_var(ntb,'Ndrv+Nc')
		rm2.get_var(ntb,'Nstg')
		rm2.get_var(ntb,'PN')
		rm2.get_var(ntb,'freq')  #frequency offset
		PN_slope[ntb]=[]
		Fo_Fc_PN[ntb]=[]
		for j in range(len(rm.vl[0][0])):        # for all values
			for i in range(len(rm.vr)):       # for all variables
				if rm.vr[i][0:5]=='HERTZ':   ###here!!!!
					freq=float(rm.vl[ntb][i][j])
				if rm.vr[i][0:2]=='BP':   ###here!!!!
					PN=float(rm.vl[ntb][i][j])
			rm2.add(ntb,NI)			
			rm2.add(ntb,Nstg)			
			rm2.add(ntb,10**(PN/10))			
			rm2.add(ntb,freq)
			if j!=0:
				logDF=np.log10(freq)-np.log10(freq_d)			
				logDPN=PN-PN_d
				PN_slope[ntb].append(freq)
				PN_slope[ntb].append(logDPN/logDF)
				#======= find corner frequency and PN at that point ======
				if Fc_flag==0 and logDPN/logDF>-25:
					Fo_Fc_PN[ntb].append(dvmap[ntb][5])
					Fo_Fc_PN[ntb].append(freq)
					Fo_Fc_PN[ntb].append(PN)
					Fc_flag=1 
			if j==len(dvmap)-1:
				PN_last.append(PN)
				f0=dvmap[ntb][5]  #center frequency
				#print NI,Nstg,f0
				#Kpn_last.append(10**(PN/10)*(Nstg)**3/(NI))
				Kpn_last.append(10**(PN/10)*float(NI**2)/(f0**3))


			freq_d=freq
			PN_d=PN	
		freq_d=0
		PN_d=0
		Fc_flag=0
	
	print('PN_slope='),
	print (PN_slope[0])
	#print dvmap
	#================================================================================================
	#    calculate Jitter from fc, PN  
	#================================================================================================
	print('Fo_Fc_PN=')
	for i in range(len(Fo_Fc_PN)):
		print (Fo_Fc_PN[i])
		Fout=Fo_Fc_PN[i][0]
		Fcorner=Fo_Fc_PN[i][1]
		PNcorner=Fo_Fc_PN[i][2]
			




	s_dvmap=[0]*len(dvmap)
	s_PN_last=[0]*len(PN_last)
	txt_mds.sort_via(dvmap,PN_last,2,0)
	txt_mds.sort_via(dvmap,Kpn_last,2,0)
	Kpn_avg=sum(Kpn_last)/len(Kpn_last)
	Emax=max(abs(max(Kpn_last)-Kpn_avg),abs(min(Kpn_last)-Kpn_avg))
	Emax=Emax/Kpn_avg*100
	print ('Kpn_avg=%e Errmax=%e%%'%(Kpn_avg,Emax))
	print (freq_cc)
	print('end')
	return Kpn_avg,Emax

def tb_verilog_gen(formatDir,tbDir,relBW,Kp_o_Ki,Fref,dFf,dFc,FCW,Fbase,ndrv,ncc,nfc,nstg):
	Kp=relBW*Fref/dFf
	Ki=Kp/Kp_o_Ki

	nm1=txt_mds.netmap()
	nm1.get_net('ns',None,nstg,nstg,1)
	nm1.get_net('nc',None,ncc,ncc,1)
	nm1.get_net('nf',None,nfc,nfc,1)
	nm1.get_net('nd',None,ndrv,ndrv,1)
	nm1.get_net('fb',None,Fbase,Fbase,1)
	nm1.get_net('dc',None,dFc,dFc,1)
	nm1.get_net('df',None,dFf,dFf,1)
	nm1.get_net('FR',None,Fref,Fref,1)
	nm1.get_net('Kp',None,Kp,Kp,1)
	nm1.get_net('Ki',None,Ki,Ki,1)
	nm1.get_net('FW',None,FCW,FCW,1)
	nm1.get_net('CT',None,30,30,1) # coarse_lock_threshold
	nm1.get_net('CC',None,10,10,1) # coarse_lock_count
	nm1.get_net('FT',None,10,10,1) # fine_lock_threshold
	nm1.get_net('FC',None,30,30,1) # fine_lock_count

	r_TB=open(formatDir+'form_TB_PLL_CONTROLLER_TDC_COUNTER.sv','r')
	w_TB=open(tbDir+'TB_PLL_CONTROLLER_TDC_COUNTER.sv','w')

	lines=list(r_TB.readlines())
	for line in lines:
		nm1.printline(line,w_TB)
	print('verilog testbench ready')
#===================================================================
# v2 takes every design param as lists
# all the lists should have the same length! 
#===================================================================
def gen_mkfile_v2(format_dir,hspiceDir,ncell,ndrv,nfc,nstg,rf_ready,num_core,result_exist,tech_node):
	r_file=open(format_dir+"/form_hspicesim.mk","r")
	#w_file=open("./Makefile","w")

	#print (result_exist)
	netmap1=txt_mds.netmap()
	#----- stuffs for transient sim -------
	netmap1.get_net('TN',tech_node,None,None,1)   #number of core
	netmap1.get_net('s2','	cd',None,None,len(ncell)-1)  #exclude ncell[0] name
	netmap1.get_net('tn',tech_node,None,None,len(ncell)-1)   #number of core
	netmap1.get_net('mp',None,num_core,num_core,1)   #number of core
	netmap1.get_net('md',None,ndrv[1],ndrv[1],1)   #starting from 1 since comblist[0] is name
	netmap1.get_net('mt',None,ncell[1],ncell[1],1)
	netmap1.get_net('nt','sc',nstg[1],nstg[1],1)
	netmap1.get_net('nf',None,nfc[1],nfc[1],1)
	#----- stuffs for rf sim -------
	if rf_ready==1:
		if 0 in result_exist:
			netmap1.get_net('s1','	cd',None,None,len(result_exist))
			netmap1.get_net('rm',None,num_core,num_core,1)   #number of core
			netmap1.get_net('rd',None,ndrv[1],ndrv[1],1)
			netmap1.get_net('mr',None,ncell[1],ncell[1],1)
			netmap1.get_net('nr','sc',nstg[1],nstg[1],1)
			netmap1.get_net('Nf',None,nfc[1],nfc[1],1)     
	for i in range(2,len(ncell)):
		#----- stuffs for transient sim -------
		netmap1.add_val('mp',None,num_core,num_core,1)   #number of core
		netmap1.add_val('md',None,ndrv[i],ndrv[i],1)
		netmap1.add_val('mt',None,ncell[i],ncell[i],1)
		netmap1.add_val('nt','sc',nstg[i],nstg[i],1)
		netmap1.add_val('nf',None,nfc[i],nfc[i],1)
		#----- stuffs for rf sim -------
		if rf_ready==1:
			if i-1 in result_exist:
				print ("got net %d"%(i-1))
				netmap1.add_val('rm',None,num_core,num_core,1)   #number of core
				netmap1.add_val('rd',None,ndrv[i],ndrv[i],1)
				netmap1.add_val('mr',None,ncell[i],ncell[i],1)
				netmap1.add_val('nr','sc',nstg[i],nstg[i],1)
				netmap1.add_val('Nf',None,nfc[i],nfc[i],1)     

	lines=list(r_file.readlines())
	with open(hspiceDir+"/hspicesim.mk","w") as w_file:
		for line in lines:
			if rf_ready==1:
				if line[0:3]=='#@@':
					line=line[1:len(line)]
				if line[0:2]=='#1':
					line=line[3:len(line)]
			netmap1.printline(line,w_file)	
	print(hspiceDir+'hspicesim.mk ready')
