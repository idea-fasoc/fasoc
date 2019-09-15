#### Makefile generation ####
import HSPICE_mds

#===================================================================
# gen_mkfile_pex: generates pex_makefile for pex hspice sim 
# receives inputs as a list
#===================================================================
def gen_mkfile_pex(formatDir,hspiceDir,hspiceResDir,tbDir,nccList,ndrvList,nfcList,nstgList,num_core):
	r_file=open(formatDir+"form_pex_hspicesim.mk","r")

	netmap1=HSPICE_mds.netmap()
	#----- stuffs for transient sim ------ 
	#----- get_net is okay since it's same as add_val when the variable is already in the list -------
	for i in range (1,len(nccList)):
		netmap1.get_net('s2','	cd',None,None,1)  #exclude ncell[0] name
		netmap1.get_net('Rd',hspiceResDir,None,None,1)  #exclude ncell[0] name
		netmap1.get_net('mp',None,None,num_core,1)   #number of core
		netmap1.get_net('Td',tbDir,None,None,1)  #exclude ncell[0] name
		netmap1.get_net('md',None,None,ndrvList[i],1)   #starting from 1 since comblist[0] is name
		netmap1.get_net('mt',None,None,nccList[i],1)
		netmap1.get_net('nt','sc',None,nstgList[i],1)
		netmap1.get_net('nf',None,None,nfcList[i],1)

	lines=list(r_file.readlines())
	with open(hspiceDir+"pex_hspicesim.mk","w") as w_file:
		for line in lines:
			netmap1.printline(line,w_file)	
	print('pex_hspicesim.mk ready')
#===================================================================
# v2 takes every design param as lists
# all the lists should have the same length! 
#===================================================================
def gen_mkfile_v2(format_dir,hspiceDir,ncell,ndrv,nfc,nstg,rf_ready,num_core,result_exist):
	r_file=open(format_dir+"/form_hspicesim.mk","r")
	#w_file=open("./Makefile","w")

	#print (result_exist)
	netmap1=HSPICE_mds.netmap()
	#----- stuffs for transient sim -------
	netmap1.get_net('s2','	cd',None,None,len(ncell)-1)  #exclude ncell[0] name
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
	print('hspicesim.mk ready')

def gen_mkfile1(ncell_1,ndrv_1,nfc_1,stg_start,stg_end,freq_cc_1,rf_ready):
	r_file=open("./formats/form_Makefile","r")
	vm1=HSPICE_mds.varmap()
	vm1.get_var('ncell',ncell_1,ncell_1,1)
	vm1.get_var('nstage',stg_start,stg_end,1)
	vm1.get_var('ndrv',ndrv_1,ndrv_1,1)
	vm1.cal_nbigcy()
	vm1.combinate()
	lines=list(r_file.readlines())
	with open("./Makefile","w") as w_file:
		for line in lines:
			if line[0:3]=='s@@':
				line=line[1:len(line)]
				for i in range(stg_start,stg_end+1):
					netmap1=HSPICE_mds.netmap()
					#----for 1----
					netmap1.get_net('s2','	cd',None,None,1)
					netmap1.get_net('md',None,ndrv_1,ndrv_1,1)
					netmap1.get_net('mt',None,ncell_1,ncell_1,1)
					netmap1.get_net('nt','sc',i,i,1)
					netmap1.get_net('nf',None,nfc_1,nfc_1,1)
					netmap1.printline(line,w_file)
			elif line[0:3]=='#@@'and rf_ready==1:
				line=line[1:len(line)]
				for i in range(stg_start,stg_end+1):
					for cc,freq in freq_cc_1[i-stg_start].iteritems():    # for all cc
						netmap1=HSPICE_mds.netmap()
						netmap1.get_net('s1','	cd',None,None,1)
						netmap1.get_net('rd',None,ndrv_1,ndrv_1,1)
						netmap1.get_net('mr',None,ncell_1,ncell_1,1)
						netmap1.get_net('nr','sc',i,i,1)
						netmap1.get_net('cc',None,cc,cc,1)
						netmap1.printline(line,w_file)
			elif line[0:2]=='#1':
				line=line[3:len(line)]
				w_file.write(line)
			else:
				w_file.write(line)
	print('mkfile ready')




