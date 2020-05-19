#=====================================================================================================
#  generates 2 outputs
#	1. dco_Nstg.pex.netlist: with modified input sequence
#	2. pex_XringX_oscX.sp: netlist wrapper with all the voltage source name defined
#=====================================================================================================
import HSPICE_mds
import HSPICE_mds2
import re
import subprocess as sp



def gen_pll_pex_netlist(switch,buf,PD,raw_pex_dir,design_name,netlist_dir,format_dir,input_array,vdd):
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

	
	netmap1=HSPICE_mds.netmap() 
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
	nm2=HSPICE_mds.netmap()	
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
	

def gen_pll_pre_netlist2(switch,buf,PD,raw_sp_dir,design_name,netlist_dir,format_dir,input_array,vdd):
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
	
	netmap1=HSPICE_mds.netmap() 
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
	nm2=HSPICE_mds.netmap()	
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


def gen_pll_prepex_netlist(design_name,netlist_dir,format_dir,input_array,vdd):
	r_netlist=open(format_dir+"/ignore_form_wrapped_test_synth_pll.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=HSPICE_mds.netmap() 
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




def gen_pex_netlist(raw_pex_dir,netlist_dir,format_dir,ncc,ndrv,nfc,nstg,ninterp,design_name):
	r_netlist=open(format_dir+"/ignore_form_pex_ffdco.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=HSPICE_mds.netmap() 
	### include pex.netlist ###
	netmap1.get_net('dn',design_name,None,None,None)
	### edge_sel voltage pulses ###
	pw=2e-8 #pulsewidth
	Tflt=0.1e-9 #floating time
	netmap1.get_net('ve',None,0,nstg*4-1,1)	
	netmap1.get_net('ES',None,0,nstg*4-1,1) # for edge sel	
	netmap1.get_net('TD',None,0,(pw+Tflt)*(nstg*4-1),pw+Tflt)	
	netmap1.get_net('PW',None,None,pw,nstg*4)	
	netmap1.get_net('PR',None,None,nstg*4*pw,nstg*4)	
	
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
	netmap1.get_net('es',None,0,nstg*4-1,1) # for edge sel	
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
			line='.include '+ '"./../../'+netlist_dir+line[10:len(line)]
			w_raw_netlist.write(line)	
		elif inst_start==0:		
			w_raw_netlist.write(line)	
			

def gen_pex_netlist_ad(raw_pex_dir,netlist_dir,format_dir,ncc,ndrv,nfc,nstg,ninterp,design_name):
	r_netlist=open(format_dir+"/ignore_form_pex_tdc_dco.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=HSPICE_mds.netmap() 
	### include pex.netlist ###
	netmap1.get_net('dn',design_name,None,None,None)
	### edge_sel voltage pulses ###
	pw=2e-8 #pulsewidth
	Tflt=0.1e-9 #floating time
	netmap1.get_net('ve',None,0,nstg*4-1,1)	
	netmap1.get_net('ES',None,0,nstg*4-1,1) # for edge sel	
	netmap1.get_net('TD',None,0,(pw+Tflt)*(nstg*4-1),pw+Tflt)	
	netmap1.get_net('PW',None,None,pw,nstg*4)	
	netmap1.get_net('PR',None,None,nstg*4*pw,nstg*4)	
	
	### enable voltages for CC,FC ###
	netmap1.get_net('vf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('nf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('Vf','vf',0,nfc*nstg-1,1) #for v2	
	netmap1.get_net('vc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('nc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('Vc','vc',0,ncc*nstg-1,1) #for v2

	### write the pex.netlist inputs ### 
	netmap1.get_net('sp',None,0,4*nstg-1,1)	
	netmap1.get_net('cc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('fc',None,0,nfc*nstg-1,1)	
	netmap1.get_net('es',None,0,nstg*4-1,1) # for edge sel	
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
			line='.include '+ '"./../../'+netlist_dir+line[10:len(line)]
			w_raw_netlist.write(line)	
		elif inst_start==0:		
			w_raw_netlist.write(line)	


def gen_pex_netlist_ad2(raw_pex_dir,netlist_dir,format_dir,ncc,ndrv,nfc,nstg,ninterp,design_name):
	r_netlist=open(format_dir+"/ignore_form_pex_tdc_dco2.sp","r")
	w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=HSPICE_mds.netmap() 
	### include pex.netlist ###
	netmap1.get_net('dn',design_name,None,None,None)
	### edge_sel voltage pulses ###
	pw=2e-8 #pulsewidth
	Tflt=0.1e-9 #floating time
	netmap1.get_net('ve',None,0,nstg*4-1,1)	
	netmap1.get_net('ES',None,0,nstg*4-1,1) # for edge sel	
	netmap1.get_net('TD',None,0,(pw+Tflt)*(nstg*4-1),pw+Tflt)	
	netmap1.get_net('PW',None,None,pw,nstg*4)	
	netmap1.get_net('PR',None,None,nstg*4*pw,nstg*4)	
	
	### enable voltages for CC,FC ###
	netmap1.get_net('vf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('nf',None,0,nfc*nstg-1,1)	
	netmap1.get_net('Vf','vf',0,nfc*nstg-1,1) #for v2	
	netmap1.get_net('vc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('nc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('Vc','vc',0,ncc*nstg-1,1) #for v2

	### write the pex.netlist inputs ### 
	netmap1.get_net('sp',None,0,4*nstg-1,1)	
	netmap1.get_net('sl',None,0,4*nstg-1,1)	
	netmap1.get_net('sc',None,0,4*nstg-1,1)	
	netmap1.get_net('cc',None,0,ncc*nstg-1,1)	
	netmap1.get_net('fc',None,0,nfc*nstg-1,1)	
	netmap1.get_net('es',None,0,nstg*4-1,1) # for edge sel	
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
			line='.include '+ '"./../../'+netlist_dir+line[10:len(line)]
			w_raw_netlist.write(line)	
		elif inst_start==0:		
			w_raw_netlist.write(line)	



def test_pad_netlist(formatDir,netlistDir, bufList,capList, numB1, numB2):
	r_form=open(formatDir+'ignore_format_test_pad.sp','r')
	
	r_lines=list(r_form.readlines()) 
	
	#=== bufList: [bufname1, bufname2, bufname3, ... ] ===

	ii=1
	nm=[None]*len(bufList)
	nm1=ignore_HSPICE_mds.netmap()
	for bufname in bufList:
		nm[ii-1]=ignore_HSPICE_mds.netmap()
		nm[ii-1].get_net('cp',None,ii,ii,1)
		nm[ii-1].get_net('pn',bufname,None,None,None)
		nm[ii-1].get_net('cv',None,float(capList[ii-1]),float(capList[ii-1]),1)

		nm[ii-1].get_net('b1',None,ii*1000,ii*1000+numB1-1,1)
		nm[ii-1].get_net('n1',None,None,ii,numB1)
#		for jj in range(numB1):
#			nm[ii].get_net('c1',bufname,None,None,None)
		nm[ii-1].get_net('c1',bufname,None,numB1,None)
		nm[ii-1].get_net('b2',None,ii*10000,ii*10000+numB2-1,1)
		nm[ii-1].get_net('P1',bufname,None,numB2,None)
#		for jj in range(numB2):
#			nm[ii].get_net('N1',bufname,None,None,None)
		nm[ii-1].get_net('N1',None,None,ii,numB2)
		nm[ii-1].get_net('C1',bufname,None,numB2,None)
		nm[ii-1].get_net('PN',None,ii,ii,1)
		nm[ii-1].get_net('Po',bufname,None,None,None)
		ii=ii+1

	w_file=open(netlistDir+'wrapped_test_pad.sp','w')
	
	for line in r_lines:
		if line[0:2]=='@@':
			for i in range(0,len(bufList)):
				nm[i].printline(line,w_file)
		else:
			nm[0].printline(line,w_file)

		#nm1.printline(line,w_file)


def gen_outbuf_pex_netlist(pwr_sim,raw_pex_dir,design_name,netlist_dir,format_dir,vdd):
	if pwr_sim==0:
		r_netlist=open(format_dir+"/ignore_form_wrapped_outbuff_div.sp","r")
		w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	elif pwr_sim==1:
		r_netlist=open(format_dir+"/ignore_form_wrapped_outbuff_div_2_pwr.sp","r")
		w_netlist=open(netlist_dir+"/"+"wrapped_"+design_name+"_pwr.sp","w")
	lines=list(r_netlist.readlines())

	
	netmap1=HSPICE_mds.netmap() 
	### register all the inputs to netmap ###
	netmap1.get_net('nd',netlist_dir,None,None,None)
	netmap1.get_net('dn',design_name,None,None,None)
	netmap1.get_net('fm','pex.netlist',None,None,None)

	r_raw_netlist=open(raw_pex_dir+"/"+design_name+".pex.netlist","r")
	w_raw_netlist=open(netlist_dir+"/"+design_name+".pex.netlist","w")

	raw_lines=list(r_raw_netlist.readlines())
	#print(ref_lines)
	nm2=HSPICE_mds.netmap()	
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

	
def gen_dco_pex_netlist(raw_pex_dir,abs_netlist_dir,format_dir,ncc,ndrv,nfc,nstg,ninterp,design_name):
	r_netlist=open(format_dir+"/ignore_form_ffdco.sp","r")
	w_netlist=open(abs_netlist_dir+"/"+"wrapped_"+design_name+".sp","w")
	lines=list(r_netlist.readlines())
	
	netmap1=HSPICE_mds.netmap() 
	### include pex.netlist ###
	netmap1.get_net('dn',design_name,None,None,None)
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

#	for line in lines:
#		netmap1.printline(line,w_netlist)

#	w_netlist.close()
#	r_netlist.close()


	r_raw_netlist=open(raw_pex_dir+"/"+design_name+".pex.netlist","r")
	w_raw_netlist=open(abs_netlist_dir+"/"+design_name+".pex.netlist","w")
	raw_lines=list(r_raw_netlist.readlines())

	
	nm2=HSPICE_mds.netmap()	
	### modify the .include file path in pex.netlist ###
	for line in raw_lines:
		if line[0:8]=='.include':
			#line='.include '+ '"./../../'+netlist_dir+line[10:len(line)]
			line='.include '+ '"'+abs_netlist_dir+line[10:len(line)] #--- absolute path ---
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
