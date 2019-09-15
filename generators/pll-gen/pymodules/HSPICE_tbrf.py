#==== tbrf generation =======

import HSPICE_mds
#==============================================================
# v3 receives only nominal frequency, but receive vdd,temp, use [0]
# it receives design parameters as dm
# only generates tbrf for the ones are in "result_exist"
#==============================================================
def gen_tbrf_v3(PDK,format_dir,tbrf_dir,dm,freq,result_exist,vdd,temp):
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
		netmap1=HSPICE_mds.netmap()  #35
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


#==============================================================
# v2 receives only nominal frequency
# it receives design parameters as lists
# only generates tbrf for the ones are in "result_exist"
#==============================================================
def gen_tbrf_v2(ncell,ndrv,nfc,nstg,freq,result_exist):
	r_file=open("./formats/form_tbrf_ring_osc.sp","r")
	lines=list(r_file.readlines())
	print ("result_exist"),
	print (result_exist)
	for nd in result_exist:
		i=nd+1 #ncell[0]='ncell'
		NCC=ncell[i]
		NDRV=ndrv[i]
		NFC=nfc[i]
		NSTG=nstg[i]
		N_ctrl_fc=NSTG*NFC
		N_ctrl_cc=NSTG*NCC
		#print freq[nd]
		per_tmp=1/freq[nd][0][0] #nominal freq, nominal temp
		freq_tmp=freq[nd][0][0]
		#print per_tmp 
		netmap1=HSPICE_mds.netmap()  #35
		netmap1.get_net('ff',None,freq_tmp,freq_tmp,1)
		netmap1.get_net('ht',None,50*per_tmp,50*per_tmp,1)
		netmap1.get_net('nd',None,NDRV,NDRV,1)
		netmap1.get_net('nm',None,NCC,NCC,1)
		netmap1.get_net('nt','sc',NSTG,NSTG,1)
		netmap1.get_net('nf',None,NFC,NFC,1)
		#----- lateral stuffs --------
		netmap1.get_net('vf','vf',0,N_ctrl_fc-1,1)
		netmap1.get_net('vc','vc',0,N_ctrl_cc-1,1)
		netmap1.get_net('f1',None,'d2o',N_ctrl_fc,N_ctrl_fc//2)
		netmap1.get_net('c1',None,'d2o',N_ctrl_cc,N_ctrl_cc//2)
		with open("./HSPICE/TBrf_v2/tbrf_%dring%d_osc%d_fc%d.sp"%(NDRV,NCC,NSTG,NFC),"w") as w_file:
			for line in lines:
			        netmap1.printline(line,w_file)
			print("tbrf nstg=%d"%(NSTG))
		


def gen_tbrf(ncell,ndrv,nfc,nstg_start,nstg_end,nstg_step,freq_cc,fcidx):

	vm1=HSPICE_mds.varmap()   ###modify here!!
	vm1.get_var('ncell',ncell,ncell,1)
	vm1.get_var('nstage',nstg_start,nstg_end,nstg_step)
	vm1.get_var('ndrive',ndrv,ndrv,1)
	vm1.get_var('nfc',nfc,nfc,1)
	vm1.cal_nbigcy()
	vm1.combinate()
	num_var=1

	r_file=open("./formats/form_tbrf_ring_osc.sp","r")
	lines=list(r_file.readlines())
	
	
	for i in range(1,len(vm1.comblist[0])):
		for cc, freq in freq_cc[i-1].iteritems():
			per=1/freq
			#print per 
			#w_file=open("./HSPICE/TBrf/tbrf_%dring%d_osc%d_cc%d_nf%d.sp"%(vm1.comblist[2][i],vm1.comblist[0][i],vm1.comblist[1][i],cc,nfc),"w")
			netmap1=HSPICE_mds.netmap()  #35
			netmap1.get_net('ff',None,freq,freq,1)
			netmap1.get_net('ht',None,50*per,50*per,1)
			netmap1.get_net('nd',None,vm1.comblist[2][i],vm1.comblist[2][i],1)
			netmap1.get_net('nm',None,vm1.comblist[0][i],vm1.comblist[0][i],1)
			netmap1.get_net('nt','sc',vm1.comblist[1][i],vm1.comblist[1][i],1)
			netmap1.get_net('nf',None,vm1.comblist[3][i],vm1.comblist[3][i],1)
			#netmap1.get_net('nf',None,nfc,nfc,1)
			#----- lateral stuffs --------
			netmap1.get_net('vf','vf',0,nfc-1,1)
			netmap1.get_net('vc','vc',0,ncell-1,1)
			netmap1.get_net('f1',None,'d2o',nfc,fcidx)
			netmap1.get_net('c1',None,'d2o',ncell,cc)
			with open("./HSPICE/TBrf/tbrf_%dring%d_osc%d_cc%d.sp"%(vm1.comblist[2][i],vm1.comblist[0][i],vm1.comblist[1][i],cc),"w") as w_file:
				for line in lines:
				        netmap1.printline(line,w_file)
				print("tbrf nstg=%d"%(i+nstg_start-1))