def gen_mkfile3(ncell_1,ncell_2,ncell_3,ndrv_1,ndrv_2,ndrv_3,nfc_1,nfc_2,nfc_3,stg_start,stg_end,freq_cc_1,freq_cc_2,freq_cc_3,rf_ready):
	r_file=open("./formats/form_Makefile","r")
	vm1=HSPICE_mds.varmap()
	vm1.get_var('ncell',ncell_1,ncell_1,1)
	vm1.get_var('nstage',stg_start,stg_end,1)
	vm1.get_var('ndrv',ndrv_1,ndrv_1,1)
	vm1.cal_nbigcy()
	vm1.combinate()
	vm2=HSPICE_mds.varmap()
	vm2.get_var('ncell',ncell_2,ncell_2,1)
	vm2.get_var('nstage',stg_start,stg_end,1)
	vm2.get_var('ndrv',ndrv_2,ndrv_2,1)
	vm2.cal_nbigcy()
	vm2.combinate()
	vm3=HSPICE_mds.varmap()
	vm3.get_var('ncell',ncell_3,ncell_3,1)
	vm3.get_var('nstage',stg_start,stg_end,1)
	vm3.get_var('ndrv',ndrv_3,ndrv_3,1)
	vm3.cal_nbigcy()
	vm3.combinate()
	lines=list(r_file.readlines())
	with open("./Makefile","w") as w_file:
		for line in lines:
			if line[0:3]=='s@@':
				line=line[1:len(line)]
				for i in range(stg_start,stg_end+1):
					netmap1=HSPICE_mds.netmap()
					#----for 1----
					netmap1.get_net('s2','	cd',None,None,1)
					netmap1.get_net('md',None,ndrv_1,ndrv_1,1)
					netmap1.get_net('mt',None,ncell_1,ncell_1,1)
					netmap1.get_net('nt','sc',i,i,1)
					netmap1.get_net('nf',None,nfc_1,nfc_1,1)
					#----for 2----
					netmap1.add_val('s2','	cd',None,None,1)
					netmap1.add_val('md',None,ndrv_2,ndrv_2,1)
					netmap1.add_val('mt',None,ncell_2,ncell_2,1)
					netmap1.add_val('nt','sc',i,i,1)
					netmap1.add_val('nf',None,nfc_2,nfc_2,1)
					#----for 3----
					netmap1.add_val('s2','	cd',None,None,1)
					netmap1.add_val('md',None,ndrv_3,ndrv_3,1)
					netmap1.add_val('mt',None,ncell_3,ncell_3,1)
					netmap1.add_val('nt','sc',i,i,1)
					netmap1.add_val('nf',None,nfc_3,nfc_3,1)
					netmap1.printline(line,w_file)
			elif line[0:3]=='#@@'and rf_ready==1:
				line=line[1:len(line)]
				for i in range(stg_start,stg_end+1):
					for cc,freq in freq_cc_1[i-1].iteritems():    # for all cc
						netmap1=HSPICE_mds.netmap()
						netmap1.get_net('s1','	cd',None,None,1)
						netmap1.get_net('rd',None,ndrv_1,ndrv_1,1)
						netmap1.get_net('mr',None,ncell_1,ncell_1,1)
						netmap1.get_net('nr','sc',i,i,1)
						netmap1.get_net('cc',None,cc,cc,1)
						netmap1.printline(line,w_file)
					for cc,freq in freq_cc_2[i-1].iteritems():    # for all cc
						netmap1=HSPICE_mds.netmap()
						netmap1.get_net('s1','	cd',None,None,1)
						netmap1.get_net('rd',None,ndrv_2,ndrv_2,1)
						netmap1.get_net('mr',None,ncell_2,ncell_2,1)
						netmap1.get_net('nr','sc',i,i,1)
						netmap1.get_net('cc',None,cc,cc,1)
						netmap1.printline(line,w_file)
					for cc,freq in freq_cc_3[i-1].iteritems():    # for all cc
						netmap1=HSPICE_mds.netmap()
						netmap1.get_net('s1','	cd',None,None,1)
						netmap1.get_net('rd',None,ndrv_3,ndrv_3,1)
						netmap1.get_net('mr',None,ncell_3,ncell_3,1)
						netmap1.get_net('nr','sc',i,i,1)
						netmap1.get_net('cc',None,cc,cc,1)
						netmap1.printline(line,w_file)
			elif line[0:2]=='#1':
				line=line[3:len(line)]
				w_file.write(line)
			else:
				w_file.write(line)
	print('mkfile ready')




