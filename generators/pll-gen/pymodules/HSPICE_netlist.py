##for HSPICE netlist
import HSPICE_mds

def gen_netlist(netlist_dir,format_dir,ncell,ndrv,nfc,nstg_start,nstg_end,nstg_step):
	vm1=HSPICE_mds.varmap()
	vm1.get_var('ncell',ncell,ncell,1)
	vm1.get_var('nstage',nstg_start,nstg_end,nstg_step)
	vm1.get_var('ndrv',ndrv,ndrv,1)
	vm1.cal_nbigcy()
	vm1.combinate()
	for i in range(1,len(vm1.comblist[0])):
		r_netlist=open(format_dir+"form_ring_osc.sp","r")
		lines=list(r_netlist.readlines())
	
		nstg=vm1.comblist[1][i]
		#print ("ntlst nstg=%d"%(nstg))
		npar=vm1.comblist[0][i]
		ndrv=vm1.comblist[2][i]
	
		netmap1=HSPICE_mds.netmap() 
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
		with open(netlist_dir+"%dring%d_osc%d_nf%d.sp"%(vm1.comblist[2][i],vm1.comblist[0][i],vm1.comblist[1][i],nfc),"w") as w_netlist:
			for line in lines:
				netmap1.printline(line,w_netlist)

