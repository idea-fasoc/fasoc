#===============================================================
# function that runs through CADRE(pll,dco) + pex(dco) 
#===============================================================
import sys
import getopt
import math
import subprocess as sp
import fileinput
import re
import os
import shutil
import numpy as np
import argparse
import json

import HSPICE_mds
import HSPICEpex_netlist
import Pex_gen
import Flow_setup
#------------------------------------------------------------------------------
# generates synth_pll.gds
#------------------------------------------------------------------------------
def pll_flow(designName,formatDir,flowDir,ndrv,ncc,nfc,nstg,W_CC,H_CC,W_FC,H_FC,FCW,vco_per,max_per,bleach,synth,design,flat):
#	designName='synth_pll'
	print ('#======================================================================')
	print('# starting cadre flow for '+designName)
	print ('#======================================================================')
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()
	
	# generate verilog file
	#Flow_setup.pll_flow_setup(designName,formatDir,flowDir,ndrv,ncc,nfc,nstg)

	NCtotal=nstg*(ncc+ndrv)
	NFtotal=nstg*(nfc)
	A_dco=NCtotal*W_CC*H_CC+NFtotal*W_FC*H_FC
	W_dco=math.ceil(math.sqrt(A_dco)*1.4/5)*5
	H_dco=math.ceil(math.sqrt(A_dco)*1.4/5)*5
	
	nm1=HSPICE_mds.netmap()
	nm1.get_net('vp',None,vco_per,vco_per,1)
	nm1.get_net('mp',None,max_per,max_per,1)
	nm1.get_net('db',None,FCW,FCW,1)
	r_const=open(formatDir+'form_pll_constraints.tcl','r')
	with open(flowDir+'scripts/dc/constraints.tcl','w') as w_const:
		lines_const=list(r_const.readlines())
		for line in lines_const:
			nm1.printline(line,w_const)
		
	if synth==1:
		#-------------------------------------------
		# run CADRE flow 
		#-------------------------------------------
		p = sp.Popen(['make','synth'], cwd=flowDir)
		p.wait()

	# read total estimated area of controller (it doesn't include the aux-cells)
	with open(flowDir + '/reports/dc/' + designName + '.mapped.area.rpt', \
		  'r')as file:
	   filedata = file.read()
	m = re.search('Total cell area: *([0-9.]*)', filedata)
	if m:
	   coreCellArea = float(m.group(1))
	   print('estimated area after synthesis is: %e'%(coreCellArea))
	else:
	   print ('Synthesis Failed')

	# Calculate and update the core cell area dimensions
	W_cont = math.ceil(math.sqrt(coreCellArea*1.5)/5)*5
	H_cont = W_cont

	W_core = math.ceil((W_dco+W_cont*2/3)/5)*5	
	H_core = math.ceil((H_dco+H_cont*2/3)/5)*5	
	A_core = W_core*H_core

	nm1.get_net('cw',None,W_core,W_core,1)
	nm1.get_net('ch',None,H_core,H_core,1)
	nm1.get_net('dw',None,W_dco,W_dco,1)
	nm1.get_net('dh',None,H_dco,H_dco,1)

	if flat==0:
		r_always=open(formatDir+'form_pll_always_source.tcl','r')
		r_init=open(formatDir+'form_pll_post_init.tcl','r')

		with open(flowDir+'scripts/innovus/always_source.tcl','w') as w_always:
			lines_always=list(r_always.readlines())	
			for line in lines_always:
				nm1.printline(line,w_always)
		with open(flowDir+'scripts/innovus/post_init.tcl','w') as w_init:
			lines_init=list(r_init.readlines())	
			for line in lines_init:
				nm1.printline(line,w_init)
	elif flat==1:
		r_always=open(formatDir+'form_pll_flat_always_source.tcl','r')
		with open(flowDir+'scripts/innovus/always_source.tcl','w') as w_always:
			lines_always=list(r_always.readlines())	
			for line in lines_always:
				nm1.printline(line,w_always)

	if design==1:	
		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()
	return A_core	

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
