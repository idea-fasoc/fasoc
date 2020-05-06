#===============================================================
# module for Beta version: PD pll including ff_dco and outbuff_div
# as hard macros
#===============================================================
import sys
import getopt
import math
import subprocess as sp
import fileinput
import re
import os
import shutil
import glob 
import numpy as np
import argparse
import json

import HSPICE_mds
import HSPICEpex_netlist
import Pex_gen
import Flow_setup
import editPin_gen
#------------------------------------------------------------------------------
# generates ff_dco
#------------------------------------------------------------------------------
def pdpll_flow(formatDir,flowDir,ffdco_flowDir,outbuff_div_flowDir,pll_name,bleach,ndrv,ncc,nfc,nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir):
	print ('#======================================================================')
	print('# setting up flow directory for ffdco')
	print ('#======================================================================')
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	#--- copy verilog files to flowDir/src/ --- taken care by Flow_setup.py
	shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',flowDir+'/src/FUNCTIONS.v')	
	shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER_TDC_COUNTER.v',flowDir+'/src/PLL_CONTROLLER_TDC_COUNTER.v')	
	shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER.v',flowDir+'/src/PLL_CONTROLLER.v')	
	shutil.copyfile(verilogSrcDir+'TDC_COUNTER.v',flowDir+'/src/TDC_COUNTER.v')	
	shutil.copyfile(verilogSrcDir+'SSC_GENERATOR.v',flowDir+'/src/SSC_GENERATOR.v')	
	shutil.copyfile(verilogSrcDir+'dco_CC.v',flowDir+'/src/dco_CC.v')	
	shutil.copyfile(verilogSrcDir+'dco_FC.v',flowDir+'/src/dco_FC.v')	
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp.v',flowDir+'/src/synth_pll_dco_interp.v')	
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff.v',flowDir+'/src/synth_pll_dco_outbuff.v')	
	#--- copy exports from ffdco ---
	spfiles=glob.iglob(os.path.join(ffdco_flowDir+'results/calibre/lvs/','*.sp'))
	for spfile in spfiles:
		if os.path.isfile(spfile):
			shutil.copy2(spfile,ffdco_flowDir+'export/'+pll_name+'_ffdco.cdl')
		else:
			print('Error: cant find the '+pll_name+'_ffdco.sp file in'+ffdco_flowDir+'results/calibre/lvs/')
			sys.exit(1)
	if os.path.isdir(flowDir+'blocks/'+pll_name+'_ffdco')==0:
		p = sp.Popen(['mkdir','blocks/'+pll_name+'_ffdco'], cwd=flowDir)
		p.wait()
	
	if os.path.isdir(flowDir+'blocks/'+pll_name+'_ffdco/export')==0:
		shutil.copytree(ffdco_flowDir+'export',flowDir+'blocks/'+pll_name+'_ffdco/export')
	#--- copy exports from outbuff_div ---
	spfiles=glob.iglob(os.path.join(outbuff_div_flowDir+'results/calibre/lvs/','*.sp'))
	for spfile in spfiles:
		if os.path.isfile(spfile):
			shutil.copy2(spfile,outbuff_div_flowDir+'export/outbuff_div.cdl')
		else:
			print('Error: cant find the outbuff_div.sp file in '+outbuff_div_flowDir+'results/calibre/lvs/')
			sys.exit(1)
	if os.path.isdir(flowDir+'blocks/outbuff_div')==0:
		p = sp.Popen(['mkdir','blocks/outbuff_div'], cwd=flowDir)
		p.wait()
	
	if os.path.isdir(flowDir+'blocks/outbuff_div/export')==0:
		shutil.copytree(outbuff_div_flowDir+'export',flowDir+'blocks/outbuff_div/export')

	#--- generate  include.mk file ---
	rmkfile=open(formatDir+'/form_ffdco_include.mk','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('iN',pll_name,None,None,None)
	with open(flowDir+'include.mk','w') as wmkfile:
		lines_const=list(rmkfile.readlines())
		for line in lines_const:
			nm1.printline(line,wmkfile)
	#--- bleach ---
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()
	
	#--- generate verilog file ---
	rvfile=open(formatDir+'/form_pll_PD.v','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('iN',pll_name,None,None,None)
	nm1.get_net('nM',None,nstg,nstg,1)
	nm1.get_net('nD',None,ndrv,ndrv,1)
	nm1.get_net('nF',None,nfc,nfc,1)
	nm1.get_net('nC',None,ncc,ncc,1)
	nm1.get_net('dN',pll_name+'_ffdco',None,None,None)
	with open(flowDir+'src/'+pll_name+'.v','w') as wvfile:
		lines_const=list(rvfile.readlines())
		for line in lines_const:
			nm1.printline(line,wvfile)
	#--- generate dc.filelist.tcl
	rflfile=open(formatDir+'/form_PDpll_dc.filelist.tcl','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('iN',pll_name+'.v',None,None,None)
	with open(flowDir+'/scripts/dc/dc.filelist.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- generate constraints.tcl
	rcfile=open(formatDir+'/form_PDpll_constraints.tcl','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('NS',None,2*nstg-1,2*nstg-1,1)
	nm1.get_net('nS',None,2*nstg-1,2*nstg-1,1)
	with open(flowDir+'/scripts/dc/constraints.tcl','w') as wcfile:
		lines_const=list(rcfile.readlines())
		for line in lines_const:
			nm1.printline(line,wcfile)
	#--- get ffdco size ---
	ffdco_lef=open(flowDir+'/blocks/'+pll_name+'_ffdco/export/'+pll_name+'_ffdco.lef','r')
	lines_dco=list(ffdco_lef.readlines())
	indco=0
	for line in lines_dco:
		words=line.split()
		for word in words:
			if word==pll_name+'_ffdco':
				indco=1
			if indco==1 and word=='SIZE':
				sizes=line.split()
				W_dco=float(sizes[1])
				H_dco=float(sizes[3])
	#--- get outbuff_div size ---
	bufdiv_lef=open(flowDir+'/blocks/outbuff_div/export/outbuff_div.lef','r')
	lines_buf=list(bufdiv_lef.readlines())
	inbuf=0
	for line in lines_buf:
		words=line.split()
		for word in words:
			if word=='outbuff_div':
				inbuf=1
			if inbuf==1 and word=='SIZE':
				sizes=line.split()
				W_buf=float(sizes[1])
				H_buf=float(sizes[3])
	#--- run synth ---
	print ('#======================================================================')
	print('# ready for synth & apr')
	print ('#======================================================================')
	if synth==1:
		#-------------------------------------------
		# run CADRE flow 
		#-------------------------------------------
		p = sp.Popen(['make','synth'], cwd=flowDir)
		p.wait()
		with open(flowDir + '/reports/dc/' + pll_name + '.mapped.area.rpt', \
			  'r')as file:
		   filedata = file.read()
		m = re.search('Total cell area: *([0-9.]*)', filedata)
		if m:
		   A_cont = float(m.group(1))
		   print('estimated area after synthesis is: %e'%(A_cont))
		else:
		   print ('Synthesis Failed')
	#--- calculate area of the PDpll ---
	A_dco=W_dco*H_dco
	A_buf=W_buf*H_buf
	W_cont=int(math.ceil(math.sqrt(A_cont*1.4/5))*5)
	H_cont=W_cont
	W_pll=int(max(W_dco,W_buf)+W_cont/2)
	H_pll=int(H_dco+H_buf+H_cont/2)
	#--- calculate X,Y coordinates of ffdco, buf ---
	X_buf=int(W_pll/2-W_buf/2)	
	Y_buf=28.8	

	X_dco=int(W_pll/2-W_dco/2)
	Y_dco=int(Y_buf+H_buf+40)
	#--- generate always_source.tcl ---
	ralfile=open(formatDir+'/form_PDpll_always_source.tcl','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('cW',None,W_pll,W_pll,1)
	nm1.get_net('cH',None,H_pll,H_pll,1)
	nm1.get_net('dX',None,X_dco,X_dco,1)
	nm1.get_net('dY',None,Y_dco,Y_dco,1)
	nm1.get_net('bX',None,X_buf,X_buf,1)
	nm1.get_net('bY',None,Y_buf,Y_buf,1)
	nm1.get_net('dW',None,W_dco,W_dco,1)
	nm1.get_net('dH',None,H_dco,H_dco,1)
	with open(flowDir+'scripts/innovus/always_source.tcl','w') as walfile:
		lines_const=list(ralfile.readlines())
		for line in lines_const:
			nm1.printline(line,walfile)
	#--- run apr flow ---	
	print ('#======================================================================')
	print('# ready for apr')
	print ('#======================================================================')
	if apr==1:	
		#p = sp.Popen(['make','bleach_init'], cwd=flowDir)
		#p.wait()

		#p = sp.Popen(['make','place'], cwd=flowDir)
		#p.wait()
		#sys.exit(1)

		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()

		p = sp.Popen(['cp','results/innovus/'+pll_name+'_ffdco_cutObs.lef','export/'+pll_name+'_ffdco.lef'], cwd=flowDir)
		p.wait()
	return W_dco, H_dco, W_pll, H_pll	

#------------------------------------------------------------------------------
# generates outbuff_div
#	current version of outbuff_div is not configurable. Below are the programmable options
#	1. Divide ratio: 1~64 (only 2^N works)
#	2. buffer power: 1~16 
#------------------------------------------------------------------------------
def outbuff_div_flow(flowDir,bleach,design):
	#--- bleach ---
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()
		
	if design==1:
		#-------------------------------------------
		# run CADRE flow 
		#-------------------------------------------
		p = sp.Popen(['make','synth'], cwd=flowDir)
		p.wait()

		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()

		p = sp.Popen(['cp','results/innovus/'+'outbuff_div_cutObs.lef','export/outbuff_div.lef'], cwd=flowDir)
		p.wait()

#------------------------------------------------------------------------------
# generates dco.gds, .pex.netlist 
#------------------------------------------------------------------------------
def dco_flow_pex(calibreRulesDir,netlistDir,formatDir,flowDir,rawPexDir,extDir,simDir,ndrv,ncc,nfc,nstg,ninterp,W_CC,H_CC,W_FC,H_FC,bleach,design,pex):
	designName='dco_%ddrv_%dcc_%dfc_%dstg'%(ndrv,ncc,nfc,nstg)
	print('starting flow for '+designName)
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()

	Flow_setup.dco_flow_setup(formatDir,flowDir,ndrv,ncc,nfc,nstg)

	NCtotal=nstg*(ncc+ndrv)
	NFtotal=nstg*(nfc)
	Atotal=NCtotal*W_CC*H_CC+NFtotal*W_FC*H_FC	
	W_core=math.ceil(math.sqrt(Atotal)*1.2)
	H_core=W_core
	
	with open(flowDir + '/scripts/innovus/always_source.tcl', 'r') as file:
	   filedata = file.read()
	filedata = re.sub(r'set core_width.*', r'set core_width    ' + \
			  str(W_core) + ' ;# Core Area Width', filedata)
	filedata = re.sub(r'set core_height.*', r'set core_height   ' + \
			  str(H_core) + ' ;# Core Area Height', filedata)
	with open(flowDir + '/scripts/innovus/always_source.tcl', 'w') as file:
	   file.write(filedata)
		
	#-------------------------------------------
	# run CADRE flow 
	#-------------------------------------------
	if design==1:
		
		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()
		
	#-------------------------------------------
	# check if pex.netlist already exists 
	#-------------------------------------------
	if pex==1:
		try:
			exist=open(netlistDir+designName+'.pex.netlist','r')
			print(designName+'.pex.netlist already exists')
		except:
			#-------------------------------------------
			# generate pex view
			#-------------------------------------------
			lvs=1  # do lvs for default
			Pex_gen.post_apr(calibreRulesDir,flowDir,extDir,simDir,designName,lvs,pex)
			
			#-------------------------------------------
			# modify the pex netlist
			#-------------------------------------------
			HSPICEpex_netlist.gen_pex_netlist(rawPexDir,netlistDir,formatDir,ncc,ndrv,nfc,nstg,ninterp,designName)
			
			#-------------------------------------------
			# copy .pxi, .pex
			#-------------------------------------------
			p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.'+designName+'.pxi',netlistDir+'/'+designName+'.pex.netlist.'+designName+'.pxi'])
			p.wait()
			p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.pex',netlistDir+'/'+designName+'.pex.netlist.pex'])
			p.wait()
