#===============================================================
# function that runs digital flow
# 	1. ffdco_flow
# 	2. outbuff_flow
# 	3. pdpll_flow 
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
import glob

import txt_mds

def pll_verilog_gen(outMode,designName,genDir,outDir,formatDir,flowDir,ndrv,ncc,nfc,nstg,verilogSrcDir,buf_small,bufz,buf_big,edge_sel,dcoName,platform):

	if outMode=='macro' or outMode=='full':
		shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',flowDir+'/src/FUNCTIONS.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER_TDC_COUNTER.v',flowDir+'/src/PLL_CONTROLLER_TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER.v',flowDir+'/src/PLL_CONTROLLER.v')	
		shutil.copyfile(verilogSrcDir+'TDC_COUNTER.v',flowDir+'/src/TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'SSC_GENERATOR.v',flowDir+'/src/SSC_GENERATOR.v')	
		shutil.copyfile(verilogSrcDir+'dco_CC.v',flowDir+'/src/dco_CC.v')	
		shutil.copyfile(verilogSrcDir+'dco_FC.v',flowDir+'/src/dco_FC.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp_'+platform+'.v',flowDir+'/src/synth_pll_dco_interp.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff_'+platform+'.v',flowDir+'/src/synth_pll_dco_outbuff.v')	
		print(outMode,'mode: verilog sources are generated in ',flowDir,'src/')
	elif outMode=='verilog':
		shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',outDir+'/FUNCTIONS.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER_TDC_COUNTER.v',outDir+'/PLL_CONTROLLER_TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER.v',outDir+'/PLL_CONTROLLER.v')	
		shutil.copyfile(verilogSrcDir+'TDC_COUNTER.v',outDir+'/TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'SSC_GENERATOR.v',outDir+'/SSC_GENERATOR.v')	
		shutil.copyfile(verilogSrcDir+'dco_CC.v',outDir+'/dco_CC.v')	
		shutil.copyfile(verilogSrcDir+'dco_FC.v',outDir+'/dco_FC.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp_'+platform+'.v',flowDir+'/src/synth_pll_dco_interp.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff_'+platform+'.v',flowDir+'/src/synth_pll_dco_outbuff.v')	
		print(outMode,'mode: verilog sources are generated in ',outDir)
		print('verilog mode: verilog sources are generated in '+outDir)
		#--- generate verilog file ---
		r_pll_v=open(formatDir+'/form_pll_PD.v','r')
		nm1=txt_mds.netmap()
		nm1.get_net('iN',designName,None,None,None)
		nm1.get_net('nM',None,nstg,nstg,1)
		nm1.get_net('nD',None,ndrv,ndrv,1)
		nm1.get_net('nF',None,nfc,nfc,1)
		nm1.get_net('nC',None,ncc,ncc,1)
		nm1.get_net('dN',dcoName,None,None,None)
		with open(outDir+'/'+designName+'.v','w') as wvfile:
			lines_pll=list(r_pll_v.readlines())
			for line in lines_pll:
				nm1.printline(line,wvfile)
		#--- generate verilog file ---
		rvfile=open(formatDir+'/form_dco.v','r')
		nm1=txt_mds.netmap()
		if edge_sel==1:
			nm1.get_net('IE','INCLUDE_EDGE_SEL',None,None,None)
		else:
			nm1.get_net('IE','EXCLUDE_EDGE_SEL',None,None,None)
		nm1.get_net('iN',dcoName,None,None,None)
		nm1.get_net('nM',None,nstg,nstg,1)
		nm1.get_net('nD',None,ndrv,ndrv,1)
		nm1.get_net('nF',None,nfc,nfc,1)
		nm1.get_net('nC',None,ncc,ncc,1)
		for bcnt in range (1,10):
			nm1.get_net('b%d'%(bcnt),buf_small,None,None,None)
		for zcnt in range (1,5):
			nm1.get_net('z%d'%(zcnt),bufz,None,None,None)
		nm1.get_net('B1',buf_big,None,None,None)
		with open(outDir+'/'+dcoName+'.v','w') as wvfile:
			lines_const=list(rvfile.readlines())
			for line in lines_const:
				nm1.printline(line,wvfile)

#------------------------------------------------------------------------------
# generates ff_dco
#------------------------------------------------------------------------------
def dco_flow(formatDir,flowDir,dcoName,bleach,ndrv,ncc,nfc,nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir,platform,edge_sel,buf_small,buf_big,bufz,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,max_r_l):
	print ('#======================================================================')
	print('# setting up flow directory for dco')
	print ('#======================================================================')
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	#--- copy verilog files to flowDir/src/ ---
	shutil.copyfile(verilogSrcDir+'dco_CC.v',flowDir+'/src/dco_CC.v')	
	shutil.copyfile(verilogSrcDir+'dco_FC.v',flowDir+'/src/dco_FC.v')	
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp_'+platform+'.v',flowDir+'/src/synth_pll_dco_interp.v')	
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff_'+platform+'.v',flowDir+'/src/synth_pll_dco_outbuff.v')	
	shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',flowDir+'/src/FUNCTIONS.v')	
	#--- copy scripts files to flowDir/scripts/ ---
	shutil.copyfile(formatDir+'dco_dc.include.tcl',flowDir+'/scripts/dc/dc.include.tcl')	
	shutil.copyfile(formatDir+'dco_dc.read_design.tcl',flowDir+'/scripts/dc/dc.read_design.tcl')	
	shutil.copyfile(formatDir+'dco_dc_setup.tcl',flowDir+'/scripts/dc/dc_setup.tcl')	
	shutil.copyfile(formatDir+'dco_report_timing.tcl',flowDir+'/scripts/dc/report_timing.tcl')	
	shutil.copyfile(formatDir+'dco_floorplan.tcl',flowDir+'/scripts/innovus/floorplan.tcl')	
	shutil.copyfile(formatDir+'dco_power_intent.cpf',flowDir+'/scripts/innovus/power_intent.cpf')	
	shutil.copyfile(formatDir+platform+'_dco_post_init.tcl',flowDir+'/scripts/innovus/post_init.tcl')	
	shutil.copyfile(formatDir+'dco_pre_route.tcl',flowDir+'/scripts/innovus/pre_route.tcl')	
	shutil.copyfile(formatDir+'dco_post_postroute.tcl',flowDir+'/scripts/innovus/post_postroute.tcl')	
	shutil.copyfile(formatDir+'dco_post_signoff.tcl',flowDir+'/scripts/innovus/post_signoff.tcl')	
	shutil.copyfile(formatDir+'pre_signoff.tcl',flowDir+'/scripts/innovus/pre_signoff.tcl')	
	shutil.copyfile(formatDir+'cadre_Makefile',flowDir+'/Makefile')	
	#--- generate  include.mk file ---
	rmkfile=open(formatDir+'/form_include.mk','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',dcoName,None,None,None)
	nm1.get_net('pf',platform,None,None,None)
	with open(flowDir+'include.mk','w') as wmkfile:
		lines_const=list(rmkfile.readlines())
		for line in lines_const:
			nm1.printline(line,wmkfile)
	#--- bleach ---
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()
	
	#--- generate verilog file ---
	rvfile=open(formatDir+'/form_dco.v','r')
	nm1=txt_mds.netmap()
	if edge_sel==1:
		nm1.get_net('IE','INCLUDE_EDGE_SEL',None,None,None)
	else:
		nm1.get_net('IE','EXCLUDE_EDGE_SEL',None,None,None)
	nm1.get_net('iN',dcoName,None,None,None)
	nm1.get_net('nM',None,nstg,nstg,1)
	nm1.get_net('nD',None,ndrv,ndrv,1)
	nm1.get_net('nF',None,nfc,nfc,1)
	nm1.get_net('nC',None,ncc,ncc,1)
	for bcnt in range (1,10):
		nm1.get_net('b%d'%(bcnt),buf_small,None,None,None)
	for zcnt in range (1,5):
		nm1.get_net('z%d'%(zcnt),bufz,None,None,None)
	nm1.get_net('B1',buf_big,None,None,None)
	with open(flowDir+'src/'+dcoName+'.v','w') as wvfile:
		lines_const=list(rvfile.readlines())
		for line in lines_const:
			nm1.printline(line,wvfile)
	#--- generate dc.filelist.tcl
	rflfile=open(formatDir+'/form_dco_dc.filelist.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',dcoName+'.v',None,None,None)
	with open(flowDir+'scripts/dc/dc.filelist.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- generate constraints.tcl
	rflfile=open(formatDir+'/form_dco_constraints.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('es',None,edge_sel,edge_sel,1)
	with open(flowDir+'scripts/dc/constraints.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- calculate area ---
	NCtotal=nstg*(ncc+ndrv)
	NFtotal=nstg*(nfc)
	A_dco=NCtotal*W_CC*H_CC+NFtotal*W_FC*H_FC
	W_dco=math.ceil(math.sqrt(A_dco)*3.0/5)*5
	H_dco=math.ceil(math.sqrt(A_dco)*3.0/5)*5
	#--- generate setup.tcl
	rsufile=open(formatDir+'/form_setup.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('mr',None,max_r_l,max_r_l,1)
	with open(flowDir+'scripts/innovus/setup.tcl','w') as wsufile:
		lines_const=list(rsufile.readlines())
		for line in lines_const:
			nm1.printline(line,wsufile)
	#--- generate always_source.tcl
	ralfile=open(formatDir+'/form_dco_always_source.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('es',None,edge_sel,edge_sel,1)
	nm1.get_net('rl',None,min_p_rng_l,min_p_rng_l,1)
	nm1.get_net('sl',None,min_p_str_l,min_p_str_l,1)
	nm1.get_net('rw',None,p_rng_w,p_rng_w,1)
	nm1.get_net('rs',None,p_rng_s,p_rng_s,1)
	nm1.get_net('2w',None,p2_rng_w,p2_rng_w,1)
	nm1.get_net('2s',None,p2_rng_s,p2_rng_s,1)
	nm1.get_net('CW',None,W_dco,W_dco,1)
	nm1.get_net('CH',None,H_dco,H_dco,1)
	with open(flowDir+'scripts/innovus/always_source.tcl','w') as walfile:
		lines_const=list(ralfile.readlines())
		for line in lines_const:
			nm1.printline(line,walfile)
	#--- generate pre_place.tcl with editPin_gen ---	
	version=2
	wfile_name=flowDir+'scripts/innovus/pre_place.tcl'
	editPin_gen(ndrv,ncc,nfc,nstg,formatDir,wfile_name)
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
		with open(flowDir + '/reports/dc/' + dcoName + '.mapped.area.rpt', \
			  'r')as file:
		   filedata = file.read()
		m = re.search('Total cell area: *([0-9.]*)', filedata)
		if m:
		   coreCellArea = float(m.group(1))
		   print('estimated area after synthesis is: %e'%(coreCellArea))
		else:
		   print ('Synthesis Failed')

	if apr==1:
		os.system('module unload calibre')
			
		os.system('module load calibre/2016.1_23.16')

		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		os.system('module unload calibre')
			
		os.system('module load calibre/2019.3_25')

		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()

		p = sp.Popen(['cp',dcoName+'_cutObs.lef','export/'+dcoName+'.lef'], cwd=flowDir)
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

def pdpll_flow(formatDir,flowDir,dco_flowDir,outbuff_div_flowDir,pll_name,dcoName,bleach,ndrv,ncc,nfc,nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir,outbuff_div,tdc_dff,buf_small,buf_big,platform,max_r_l,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,H_stdc):
	print ('#======================================================================')
	print ('# setting up flow directory for pdpll')
	print ('#======================================================================')
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	#--- copy scripts ---
	shutil.copyfile(formatDir+'pdpll_dc.include.tcl',flowDir+'/scripts/dc/dc.include.tcl')	
	shutil.copyfile(formatDir+'pdpll_dc.read_design.tcl',flowDir+'/scripts/dc/dc.read_design.tcl')	
	shutil.copyfile(formatDir+'pdpll_dc_setup.tcl',flowDir+'/scripts/dc/dc_setup.tcl')	
	shutil.copyfile(formatDir+'pdpll_report_timing.tcl',flowDir+'/scripts/dc/report_timing.tcl')	
	shutil.copyfile(formatDir+'dco_floorplan.tcl',flowDir+'/scripts/innovus/floorplan.tcl')	
	shutil.copyfile(formatDir+platform+'_pdpll_power_intent.cpf',flowDir+'/scripts/innovus/power_intent.cpf')	
	shutil.copyfile(formatDir+'pdpll_pre_init.tcl',flowDir+'/scripts/innovus/pre_init.tcl')	
	shutil.copyfile(formatDir+'pdpll_post_init.tcl',flowDir+'/scripts/innovus/post_init.tcl')	
	shutil.copyfile(formatDir+'pdpll_pre_place.tcl',flowDir+'/scripts/innovus/pre_place.tcl')	
	shutil.copyfile(formatDir+'pdpll_pre_route.tcl',flowDir+'/scripts/innovus/pre_route.tcl')	
	shutil.copyfile(formatDir+'pdpll_post_postroute.tcl',flowDir+'/scripts/innovus/post_postroute.tcl')	
	shutil.copyfile(formatDir+'pre_signoff.tcl',flowDir+'/scripts/innovus/pre_signoff.tcl')	
	shutil.copyfile(formatDir+'pdpll_post_signoff.tcl',flowDir+'/scripts/innovus/post_signoff.tcl')	
	shutil.copyfile(formatDir+'cadre_Makefile',flowDir+'/Makefile')	
	#--- copy exports from dco ---
	spfiles=glob.iglob(os.path.join(dco_flowDir+'results/calibre/lvs/','*.sp'))
	for spfile in spfiles:
		if os.path.isfile(spfile):
			shutil.copy2(spfile,dco_flowDir+'export/'+dcoName+'.cdl')
		else:
			print('Error: cant find the '+dcoName+'.sp file in'+dco_flowDir+'results/calibre/lvs/')
			sys.exit(1)
	if os.path.isdir(flowDir+'blocks/'+dcoName+'')==0:
		p = sp.Popen(['mkdir','blocks/'+dcoName+''], cwd=flowDir)
		p.wait()

	dco_ex_list=['.cdl','.lef','.gds','_typ.lib']	
	if os.path.isdir(flowDir+'blocks/'+dcoName+'/export')==0:
		shutil.copytree(dco_flowDir+'export',flowDir+'blocks/'+dcoName+'/export')
	#--- copy exports from outbuff_div ---
	if outbuff_div==1:
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
	rmkfile=open(formatDir+'/form_include.mk','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',pll_name,None,None,None)
	nm1.get_net('pf',platform,None,None,None)
	with open(flowDir+'include.mk','w') as wmkfile:
		lines_const=list(rmkfile.readlines())
		for line in lines_const:
			nm1.printline(line,wmkfile)
	#--- bleach ---
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()
	
	#--- generate verilog file ---
	rvfile=open(formatDir+'/form_pdpll.v','r')
	nm1=txt_mds.netmap()
	if outbuff_div==1:
		nm1.get_net('IO','INCLUDE_OUTBUFF_DIV',None,None,None)
	else:
		nm1.get_net('IO','EXCLUDE_OUTBUFF_DIV',None,None,None)
	nm1.get_net('iN',pll_name,None,None,None)
	nm1.get_net('nM',None,nstg,nstg,1)
	nm1.get_net('nD',None,ndrv,ndrv,1)
	nm1.get_net('nF',None,nfc,nfc,1)
	nm1.get_net('nC',None,ncc,ncc,1)
	nm1.get_net('dN',dcoName+'',None,None,None)
	for bcnt in range (1,7):
		nm1.get_net('b%d'%(bcnt),buf_small,None,None,None)
	nm1.get_net('B1',buf_big,None,None,None)
	nm1.get_net('df',tdc_dff,None,None,None)
	with open(flowDir+'src/'+pll_name+'.v','w') as wvfile:
		lines_const=list(rvfile.readlines())
		for line in lines_const:
			nm1.printline(line,wvfile)
	#--- generate dc.filelist.tcl
	rflfile=open(formatDir+'/form_pdpll_dc.filelist.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',pll_name+'.v',None,None,None)
	with open(flowDir+'/scripts/dc/dc.filelist.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- generate constraints.tcl
	rcfile=open(formatDir+'/form_pdpll_constraints.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('NS',None,2*nstg-1,2*nstg-1,1)
	nm1.get_net('nS',None,2*nstg-1,2*nstg-1,1)
	with open(flowDir+'/scripts/dc/constraints.tcl','w') as wcfile:
		lines_const=list(rcfile.readlines())
		for line in lines_const:
			nm1.printline(line,wcfile)
	#--- get dco size ---
	dco_lef=open(flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.lef','r')
	lines_dco=list(dco_lef.readlines())
	indco=0
	for line in lines_dco:
		words=line.split()
		for word in words:
			if word==dcoName+'':
				indco=1
			if indco==1 and word=='SIZE':
				sizes=line.split()
				W_dco=float(sizes[1])
				H_dco=float(sizes[3])
	if outbuff_div==1:
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
	elif outbuff_div==0:
		W_buf=0
		H_buf=0
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
	#--- generate setup.tcl
	rsufile=open(formatDir+'/form_setup.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('mr',None,max_r_l,max_r_l,1)
	with open(flowDir+'scripts/innovus/setup.tcl','w') as wsufile:
		lines_const=list(rsufile.readlines())
		for line in lines_const:
			nm1.printline(line,wsufile)
	#--- generate always_source.tcl ---
	ralfile=open(formatDir+'/form_pdpll_always_source.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('ob',None,outbuff_div,outbuff_div,1)
	nm1.get_net('mr',None,max_r_l,max_r_l,1)
	nm1.get_net('rl',None,min_p_rng_l,min_p_rng_l,1)
	nm1.get_net('sl',None,min_p_str_l,min_p_str_l,1)
	nm1.get_net('rw',None,p_rng_w,p_rng_w,1)
	nm1.get_net('rs',None,p_rng_s,p_rng_s,1)
	nm1.get_net('2w',None,p2_rng_w,p2_rng_w,1)
	nm1.get_net('2s',None,p2_rng_s,p2_rng_s,1)
	nm1.get_net('CW',None,W_pll,W_pll,1)
	nm1.get_net('CH',None,H_pll,H_pll,1)
	nm1.get_net('sH',None,H_stdc,H_stdc,1)
	nm1.get_net('bW',None,W_buf,W_buf,1)
	nm1.get_net('bH',None,H_buf,H_buf,1)
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
		os.system('module unload calibre')
			
		os.system('module load calibre/2016.1_23.16')

		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		os.system('module unload calibre')
			
		os.system('module load calibre/2019.3_25')
		
		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()

	return W_dco, H_dco, W_pll, H_pll	

#------------------------------------------------------------------------------
# custom LVS flow for welltap issues in tsmc65lp
# flowDir should be absolute path
# This funciton is especially for design using ff_dco as a Hard Macro 
#------------------------------------------------------------------------------
def pdpll_custom_lvs(VDDnames,buf,bufName,dcoName,calibreRulesDir,flowDir,extDir,formatDir,platform,designName,lvs,pex):
	# copy lvs ruleFiles
	if os.path.isdir(extDir+'ruleFiles')==0:	
		shutil.copytree(formatDir+platform+'_ext_ruleFiles',extDir+'ruleFiles')

	p = sp.Popen(['cp', flowDir+'/results/innovus/'+designName+'_lvs.v', flowDir+'/results/innovus/'+designName+'_lvs_well.v']) 
	p.wait()
	
	for VDDname in VDDnames:	
		p = sp.Popen(['vi', flowDir+'/results/innovus/'+designName+'_lvs_well.v', \
			      '-c', '%s/.VDD('+VDDname+')/.VDD('+VDDname+'), .VNW('+VDDname+'), .VPW(VSS)/g | wq'])
		p.wait()
	
	cdlInclude = ''
	cdlParse   = ''
	with open(flowDir + '/scripts/innovus/generated/' + designName + \
		  '.cdlList', 'r') as file:
	   filedata = file.readlines()
	
	for line in filedata:
	   cdlInclude = cdlInclude + ' -s ' + line.rstrip()
	   cdlParse   = cdlParse + ' -lsr ' + line.rstrip()

	if buf==0:
		p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl', flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl',
			      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-s',flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl', '-v',
		              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
		              '-o',extDir+'/sch/'+designName+'.spi','-c','/_'])
		p.wait()
	elif buf==1:
		p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl',flowDir+'/blocks/'+bufName+'/export/'+bufName+'.cdl', flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl',
			      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-s',flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl','-s',flowDir+'/blocks/'+bufName+'/export/'+bufName+'.cdl', '-v',
		              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
		              '-o',extDir+'/sch/'+designName+'.spi','-c','/_'])
		p.wait()

	# NOTE: The exported version of the gds is not merged (i.e. doesn't include standard cells)
	p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
		      extDir+'/layout/'+designName+'.gds.gz'])
	p.wait()

	# Clean the space
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.dv'):
	   os.remove(extDir + '/run/svdb/' + designName + '.dv')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.extf'):
	   os.remove(extDir + '/run/svdb/' + designName + '.extf')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.lvsf'):
	   os.remove(extDir + '/run/svdb/' + designName + '.lvsf')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.pdsp'):
	   os.remove(extDir + '/run/svdb/' + designName + '.pdsp')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.sp'):
	   os.remove(extDir + '/run/svdb/' + designName + '.sp')

	# Calibre LVS
	shutil.copy(extDir+'/ruleFiles/_calibre.lvs_',extDir+'/run/')
	with open(extDir+'/run/_calibre.lvs_', 'r') as file:
	   filedata = file.read()
	filedata = filedata.replace('design', designName)
	with open(extDir+'/run/_calibre.lvs_', 'w') as file:
	   file.write(filedata)
	
	if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdhB'):
	   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdhB', 
	                 ignore_errors=True)
	p = sp.Popen(['calibre','-spice',designName+'.sp','-lvs','-hier','-nowait',
	              '_calibre.lvs_'],cwd=extDir+'/run')
	p.wait()
	print ('INFO: custom LVS for '+designName+' is completed. check '+extDir+'/run/'+designName+'.lvs.report')

def editPin_gen(Ndrv,Ncc,Nfc,Nstg,formatDir,wfile_name):
	nCC=Ncc*Nstg
	nFC=Nfc*Nstg
	nPout=Nstg*2
	
	#rfile=open(formatDir+'/form_floorplan_test.tcl','r')
	#rfile=open('ignore_form_floorplan.tcl','r')
	rfile=open(formatDir+'/form_dco_pre_place.tcl','r')
	wfile=open(wfile_name,'w')
	
	#========================================================================
	# Version 2
	#	for floor plan.tcl: spreading out the pin
	# 	this is the 2nd version, with all the edge selection spread out,
	#	PH_P/N_out*, CLK_OUT are only concentrated in the bottom,
	#	all other pins are spread 4-side to reduce the delay mismatch between cells
	#========================================================================
	Nedge_start=Nstg*2
	eps=int(Nstg/2) # edge_per_side per either N or P
	nm2=txt_mds.netmap()
	#--- distribute EDGE_SEL ---
	nm2.get_net('el',None,0,eps-1,1)
	nm2.get_net('eL',None,Nedge_start,Nedge_start+eps-1,1)
	
	nm2.get_net('et',None,eps,2*eps-1,1)
	nm2.get_net('eT',None,Nedge_start+eps,Nedge_start+2*eps-1,1)
	
	nm2.get_net('er',None,2*eps,3*eps-1,1)
	nm2.get_net('eR',None,Nedge_start+2*eps,Nedge_start+3*eps-1,1)
	
	#--- distribute PH_P_OUT, PH_N_OUT ---
	nm2.get_net('ep',None,eps*3,eps*3+int(eps/2)-1,1)
	nm2.get_net('en',None,Nedge_start+eps*3,Nedge_start+eps*3+int(eps/2)-1,1)
	nm2.get_net('po',None,0,Nstg-1,1)
	nm2.get_net('no',None,0,Nstg-1,1)
	nm2.get_net('Po',None,Nstg,2*Nstg-1,1)
	nm2.get_net('No',None,Nstg,2*Nstg-1,1)
	nm2.get_net('Ep',None,int(eps*3.5),eps*4-1,1)
	nm2.get_net('En',None,Nedge_start+int(eps*3.5),Nedge_start+eps*4-1,1)
	
	lines=list(rfile.readlines())
	istg=0
	for line in lines:
		if line[0:2]=='@E': 
			nm1=txt_mds.netmap()
			nm1.get_net('f1','FC[',istg,istg+Nstg*(Nfc-1),Nstg)
			nm1.get_net('c1','CC[',istg,istg+Nstg*(Ncc-1),Nstg)
			nm1.printline(line,wfile)
			istg=istg+1
		else:
			nm2.printline(line,wfile)
