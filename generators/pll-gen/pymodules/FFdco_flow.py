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
import editPin_gen
#------------------------------------------------------------------------------
# generates ff_dco
#------------------------------------------------------------------------------
def ffdco_flow(formatDir,flowDir,pll_name,bleach,ndrv,ncc,nfc,nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir):
	print ('#======================================================================')
	print('# setting up flow directory for ffdco')
	print ('#======================================================================')
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	#--- copy verilog files to flowDir/src/ ---
	shutil.copyfile(verilogSrcDir+'dco_CC.v',flowDir+'/src/dco_CC.v')	
	shutil.copyfile(verilogSrcDir+'dco_FC.v',flowDir+'/src/dco_FC.v')	
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp.v',flowDir+'/src/synth_pll_dco_interp.v')	
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff.v',flowDir+'/src/synth_pll_dco_outbuff.v')	
	shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',flowDir+'/src/FUNCTIONS.v')	
	#--- generate  include.mk file ---
	rmkfile=open(formatDir+'/form_ffdco_include.mk','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('iN',pll_name+'_ffdco',None,None,None)
	with open(flowDir+'include.mk','w') as wmkfile:
		lines_const=list(rmkfile.readlines())
		for line in lines_const:
			nm1.printline(line,wmkfile)
	#--- bleach ---
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()
	
	#--- generate verilog file ---
	rvfile=open(formatDir+'/form_ffdco.v','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('iN',pll_name+'_ffdco',None,None,None)
	nm1.get_net('nM',None,nstg,nstg,1)
	nm1.get_net('nD',None,ndrv,ndrv,1)
	nm1.get_net('nF',None,nfc,nfc,1)
	nm1.get_net('nC',None,ncc,ncc,1)
	with open(flowDir+'src/'+pll_name+'_ffdco.v','w') as wvfile:
		lines_const=list(rvfile.readlines())
		for line in lines_const:
			nm1.printline(line,wvfile)
	#--- generate dc.filelist.tcl
	rflfile=open(formatDir+'/form_ffdco_dc.filelist.tcl','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('iN',pll_name+'_ffdco.v',None,None,None)
	with open(flowDir+'scripts/dc/dc.filelist.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- calculate area ---
	NCtotal=nstg*(ncc+ndrv)
	NFtotal=nstg*(nfc)
	A_dco=NCtotal*W_CC*H_CC+NFtotal*W_FC*H_FC
	W_dco=math.ceil(math.sqrt(A_dco)*3.0/5)*5
	H_dco=math.ceil(math.sqrt(A_dco)*3.0/5)*5
	#--- generate always_source.tcl
	ralfile=open(formatDir+'/form_ffdco_always_source.tcl','r')
	nm1=HSPICE_mds.netmap()
	nm1.get_net('cW',None,W_dco,W_dco,1)
	nm1.get_net('cH',None,H_dco,H_dco,1)
	with open(flowDir+'scripts/innovus/always_source.tcl','w') as walfile:
		lines_const=list(ralfile.readlines())
		for line in lines_const:
			nm1.printline(line,walfile)
	#--- generate pre_place.tcl with editPin_gen ---	
	version=2
	wfile_name=flowDir+'scripts/innovus/pre_place.tcl'
	editPin_gen.editPin_gen(ndrv,ncc,nfc,nstg,formatDir,version,wfile_name)
	print ('#======================================================================')
	print('# ready for synth & apr')
	print ('#======================================================================')
	if synth==1:
		#-------------------------------------------
		# run CADRE flow 
		#-------------------------------------------
		p = sp.Popen(['make','synth'], cwd=flowDir)
		p.wait()
	# read total estimated area of controller (it doesn't include the aux-cells)
		with open(flowDir + '/reports/dc/' + pll_name + '_ffdco.mapped.area.rpt', \
			  'r')as file:
		   filedata = file.read()
		m = re.search('Total cell area: *([0-9.]*)', filedata)
		if m:
		   coreCellArea = float(m.group(1))
		   print('estimated area after synthesis is: %e'%(coreCellArea))
		else:
		   print ('Synthesis Failed')


	if apr==1:	
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
	return W_dco, H_dco	

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
