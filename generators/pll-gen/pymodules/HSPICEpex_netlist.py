#=====================================================================================================
#  generates 2 outputs
#	1. dco_Nstg.pex.netlist: with modified input sequence
#	2. pex_XringX_oscX.sp: netlist wrapper with all the voltage source name defined
#=====================================================================================================
import HSPICE_mds
import re

def gen_pex_netlist(raw_pex_dir,netlist_dir,format_dir,ncc,ndrv,nfc,nstg,ninterp,design_name):
	r_netlist=open(format_dir+"/form_pex_ring_osc.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=HSPICE_mds.netmap() 
	### include pex.netlist ###
	netmap1.get_net('dn',design_name,None,None,None)	
	### enable voltages for CC,FC ###
	netmap1.get_net('vf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('nf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('Vf','vf',0,nfc*nstg-1,1) #for v2	
	netmap1.get_net('vc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('nc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('Vc','vc',0,ncc*nstg-1,1) #for v2

	### write the pex.netlist inputs ### 
	netmap1.get_net('cc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('fc',None,0,nfc*nstg-1,1)	
	netmap1.get_net('po',None,0,ninterp*nstg-1,1)	
	netmap1.get_net('no',None,0,ninterp*nstg-1,1)	
	netmap1.get_net('pt',None,0,nstg-1,1) # for test purpose	
	netmap1.get_net('nt',None,0,nstg-1,1) # for test purpose	
	netmap1.get_net('DN',design_name,None,None,None)	

	for line in lines:
		netmap1.printline(line,w_netlist)

	w_netlist.close()
	r_netlist.close()


	r_ref_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","r")
	r_raw_netlist=open(raw_pex_dir+"/"+design_name+".pex.netlist","r")
	w_raw_netlist=open(netlist_dir+"/"+design_name+".pex.netlist","w")
	raw_lines=list(r_raw_netlist.readlines())
	ref_lines=list(r_ref_netlist.readlines())
	#print(ref_lines)

	### copies the first defined instant into inst_def for matching input sequence of pex.netlist###
	inst_def=[]
	inst_start=0
	for line in ref_lines:
		if inst_start==1 and line[0:1]!='+':
			inst_start=0	
		if inst_start==1 and line[0:1]=='+':
			inst_def.append(line)
		if line[0:2]=='xi':
			inst_start=1	
			inst_def.append(line[4:len(line)])
			print('found instance')
			#print(inst_def)

	#print(inst_def)

	
	### replace the inputs with inst_def on pex.netlist###
	inst_start=0
	for line in raw_lines:
		if inst_start==1 and line[0:1]!='+':
			inst_start=0	
			w_raw_netlist.write(line)	
		elif line[0:7]=='.subckt':
			inst_start=1	
			print('found subckt')
			line='.subckt '+ design_name + ' ' + inst_def[0]
			w_raw_netlist.write(line)	
			for ll in range(1,len(inst_def)-1):  #exclude + dco_8stg
				w_raw_netlist.write(inst_def[ll])	
		elif line[0:8]=='.include':
			line='.include '+ '"./../pex_NETLIST/'+line[10:len(line)]
			w_raw_netlist.write(line)	
		elif inst_start==0:		
			w_raw_netlist.write(line)	
			
























 					 
		

