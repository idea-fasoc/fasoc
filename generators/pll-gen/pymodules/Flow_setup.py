#====================================================================
# prepare setups for digital flow
# generates 1 verilog file
#====================================================================
import subprocess as sp
import HSPICE_mds
import sys
import os
import shutil
def pll_flow_setup(outMode,designName,genDir,outDir,formatDir,flowDir,ndrv,ncc,nfc,nstg):

	# write verilog 
	nm1=HSPICE_mds.netmap()
	nm1.get_net('iN',designName,None,None,None)		
	nm1.get_net('nM',None,None,nstg,1)		
	nm1.get_net('nD',None,None,ndrv,1)		
	nm1.get_net('nF',None,None,nfc,1)		
	nm1.get_net('nC',None,None,ncc,1)		
	r_pll_v=open(formatDir+'form_synth_pll.v','r')	
	lines=list(r_pll_v.readlines())

	with open(genDir+'verilogs/'+designName+'.v','w') as w_pll_v:
		for line in lines:
			nm1.printline(line,w_pll_v)
	if outMode=='macro' or outMode=='full':
		p = sp.Popen(['cp',genDir+'./verilogs/*',flowDir+'src/']) 
		p.wait()
	elif outMode=='verilog':
		vsrcs=os.listdir(genDir+'./verilogs/')
		for vsrc in vsrcs:
			full_vsrc=os.path.join(genDir+'./verilogs/',vsrc)
			if os.path.isfile(full_vsrc):
				shutil.copy(full_vsrc,outDir+'/')
		print('verilog mode: verilog sources are generated in '+outDir)
		#p = sp.Popen(['cp','verilogs/'+designName+'.v',outDir+'/']) 
		#p.wait()
#		with open(flowDir+'src/'+designName+'.v','w') as w_pll_v2:
#			for line in lines:
#				nm1.printline(line,w_pll_v2)	
	
	# write include.mk 
	nm1=HSPICE_mds.netmap()
	nm1.get_net('dn',designName,None,None,None)		
	r_pll_mk=open(formatDir+'form_pll_include.mk','r')	
	lines=list(r_pll_mk.readlines())
	if outMode=='macro' or outMode=='full':
		with open(flowDir+'/include.mk','w') as w_pll_mk:
			for line in lines:
				nm1.printline(line,w_pll_mk)	

	# write dc.filelist.tcl 
	nm1=HSPICE_mds.netmap()
	nm1.get_net('DN',designName,None,None,None)		
	r_pll_fl=open(formatDir+'form_pll_dc.filelist.tcl','r')	
	lines=list(r_pll_fl.readlines())
	if outMode=='macro' or outMode=='full':
		with open(flowDir+'/scripts/dc/dc.filelist.tcl','w') as w_pll_fl:
			for line in lines:
				nm1.printline(line,w_pll_fl)	

def dco_flow_setup(formatDir,flowDir,ndrv,ncc,nfc,nstg):

	#-------------------------------------------
	# generate dco.v to /flow/src/
	#-------------------------------------------
	r_dco_v=open(formatDir+'form_DCO.v','r')	
	lines=list(r_dco_v.readlines())
	
	nm1=HSPICE_mds.netmap()
	nm1.get_net('nD',None,None,ndrv,1)		
	nm1.get_net('nC',None,None,ncc,1)		
	nm1.get_net('nF',None,None,nfc,1)		
	nm1.get_net('nM',None,None,nstg,1)		
	nm1.get_net('nm',None,None,nstg,1)		
	nm1.get_net('nd',None,None,ndrv,1)		
	nm1.get_net('nf',None,None,nfc,1)		
	nm1.get_net('nc',None,None,ncc,1)		
	
	with open(flowDir+'src/dco_%ddrv_%dcc_%dfc_%dstg.v'%(ndrv,ncc,nfc,nstg),'w') as w_dco_v:		
		for line in lines:
			nm1.printline(line,w_dco_v)	
	#-------------------------------------------
	# generate include.mk 
	#-------------------------------------------
	r_include=open(formatDir+'form_include.mk','r')	
	lines=list(r_include.readlines())
	
	nm1=HSPICE_mds.netmap()
	nm1.get_net('nD',None,None,ndrv,1)		
	nm1.get_net('nC',None,None,ncc,1)		
	nm1.get_net('nF',None,None,nfc,1)		
	nm1.get_net('nM',None,None,nstg,1)		
	
	with open(flowDir+'include.mk','w') as w_include:		
		for line in lines:
			nm1.printline(line,w_include)	
	#-------------------------------------------
	# generate dc.filelist.tcl 
	#-------------------------------------------
	r_flist=open(formatDir+'form_dc.filelist.tcl','r')	
	lines=list(r_flist.readlines())
	
	nm1=HSPICE_mds.netmap()
	nm1.get_net('nD',None,None,ndrv,1)		
	nm1.get_net('nC',None,None,ncc,1)		
	nm1.get_net('nF',None,None,nfc,1)		
	nm1.get_net('nM',None,None,nstg,1)		
	
	with open(flowDir+'scripts/dc/dc.filelist.tcl','w') as w_flist:	
		for line in lines:
			nm1.printline(line,w_flist)	
