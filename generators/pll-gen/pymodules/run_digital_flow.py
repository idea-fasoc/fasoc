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
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp_'+platform+'.v',outDir+'/synth_pll_dco_interp.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff_'+platform+'.v',outDir+'/synth_pll_dco_outbuff.v')	
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
		rvfile=open(formatDir+'/form_ffdco.v','r')
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

def pll_verilog_gen_v2(outMode,designName,genDir,outDir,formatDir,flowDir,ndrv,ncc,nfc,nstg,verilogSrcDir,buf_small,bufz,buf_big,edge_sel,dcoName,platform,ncc_dead,dco_CC_name,dco_FC_name,buf1_name,buf2_name,buf3_name,tdc_width,Fcenter,Fbase,dFc,dFf):

	shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',outDir+'/FUNCTIONS.v')	
	shutil.copyfile(verilogSrcDir+'ssc_generator.v',outDir+'/ssc_generator.v')	
	shutil.copyfile(verilogSrcDir+'dco_CC_se_3st.v',outDir+'/dco_CC_se_3st.v')	
	shutil.copyfile(verilogSrcDir+'dco_FC_se2_half.v',outDir+'/dco_FC_se2_half.v')	
	shutil.copyfile(verilogSrcDir+'pll_controller_v2.sv',outDir+'/pll_controller.sv')	
	if outMode=='macro' or outMode=='full':
		shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',flowDir+'/src/FUNCTIONS.v')	
		shutil.copyfile(verilogSrcDir+'ssc_generator.v',flowDir+'/src/ssc_generator.v')	
		shutil.copyfile(verilogSrcDir+'dco_CC_se_3st.v',flowDir+'/src/dco_CC_se_3st.v')	
		shutil.copyfile(verilogSrcDir+'dco_FC_se2_half.v',flowDir+'/src/dco_FC_se2_half.v')	
		shutil.copyfile(verilogSrcDir+'pll_controller_v2.sv',flowDir+'/src/pll_controller.sv')	
		print(outMode,'mode: verilog sources are generated in ',flowDir,'src/')
	elif outMode=='verilog':
		print(outMode,'mode: verilog sources are generated in ',outDir)

	#--- bit-width cal. 
#	tdc_width = int(np.floor(np.log2(nstg*2)) + 2)

	#--- generate verilog file: tdc_counter_v2 ---
	r_tdc_v = open(formatDir+'/form_tdc_counter_v2.sv','r')
	nm1=txt_mds.netmap()
	nm1.get_net('ns',None,nstg,nstg,1)	
	#nm1.get_net('ew',None,tdc_width,tdc_width,1)
	# EMBTDC decoding 'case'
	nm1.get_net('Ns',None,None,nstg,nstg*2)

	ph_list_start = '1'*nstg + '0'*nstg
	ph_list=[None]*nstg	
	for stgcnt in range(nstg):
		if stgcnt==0:
			ph_list[stgcnt]=ph_list_start
		else:
			ph_list[stgcnt]=ph_list[stgcnt-1][-nstg-1:]+ph_list[stgcnt-1][:-nstg-1]

	for phcnt in range(2*nstg):
		phval=''
		for stgcnt in range(nstg):
			phval=phval+ph_list[stgcnt][phcnt]
		phval=phval[::-1]	
		#print(phval)
		if phcnt<np.floor(nstg*2/4)+1:
			retime_edge_sel = 0
			retime_lag = 0		
		elif phcnt>= np.floor(nstg*2/4)+1 and phcnt <np.floor(nstg*2/4)*3+1:
			retime_edge_sel = 1	
			retime_lag = 0		
		else:
			retime_edge_sel = 0	
			retime_lag = 1		
		#nm1.get_net('er',phval,None,None,None)
		nm1.get_net('er',None,phval,phval,1)
		nm1.get_net('ei',None,phcnt,phcnt,1)
		nm1.get_net('re',None,retime_edge_sel,retime_edge_sel,1)
		nm1.get_net('rl',None,retime_lag,retime_lag,1)

	with open(outDir+'/tdc_counter.sv','w') as wvfile:
		lines_tdc=list(r_tdc_v.readlines())
		for line in lines_tdc:
			nm1.printline(line,wvfile)

	#--- generate verilog file ---
	r_pll_v=open(formatDir+'/form_pll_top_v2.sv','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',designName,None,None,None)
	nm1.get_net('nM',None,nstg,nstg,1)
	nm1.get_net('nC',None,ncc,ncc,1)
	nm1.get_net('nF',None,nfc,nfc,1)

	# DCO analog performance
	nm1.get_net('CF',None,Fcenter,Fcenter,1)
	nm1.get_net('FB',None,Fbase,Fbase,1)
	nm1.get_net('CS',None,dFc,dFc,1)
	nm1.get_net('FS',None,dFf,dFf,1)

	nm1.get_net('ew',None,tdc_width,tdc_width,1)
	nm1.get_net('dN',dcoName,None,None,None)
	with open(outDir+'/'+designName+'.sv','w') as wvfile:
		lines_pll=list(r_pll_v.readlines())
		for line in lines_pll:
			nm1.printline(line,wvfile)

	#--- generate verilog file: DCO ---
	rvfile=open(formatDir+'/form_dco_v2.v','r')
	nm1=txt_mds.netmap()
	if edge_sel==1:
		nm1.get_net('IE','INCLUDE_EDGE_SEL',None,None,None)
	else:
		nm1.get_net('IE','EXCLUDE_EDGE_SEL',None,None,None)
	# design params
	nm1.get_net('iN',dcoName,None,None,None)
	nm1.get_net('nM',None,nstg,nstg,1)
	nm1.get_net('nD',None,ndrv,ndrv,1)
	nm1.get_net('nC',None,ncc,ncc,1)
	nm1.get_net('nF',None,nfc,nfc,1)
	nm1.get_net('ND',None,ncc_dead,ncc_dead,1)
	
	# cell names
	nm1.get_net('cN',dco_CC_name,None,None,None)
	nm1.get_net('Cn',dco_CC_name,None,None,None)
	nm1.get_net('CN',dco_CC_name,None,None,None)
	nm1.get_net('fN',dco_FC_name,None,None,None)
	nm1.get_net('b1',buf1_name,None,None,None)
	nm1.get_net('dn',dco_CC_name,None,None,None)
	nm1.get_net('Dn',dco_CC_name,None,None,None)
	nm1.get_net('dN',dco_CC_name,None,None,None)
	nm1.get_net('DN',dco_CC_name,None,None,None)
	nm1.get_net('FN',dco_FC_name,None,None,None)
	nm1.get_net('b2',buf1_name,None,None,None)
	nm1.get_net('b3',buf1_name,None,None,None)
	nm1.get_net('b4',buf2_name,None,None,None)
	nm1.get_net('b5',buf3_name,None,None,None)
	with open(outDir+'/'+dcoName+'.v','w') as wvfile:
		lines_const=list(rvfile.readlines())
		for line in lines_const:
			nm1.printline(line,wvfile)


#------------------------------------------------------------------------------
# generates ff_dco
#------------------------------------------------------------------------------
def dco_flow(formatDir,flowDir,dcoName,bleach,ndrv,ncc,nfc,nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir,platform,edge_sel,buf_small,buf_big,bufz,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,max_r_l,cust_place,single_ended,FC_half,CC_stack,dco_CC_name,dco_FC_name, dcocp_version, welltap_dim, welltap_xc,ND,outputDir):
	print ('#======================================================================')
	print('# setting up flow directory for dco')
	print ('#======================================================================')
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	#--- copy verilog files to flowDir/src/ ---
	shutil.copyfile(verilogSrcDir+'/'+dco_CC_name+'.v',flowDir+'/src/'+dco_CC_name+'.v')	
	shutil.copyfile(verilogSrcDir+'/'+dco_FC_name+'.v',flowDir+'/src/'+dco_FC_name+'.v')
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp_'+platform+'.v',flowDir+'/src/synth_pll_dco_interp.v')	
	shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff_'+platform+'.v',flowDir+'/src/synth_pll_dco_outbuff.v')	
	shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',flowDir+'/src/FUNCTIONS.v')	
	#--- copy scripts files to flowDir/scripts/ ---
	shutil.copyfile(formatDir+'dco_dc.include.tcl',flowDir+'/scripts/dc/dc.include.tcl')	
	shutil.copyfile(formatDir+'dco_dc.read_design.tcl',flowDir+'/scripts/dc/dc.read_design.tcl')	
	shutil.copyfile(formatDir+'dco_dc_setup.tcl',flowDir+'/scripts/dc/dc_setup.tcl')	
	shutil.copyfile(formatDir+'dco_report_timing.tcl',flowDir+'/scripts/dc/report_timing.tcl')	
	shutil.copyfile(formatDir+'dco_floorplan.tcl',flowDir+'/scripts/innovus/floorplan.tcl')	
	shutil.copyfile(formatDir+'pdpll_pre_init.tcl',flowDir+'/scripts/innovus/pre_init.tcl')	
	shutil.copyfile(formatDir+'dco_power_intent.cpf',flowDir+'/scripts/innovus/power_intent.cpf')	
	shutil.copyfile(formatDir+platform+'_dco_post_init.tcl',flowDir+'/scripts/innovus/post_init.tcl')	
	shutil.copyfile(formatDir+'dco_pre_route.tcl',flowDir+'/scripts/innovus/pre_route.tcl')	
	shutil.copyfile(formatDir+'dco_post_postroute.tcl',flowDir+'/scripts/innovus/post_postroute.tcl')	
	shutil.copyfile(formatDir+'dco_post_signoff.tcl',flowDir+'/scripts/innovus/post_signoff.tcl')	
	shutil.copyfile(formatDir+'pre_signoff.tcl',flowDir+'/scripts/innovus/pre_signoff.tcl')	
	shutil.copyfile(formatDir+'dcoPowerPlanGf14.tcl',flowDir+'/scripts/innovus/dcoPowerPlanGf14.tcl')	
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
	#--- generate verilog file ---
	nm1=txt_mds.netmap()
	if platform=='gf12lp':
		shutil.copyfile(outputDir+'/'+dcoName+'.v',flowDir+'/src/'+dcoName+'.v')	
	elif single_ended==0:
		rvfile=open(formatDir+'/form_dco.v','r')
		if edge_sel==1:
			nm1.get_net('IE','INCLUDE_EDGE_SEL',None,None,None)
		else:
			nm1.get_net('IE','EXCLUDE_EDGE_SEL',None,None,None)
		nm1.get_net('iN',dcoName,None,None,None)
		nm1.get_net('nM',None,nstg,nstg,1)
		nm1.get_net('nD',None,ndrv,ndrv,1)
		nm1.get_net('nF',None,nfc,nfc,1)
		nm1.get_net('nC',None,ncc,ncc,1)
		nm1.get_net('NC',dco_CC_name,None,None,None)
		nm1.get_net('Nc',dco_CC_name,None,None,None)
		for bcnt in range (1,10):
			nm1.get_net('b%d'%(bcnt),buf_small,None,None,None)
		for zcnt in range (1,5):
			nm1.get_net('z%d'%(zcnt),bufz,None,None,None)
		nm1.get_net('B1',buf_big,None,None,None)
		nm1.get_net('CN',dco_CC_name,None,None,None)
		nm1.get_net('cN',dco_CC_name,None,None,None)
		nm1.get_net('Cn',dco_CC_name,None,None,None)
	else:
		if FC_half==0:
			if ND==0:
				rvfile=open(formatDir+'/form_dco_se.v','r')
			else:
				rvfile=open(formatDir+'/form_dco_se_dCC.v','r')
		elif FC_half==1:
			if ND==0:
				rvfile=open(formatDir+'/form_dco_se_halfFC.v','r')
			else:
				rvfile=open(formatDir+'/form_dco_se_halfFC_dCC.v','r')
		nm1.get_net('iN',dcoName,None,None,None)
		nm1.get_net('nM',None,nstg,nstg,1)
		nm1.get_net('nD',None,ndrv,ndrv,1)
		nm1.get_net('nF',None,nfc,nfc,1)
		nm1.get_net('nC',None,ncc,ncc,1)
		if ND>0:
			nm1.get_net('ND',None,ND,ND,1)
			nm1.get_net('CC',dco_CC_name,None,None,None)
		nm1.get_net('NC',dco_CC_name,None,None,None)
		nm1.get_net('Nc',dco_CC_name,None,None,None)
		nm1.get_net('Nf',dco_FC_name,None,None,None)
		for bcnt in range (1,3):
			nm1.get_net('b%d'%(bcnt),buf_small,None,None,None)
		nm1.get_net('B1',buf_big,None,None,None)
		if ND>0:
			nm1.get_net('DL',dco_CC_name,None,None,None)
		nm1.get_net('CN',dco_CC_name,None,None,None)
		nm1.get_net('cN',dco_CC_name,None,None,None)
		nm1.get_net('Cn',dco_CC_name,None,None,None)
		nm1.get_net('NF',dco_FC_name,None,None,None)
	if platform!='gf12lp':
		with open(flowDir+'src/'+dcoName+'.v','w') as wvfile:
			lines_const=list(rvfile.readlines())
			for line in lines_const:
				nm1.printline(line,wvfile)
	#--- generate dc.filelist.tcl
	rflfile=open(formatDir+'/form_dco_dc.filelist.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',dcoName+'.v',None,None,None)
	nm1.get_net('Nc',dco_CC_name,None,None,None)
	nm1.get_net('Nf',dco_FC_name,None,None,None)
	with open(flowDir+'scripts/dc/dc.filelist.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- generate constraints.tcl
	rflfile=open(formatDir+'/form_dco_constraints.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('es',None,edge_sel,edge_sel,1)
	nm1.get_net('SE',None,single_ended,single_ended,1)
	with open(flowDir+'scripts/dc/constraints.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- calculate area ---
	NCtotal=nstg*(ncc+ndrv)
	NFtotal=nstg*(nfc)
	A_dco=NCtotal*W_CC*H_CC+NFtotal*W_FC*H_FC
	if cust_place==0:
		W_dco=math.ceil(math.sqrt(A_dco)*2.2/2)*3  # 01_09_2021
		H_dco=math.ceil(math.sqrt(A_dco)*2.2/2)*3  # 01_09_2021
	else:
		nspace=1
		#nxoff=4
		nxoff=14
		nyoff=6
		#W_dco=math.ceil((W_CC*ncc+W_FC*nfc)*2.2/5)*5
		#H_dco=math.ceil(H_CC*nstg*2.2/5)*5

		#W_dco=math.ceil((W_CC*ncc+W_FC*nfc+nxoff*W_FC*2.5)/2)*2
		#H_dco=math.ceil((H_CC*nstg+H_CC*nyoff*2)/2)*2
		if FC_half==0:
			W_dco=math.ceil((W_CC*ncc+W_FC*nfc+nxoff*W_FC)/2)*2
			H_dco=math.ceil((H_CC*nstg+H_CC*nyoff*4)/2)*2
		elif FC_half==1:
			if ND==0:
				W_dco=math.ceil((W_CC*ncc+W_FC*nfc+nxoff*W_FC*2)/2)*2
			elif ND>0:
				W_dco=math.ceil((W_CC*ncc+W_FC*nfc+nxoff*W_FC*2+W_CC*ND)/2)*2
			H_dco=math.ceil((H_CC*nstg+H_CC*nyoff*8)/2)*2
		if dcocp_version==1:
			dco_custom_place(formatDir,flowDir+'scripts/innovus/',[W_CC, H_CC],[W_FC, H_FC],ncc,int(nfc/2),nstg,ndrv,nspace,nxoff,nyoff)
		elif dcocp_version==2:
		#	dco_custom_place_v2(formatDir,flowDir+'scripts/innovus/',[W_CC, H_CC],[W_FC, H_FC],ncc,int(nfc/2),nstg,ndrv,nspace,nxoff,nyoff,welltap_dim,welltap_xc)
			dco_custom_place_v2p5(formatDir,flowDir+'scripts/innovus/',[W_CC, H_CC],[W_FC, H_FC],ncc,int(nfc/2),nstg,ndrv,nspace,nxoff,nyoff,welltap_dim,welltap_xc,ND)
	#--- generate setup.tcl
	rsufile=open(formatDir+'/form_setup.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('mr',None,max_r_l,max_r_l,1)
	with open(flowDir+'scripts/innovus/setup.tcl','w') as wsufile:
		lines_const=list(rsufile.readlines())
		for line in lines_const:
			nm1.printline(line,wsufile)
	#--- generate custom_place.tcl
	#--- generate always_source.tcl
	ralfile=open(formatDir+'/form_dco_always_source.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('es',None,edge_sel,edge_sel,1)
	nm1.get_net('cP',None,cust_place,cust_place,1)
	nm1.get_net('sE',None,single_ended,single_ended,1)
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
	if single_ended==0: 
		editPin_gen(ndrv,ncc,nfc,nstg,formatDir,wfile_name)
	elif single_ended==1: 
		editPin_gen_se(ndrv,ncc,nfc,nstg,formatDir,wfile_name,platform)
	print ('#======================================================================')
	print('# ready for synth & apr')
	print ('#======================================================================')
	#--- bleach ---
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()
	
	if synth==1:
		#-------------------------------------------
		# run CADRE flow 
		#-------------------------------------------
		p = sp.Popen(['make','synth'], cwd=flowDir)
		p.wait()
	# read total estimated area of controller (it doesn't include the aux-cells)
		if bleach==1:
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
		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()
		
		if platform=='gf12lp':
			for file in glob.glob(flowDir+'/results/calibre/lvs/_'+dcoName+'*.sp'):
				shutil.copy(file, flowDir+'/export/'+dcoName+'.cdl')

		if platform=='tsmc65lp':
			p = sp.Popen(['cp',dcoName+'_cutObs.lef','export/'+dcoName+'.lef'], cwd=flowDir)
			p.wait()
	return W_dco, H_dco	

#------------------------------------------------------------------------------
# generates outbuff_div
#	current version of outbuff_div is not configurable. Below are the programmable options
#	1. Divide ratio: 1~64 (only 2^N works)
#	2. buffer power: 1~16 
#------------------------------------------------------------------------------
def outbuff_div_flow(formatDir,flowDir,bufName,platform,bleach,design):
	# copy scripts, src, Makefile
	if os.path.isdir(flowDir+'scripts')==0:	
		shutil.copytree(formatDir+'buf_scripts',flowDir+'/scripts')
		shutil.copytree(formatDir+'buf_src',flowDir+'/src')
		shutil.copyfile(formatDir+'cadre_Makefile',flowDir+'/Makefile')	

	#--- generate  include.mk file ---
	rmkfile=open(formatDir+'/form_include.mk','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',bufName,None,None,None)
	nm1.get_net('pf',platform,None,None,None)
	with open(flowDir+'include.mk','w') as wmkfile:
		lines_const=list(rmkfile.readlines())
		for line in lines_const:
			nm1.printline(line,wmkfile)

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

def pdpll_flow(formatDir,flowDir,dco_flowDir,outbuff_div_flowDir,pll_name,dcoName,bleach,ndrv,ncc,nfc,nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir,outbuff_div,tdc_dff,buf_small,buf_big,platform,max_r_l,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,H_stdc,FCW,vco_per,outputDir):
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
	shutil.copyfile(formatDir+platform+'_floorplan.tcl',flowDir+'/scripts/innovus/floorplan.tcl')	
	shutil.copyfile(formatDir+platform+'_pdpll_power_intent.cpf',flowDir+'/scripts/innovus/power_intent.cpf')	
	shutil.copyfile(formatDir+'pdpll_pre_init.tcl',flowDir+'/scripts/innovus/pre_init.tcl')	
	shutil.copyfile(formatDir+platform+'_pdpll_post_init.tcl',flowDir+'/scripts/innovus/post_init.tcl')	
	shutil.copyfile(formatDir+platform+'_pdpll_pre_place.tcl',flowDir+'/scripts/innovus/pre_place.tcl')	
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

	#--- get DCO pin location
	if platform=='gf12lp':
		#shutil.copyfile(formatDir+'gf12lp_pdpllPowerPlanGf12.tcl',flowDir+'/scripts/innovus/pdpllPowerPlanGf12.tcl')	
		dcoLefFile = open(flowDir+'blocks/'+dcoName+'/export/'+dcoName+'.lef','r')
		lines_lef = list(dcoLefFile.readlines())
		VDD_flag=0
		OBS_flag=0
		OBS_H2_flag=0
		END_flag=0
		H2_flag=0
		xy_found=0
		delete_line =0
		write_lines=[]
		for line in lines_lef:
			words = line.split()
			if len(words)>0:
				if OBS_flag==0 and words[0]=='OBS':
					print('INFO: OBS found in dco lef file')
					OBS_flag=1
				elif OBS_flag==1 and OBS_H2_flag==1 and END_flag==0:
					if words[0]!='RECT':
						END_flag=1
						delete_line =0
			if len(words)>1:
				if VDD_flag==0:
					if words[0]=='PIN' and words[1]=='VDD':
						print('INFO: PIN VDD found in dco lef file')
						VDD_flag=1
				elif H2_flag==0:
					if words[1]=='H2':
						H2_flag=1
				elif H2_flag==1 and xy_found==0:
					pin_llx = float(words[1])	
					pin_lly = float(words[2])		
					pin_urx = float(words[3])		
					pin_ury = float(words[4])
					print('pin coordinates: (%.3f, %.3f) ~ (%.3f, %.3f)'%(pin_llx,pin_lly,pin_urx,pin_ury))
					xy_found=1

				#elif OBS_flag==0:
				elif OBS_flag==1 and OBS_H2_flag==0:
					if words[1]=='H2':
						print('INFO: H2 layer found in OBS')
						OBS_H2_flag=1
						delete_line =1
						#delete_line =0
				elif END_flag==1:
					delete_line =0
			# append lines except when delete_line==1 
			if delete_line==0:
				write_lines.append(line)	
		with open(flowDir+'blocks/'+dcoName+'/export/'+dcoName+'.lef','w') as wlef:
			for line in write_lines:
				wlef.write(line)


		rpp=open(formatDir+'/form_'+platform+'_pdpllPowerPlan.tcl','r')
		nm1=txt_mds.netmap()
		nm1.get_net('vo',None,pin_llx,pin_llx,1)
		with open(flowDir+'scripts/innovus/pdpllPowerPlanGf12.tcl','w') as wpp:
			lines_pp=list(rpp.readlines())
			for line in lines_pp:
				nm1.printline(line,wpp)


		rpp=open(formatDir+'/form_'+platform+'_pdpll_pre_place.tcl','r')
		nm1=txt_mds.netmap()
		nm1.get_net('lx',None,pin_llx,pin_llx,1)
		nm1.get_net('ly',None,pin_lly,pin_lly,1)
		nm1.get_net('ux',None,pin_urx,pin_urx,1)
		nm1.get_net('uy',None,pin_ury,pin_ury,1)
		with open(flowDir+'scripts/innovus/pre_place.tcl','w') as wpp:
			lines_pp=list(rpp.readlines())
			for line in lines_pp:
				nm1.printline(line,wpp)

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
	
	#--- generate verilog file : need to clean it up to be technology agnostic 
	if platform=='tsmc65lp':
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
	elif platform=='gf12lp':
		shutil.copyfile(outputDir+'/'+pll_name+'.sv',flowDir+'/src/'+pll_name+'.sv')	
		shutil.copyfile(outputDir+'/tdc_counter.sv',flowDir+'/src/tdc_counter.sv')
	
	#--- generate dc.filelist.tcl
	rflfile=open(formatDir+'/form_'+platform+'_pdpll_dc.filelist.tcl','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',pll_name,None,None,None)
	with open(flowDir+'/scripts/dc/dc.filelist.tcl','w') as wflfile:
		lines_const=list(rflfile.readlines())
		for line in lines_const:
			nm1.printline(line,wflfile)
	#--- generate constraints.tcl
	rcfile=open(formatDir+'/form_'+platform+'_pdpll_constraints.tcl','r')
	nm1=txt_mds.netmap()
	if platform=='tsmc65lp':
		nm1.get_net('NS',None,2*nstg-1,2*nstg-1,1)
		nm1.get_net('nS',None,2*nstg-1,2*nstg-1,1)
	elif platform=='gf12lp':
		nm1.get_net('vp',None,vco_per*1e3,vco_per*1e3,1)
		nm1.get_net('db',None,FCW,FCW,1)

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
		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
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

def buf_custom_lvs(calibreRulesDir,flowDir,extDir,designName,formatDir,platform):
	# copy lvs ruleFiles
	if os.path.isdir(extDir+'ruleFiles')==0:	
		shutil.copytree(formatDir+platform+'_ext_ruleFiles',extDir+'ruleFiles')

	# Generate pre PEX netlist and gds files
	p = sp.Popen(['cp', flowDir+'/results/innovus/'+designName+'_lvs.v', flowDir+'/results/innovus/'+designName+'_lvs_well.v']) 
	p.wait()
	
	p = sp.Popen(['vi', flowDir+'/results/innovus/'+designName+'_lvs_well.v', \
		      '-c', '%s/.VDD(VDD)/.VDD(VDD), .VNW(VDD), .VPW(VSS)/g | wq'])
	p.wait()
	
	cdlInclude = ''
	cdlParse   = ''
	with open(flowDir + '/scripts/innovus/generated/' + designName + \
		  '.cdlList', 'r') as file:
	   filedata = file.readlines()
	
	for line in filedata:
	   cdlInclude = cdlInclude + ' -s ' + line.rstrip()
	   cdlParse   = cdlParse + ' -lsr ' + line.rstrip()

	p = sp.Popen(['v2lvs', cdlParse,
		      cdlInclude,'-v',
	              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
	              '-o',extDir+'/sch/'+designName+'.spi','-i','-c','/_'])
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
	p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.lvs_',extDir+'/run/'])
	p.wait()
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
	print ('# OUTBUFF_DIV - LVS completed. check '+extDir+'/run/'+designName+'.lvs.report')

def dco_custom_place(formatDir,outputDir,crscell_dim,finecell_dim,ncrs,nfine_h,nstg,ndrv,nspace,nxoff,nyoff):
	r_c = open(formatDir+"form_dco_custom_place.tcl","r")
	lines=list(r_c.readlines())

	crs_w=crscell_dim[0]
	crs_h=crscell_dim[1]
	fine_w=finecell_dim[0]
	fine_h=finecell_dim[1]
	xoff=nxoff*fine_w	
	yoff=nyoff*fine_h

	xfl_end=xoff+nfine_h*fine_w
	xd_start=xfl_end + nspace*fine_w	
	xd_end=xd_start + ndrv*crs_w
	xc_end=xd_end + ncrs*crs_w
	xfr_start=xc_end + nspace*fine_w
	netmap1=txt_mds.netmap()
	for ig in range(nstg): # for each stage
		#---------------------------------------------
		# place fine cells
		#---------------------------------------------
		for cntf in range(nfine_h*2):
			if ig!=nstg-1:	
				netmap1.get_net('NS',None,ig,ig,1) # stg
			else:
				netmap1.get_net('NS',None,None,'last',1) # stg
			netmap1.get_net('nf',None,cntf,cntf,1) # fine cell
			if cntf < nfine_h:
				netmap1.get_net('LX', None, xoff+cntf*fine_w, xoff+cntf*fine_w, 1) # X coordinate 
			else:
				netmap1.get_net('LX',None, xfr_start+(cntf-nfine_h)*fine_w, xfr_start+(cntf-nfine_h)*fine_w, 1) # X coordinate 
			netmap1.get_net('LY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 
		#---------------------------------------------
		# place driver cells
		#---------------------------------------------
		for cntd in range(ndrv):
			if ig!=nstg-1:	
				netmap1.get_net('ns',None,ig,ig,1) # stg
			else:
				netmap1.get_net('ns',None,None,'last',1) # stg
			netmap1.get_net('nd',None,cntd,cntd,1) # driver cell 
			netmap1.get_net('lx',None, xd_start+cntd*crs_w, xd_start+cntd*crs_w, 1) # X coordinate 
			netmap1.get_net('ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 
		#---------------------------------------------
		# place coarse cells
		#---------------------------------------------
		for cntc in range(ncrs):
			if ig!=nstg-1:	
				netmap1.get_net('Ns',None,ig,ig,1) # stg
			else:
				netmap1.get_net('Ns',None,None,'last',1) # stg
			netmap1.get_net('nc',None,cntc,cntc,1) # coarse cell 
			netmap1.get_net('Lx',None, xd_end+cntc*crs_w, xd_end+cntc*crs_w, 1) # X coordinate 
			netmap1.get_net('Ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 

	with open(outputDir+"custom_place.tcl","w") as w_tcl:
		for line in lines:
			netmap1.printline(line,w_tcl)

def dltdc_custom_place(formatDir,outputDir,crscell_dim,finecell_dim,dff_dim,ncrs,nfine_h,nstg,ndrv,nspace,nxoff,nyoff, version, ndrv_ref, ncrs_ref):
	if nfine_h!=0 and version<3:
		r_c = open(formatDir+"form_dltdc_custom_place.tcl","r")
	elif version==1:
		r_c = open(formatDir+"form_dltdc_custom_place_noFC.tcl","r")
	elif version==2:
		r_c = open(formatDir+"form_dltdc_custom_place_noFC_v2.tcl","r")
	elif version==3 and nfine_h==0:
		r_c = open(formatDir+"form_dltdc_custom_place_noFC_v3.tcl","r")
	elif version==3 and nfine_h!=0:
		r_c = open(formatDir+"form_dltdc_custom_place_v3.tcl","r")
	lines=list(r_c.readlines())

	crs_w=crscell_dim[0]
	crs_h=crscell_dim[1]
	fine_w=finecell_dim[0]
	fine_h=finecell_dim[1]
	dff_w=dff_dim[0]
	dff_h=dff_dim[1]
	xoff=nxoff*fine_w	
	yoff=nyoff*fine_h

	if version==1 or version==2:
		xfl_end=xoff+nfine_h*fine_w
		xd_start=xfl_end + nspace*fine_w	
		xd_end=xd_start + ndrv*crs_w
		xc_end=xd_end + ncrs*crs_w
		xfr_start=xc_end + nspace*fine_w
		xfr_end=xfr_start+fine_w*nfine_h
		xdff_start=xfr_end+nspace*fine_w
		xdff_end=xdff_start+dff_w
		xdr_start=xdff_end+nspace*fine_w
		xdr_end=xdr_start+ndrv*crs_w
	elif version==3:
		xfl_end=xoff+nfine_h*2*fine_w
		xd_start=xfl_end + nspace*fine_w	
		xd_end=xd_start + ndrv*crs_w*2
		xc_end=xd_end + ncrs*crs_w*2
		xdff_start=xc_end+nspace*fine_w
		xdff_end=xdff_start+dff_w
		xdr_start=xdff_end+nspace*fine_w
		xdr_end=xdr_start+ndrv_ref*crs_w*2
		xcr_start=xdr_end
		xcr_end=xcr_start+ncrs_ref*crs_w*2
		xfr_start=xcr_end + nspace*fine_w # ref
		xfr_end=xfr_start+fine_w*2*nfine_h
	netmap1=txt_mds.netmap()
	for ig in range(nstg): # for each stage
		if version==1 or version==2:
			#---------------------------------------------
			# place fine cells
			#---------------------------------------------
			for cntf in range(nfine_h*2):
				netmap1.get_net('NS',None,ig,ig,1) # stg
				netmap1.get_net('nf',None,cntf,cntf,1) # fine cell
				if cntf < nfine_h:
					netmap1.get_net('LX', None, xoff+cntf*fine_w, xoff+cntf*fine_w, 1) # X coordinate 
				else:
					netmap1.get_net('LX',None, xfr_start+(cntf-nfine_h)*fine_w, xfr_start+(cntf-nfine_h)*fine_w, 1) # X coordinate 
				netmap1.get_net('LY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 
			#---------------------------------------------
			# place driver cells
			#---------------------------------------------
			for cntd in range(ndrv):
				netmap1.get_net('ns',None,ig,ig,1) # stg
				netmap1.get_net('nd',None,cntd,cntd,1) # driver cell 
				netmap1.get_net('lx',None, xd_start+cntd*crs_w, xd_start+cntd*crs_w, 1) # X coordinate 
				netmap1.get_net('ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
				if version==2: 
					netmap1.get_net('rs',None,ig,ig,1) # stg
					netmap1.get_net('rd',None,cntd,cntd,1) # driver cell 
					netmap1.get_net('rx',None, xdr_start+cntd*crs_w, xdr_start+cntd*crs_w, 1) # X coordinate 
					netmap1.get_net('ry',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
			#---------------------------------------------
			# place coarse cells
			#---------------------------------------------
			for cntc in range(ncrs):
				netmap1.get_net('Ns',None,ig,ig,1) # stg
				netmap1.get_net('nc',None,cntc,cntc,1) # coarse cell 
				netmap1.get_net('Lx',None, xd_end+cntc*crs_w, xd_end+cntc*crs_w, 1) # X coordinate 
				netmap1.get_net('Ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 
				if version==2:
					netmap1.get_net('Rs',None,ig,ig,1) # stg
					netmap1.get_net('Rc',None,cntc,cntc,1) # coarse cell 
					netmap1.get_net('Rx',None, xdr_end+cntc*crs_w, xdr_end+cntc*crs_w, 1) # X coordinate 
					netmap1.get_net('Ry',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
		elif version==3:
			for cntf in range(nfine_h*2):
				# for fb path
				netmap1.get_net('fs',None,ig,ig,1) # stg
				netmap1.get_net('nf',None,cntf,cntf,1) # fine cell
				netmap1.get_net('fx', None, xoff+cntf*fine_w, xoff+cntf*fine_w, 1) # X coordinate 
				netmap1.get_net('fy',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
				# for ref path 
				netmap1.get_net('FS',None,ig,ig,1) # stg
				netmap1.get_net('NF',None,cntf,cntf,1) # fine cell
				netmap1.get_net('FX', None, xfr_start+cntf*fine_w, xfr_start+cntf*fine_w, 1) # X coordinate 
				netmap1.get_net('FY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 
			for cntd in range(ndrv):
				netmap1.get_net('ns',None,ig,ig,1) # stg
				netmap1.get_net('nd',None,cntd,cntd,1) # driver cell 
				netmap1.get_net('lx',None, xd_start+cntd*crs_w*2, xd_start+cntd*crs_w*2, 1) # X coordinate 
				netmap1.get_net('ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
				netmap1.get_net('NS',None,ig,ig,1) # stg
				netmap1.get_net('ND',None,cntd,cntd,1) # driver cell 
				netmap1.get_net('LX',None, xd_start+cntd*crs_w*2+crs_w, xd_start+cntd*crs_w*2+crs_w, 1) # X coordinate 
				netmap1.get_net('LY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
			for cntd in range(ndrv_ref):
				netmap1.get_net('rs',None,ig,ig,1) # stg
				netmap1.get_net('rd',None,cntd,cntd,1) # driver cell 
				netmap1.get_net('rx',None, xdr_start+cntd*crs_w*2, xdr_start+cntd*crs_w*2, 1) # X coordinate 
				netmap1.get_net('ry',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
				netmap1.get_net('RS',None,ig,ig,1) # stg
				netmap1.get_net('RD',None,cntd,cntd,1) # driver cell 
				netmap1.get_net('RX',None, xdr_start+cntd*crs_w*2+crs_w, xdr_start+cntd*crs_w*2+crs_w, 1) # X coordinate 
				netmap1.get_net('RY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
			for cntc in range(ncrs):
				netmap1.get_net('Ns',None,ig,ig,1) # stg
				netmap1.get_net('nc',None,cntc,cntc,1) # coarse cell 
				netmap1.get_net('Lx',None, xd_end+cntc*crs_w*2, xd_end+cntc*crs_w*2, 1) # X coordinate 
				netmap1.get_net('Ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 
				netmap1.get_net('cS',None,ig,ig,1) # stg
				netmap1.get_net('nC',None,cntc,cntc,1) # coarse cell 
				netmap1.get_net('cX',None, xd_end+cntc*crs_w*2+crs_w, xd_end+cntc*crs_w*2+crs_w, 1) # X coordinate 
				netmap1.get_net('cY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
			for cntc in range(ncrs_ref):
				netmap1.get_net('Rs',None,ig,ig,1) # stg
				netmap1.get_net('Rc',None,cntc,cntc,1) # coarse cell 
				netmap1.get_net('Rx',None, xdr_end+cntc*crs_w*2, xdr_end+cntc*crs_w*2, 1) # X coordinate 
				netmap1.get_net('Ry',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
				netmap1.get_net('rS',None,ig,ig,1) # stg
				netmap1.get_net('rC',None,cntc,cntc,1) # coarse cell 
				netmap1.get_net('rX',None, xdr_end+cntc*crs_w*2+crs_w, xdr_end+cntc*crs_w*2+crs_w, 1) # X coordinate 
				netmap1.get_net('rY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
		#---------------------------------------------
		# place dffs 
		#---------------------------------------------
		netmap1.get_net('nS',None,ig,ig,1) # stg
	#	netmap1.get_net('lX',None, xfr_end+nspace*fine_w, xfr_end+nspace*fine_w, 1) # X coordinate 
		netmap1.get_net('lX',None, xdff_start, xdff_start, 1) # X coordinate 
		netmap1.get_net('lY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 

	with open(outputDir+"custom_place.tcl","w") as w_tcl:
		for line in lines:
			netmap1.printline(line,w_tcl)

# v2 considers welltap placements and skips the cell placements near them
# welltap_xc is a list of x-coordinates where the welltaps are placed
def dco_custom_place_v2(formatDir,outputDir,crscell_dim,finecell_dim,ncrs,nfine_h,nstg,ndrv,nspace,nxoff,nyoff, welltap_dim, welltap_xc):
	r_c = open(formatDir+"form_dco_custom_place.tcl","r")
	lines=list(r_c.readlines())

	welltap_w=welltap_dim[0]
	crs_w=crscell_dim[0]
	crs_h=crscell_dim[1]
	fine_w=finecell_dim[0]
	fine_h=finecell_dim[1]
	xoff=nxoff*fine_w	
	yoff=nyoff*fine_h

#	xfl_end=xoff+nfine_h*fine_w
#	xd_start=xfl_end + nspace*fine_w	
#	xd_end=xd_start + ndrv*crs_w
#	xc_end=xd_end + ncrs*crs_w
#	xfr_start=xc_end + nspace*fine_w
	netmap1=txt_mds.netmap()
	skip=0
	for ig in range(nstg): # for each stage
		#---------------------------------------------
		# place left fine cells
		#---------------------------------------------
		for cntf in range(nfine_h):
			if ig!=nstg-1:	
				netmap1.get_net('NS',None,ig,ig,1) # stg
			else:
				netmap1.get_net('NS',None,None,'last',1) # stg
			netmap1.get_net('nf',None,cntf,cntf,1) # fine cell
			if cntf==0:
				xtry=xoff
			else:
				xtry=xcor+fine_w
			xcor,skip=xcorCal_skipwt(xtry, fine_w, welltap_w, welltap_xc, fine_w)
			netmap1.get_net('LX', None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('LY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
			if cntf==nfine_h-1:
				xfl_end=xcor+fine_w
				#print("xfl_end=%.3e"%(xfl_end))
			#print("%.2e, %d"%(xcor,skip))
			
		#---------------------------------------------
		# place driver cells
		#---------------------------------------------
		xd_start=xfl_end+nspace*fine_w
		for cntd in range(ndrv):
			if ig!=nstg-1:	
				netmap1.get_net('ns',None,ig,ig,1) # stg
			else:
				netmap1.get_net('ns',None,None,'last',1) # stg
			if cntd==0:
				xtry=xd_start
			else:
				xtry=xcor+crs_w
			netmap1.get_net('nd',None,cntd,cntd,1) # driver cell 
			xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
			#print("%.2e, %d"%(xcor,skip))
			netmap1.get_net('lx',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
			if cntd==ndrv-1:
				xd_end=xcor+crs_w 
				#print("xd_end=%.3e"%(xd_end))
		#---------------------------------------------
		# place coarse cells
		#---------------------------------------------
		for cntc in range(ncrs):
			if ig!=nstg-1:	
				netmap1.get_net('Ns',None,ig,ig,1) # stg
			else:
				netmap1.get_net('Ns',None,None,'last',1) # stg
			if cntc==0:
				xtry=xd_end
			else:
				xtry=xcor+crs_w
			netmap1.get_net('nc',None,cntc,cntc,1) # coarse cell 
			xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
			#print("%.2e, %d"%(xcor,skip))
			netmap1.get_net('Lx',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('Ly',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate
			if cntc==ncrs-1:
				xc_end=xcor+crs_w 
				#print("xc_end=%.3e"%(xc_end))
		#---------------------------------------------
		# place right fine cells
		#---------------------------------------------
		xfr_start=xc_end+nspace*fine_w
		for cntf in range(nfine_h):
			if ig!=nstg-1:	
				netmap1.get_net('NS',None,ig,ig,1) # stg
			else:
				netmap1.get_net('NS',None,None,'last',1) # stg
			if cntf==0:
				xtry=xfr_start
			else:
				xtry=xcor+fine_w
			netmap1.get_net('nf',None,cntf+nfine_h,cntf+nfine_h,1) # fine cell
			xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
			netmap1.get_net('LX',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('LY',None,yoff+ig*crs_h,yoff+ig*crs_h,1) # Y coordinate 

	with open(outputDir+"custom_place.tcl","w") as w_tcl:
		for line in lines:
			netmap1.printline(line,w_tcl)

# 2 stack per stage. the number of cells per xtage have to be even!!!
def dco_custom_place_v2p5(formatDir,outputDir,crscell_dim,finecell_dim,ncrs,nfine_h,nstg,ndrv,nspace,nxoff,nyoff, welltap_dim, welltap_xc, ND):
	if ND==0:
		r_c = open(formatDir+"form_dco_custom_place.tcl","r")
	else:
		r_c = open(formatDir+"form_dco_custom_place_dCC.tcl","r") # dead CC
	lines=list(r_c.readlines())

	welltap_w=welltap_dim[0]
	crs_w=crscell_dim[0]
	crs_h=crscell_dim[1]
	fine_w=finecell_dim[0]
	fine_h=finecell_dim[1]
	xoff=nxoff*fine_w	
	yoff=nyoff*fine_h

	nfine_h_h=int(nfine_h/2)
	ndrv_h=int(ndrv/2)
	ncrs_h=int(ncrs/2)

#	xfl_end=xoff+nfine_h*fine_w
#	xd_start=xfl_end + nspace*fine_w	
#	xd_end=xd_start + ndrv*crs_w
#	xc_end=xd_end + ncrs*crs_w
#	xfr_start=xc_end + nspace*fine_w
	netmap1=txt_mds.netmap()
	skip=0
	for ig in range(nstg): # for each stage
		if ND>0:
			#---------------------------------------------
			# place left off-coarse cells
			#---------------------------------------------
			for cntd in range(int(ND/4)):
				if ig!=nstg-1:	
					netmap1.get_net('nS',None,ig,ig,1) # stg
					netmap1.get_net('nS',None,ig,ig,1) # stg
				else:
					netmap1.get_net('nS',None,None,'last',1) # stg
					netmap1.get_net('nS',None,None,'last',1) # stg
				netmap1.get_net('nD',None,2*cntd,2*cntd,1) # fine cell idx
				netmap1.get_net('nD',None,2*cntd+1,2*cntd+1,1) # fine cell idx2
				if cntd==0:
					xtry=xoff
				else:
					xtry=xcor+crs_w
				xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
				netmap1.get_net('DX', None, xcor, xcor, 1) # X coordinate 
				netmap1.get_net('DX', None, xcor, xcor, 1) # X coordinate 
				netmap1.get_net('DY',None,yoff+2*ig*crs_h,yoff+2*ig*crs_h,1) # Y coordinate
				netmap1.get_net('DY',None,yoff+(2*ig+1)*crs_h,yoff+(2*ig+1)*crs_h,1) # Y coordinate
				if cntd==int(ND/4)-1:
					xdc_end=xcor+crs_w
					#print("xdc_end=%.3e"%(xdc_end))
#				print("%.2e, %d"%(xcor,skip))
		#---------------------------------------------
		# place left fine cells
		#---------------------------------------------
		for cntf in range(nfine_h_h):
			if ig!=nstg-1:	
				netmap1.get_net('NS',None,ig,ig,1) # stg
				netmap1.get_net('NS',None,ig,ig,1) # stg
			else:
				netmap1.get_net('NS',None,None,'last',1) # stg
				netmap1.get_net('NS',None,None,'last',1) # stg
			netmap1.get_net('nf',None,2*cntf,2*cntf,1) # fine cell idx
			netmap1.get_net('nf',None,2*cntf+1,2*cntf+1,1) # fine cell idx2
			if cntf==0:
				if ND==0:
					xtry=xoff
				elif ND>0:
					xtry=xdc_end+fine_w*nspace
					#print("ND is greater than 0. fine cells starting from %.3e"%(xtry))
			else:
				xtry=xcor+fine_w
			xcor,skip=xcorCal_skipwt(xtry, fine_w, welltap_w, welltap_xc, fine_w)
			netmap1.get_net('LX', None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('LX', None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('LY',None,yoff+2*ig*crs_h,yoff+2*ig*crs_h,1) # Y coordinate
			netmap1.get_net('LY',None,yoff+(2*ig+1)*crs_h,yoff+(2*ig+1)*crs_h,1) # Y coordinate
			if cntf==nfine_h_h-1:
				xfl_end=xcor+fine_w
				#print("xfl_end=%.3e"%(xfl_end))
			#print("%.2e, %d"%(xcor,skip))
			
		#---------------------------------------------
		# place driver cells
		#---------------------------------------------
		xd_start=xfl_end+nspace*fine_w
		for cntd in range(ndrv_h):
			if ig!=nstg-1:	
				netmap1.get_net('ns',None,ig,ig,1) # stg
				netmap1.get_net('ns',None,ig,ig,1) # stg
			else:
				netmap1.get_net('ns',None,None,'last',1) # stg
				netmap1.get_net('ns',None,None,'last',1) # stg
			if cntd==0:
				xtry=xd_start
			else:
				xtry=xcor+crs_w
			netmap1.get_net('nd',None,2*cntd,2*cntd,1) # driver cell 
			netmap1.get_net('nd',None,2*cntd+1,2*cntd+1,1) # driver cell 
			xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
			print("%.2e, %d"%(xcor,skip))
			netmap1.get_net('lx',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('lx',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('ly',None,yoff+2*ig*crs_h,yoff+2*ig*crs_h,1) # Y coordinate
			netmap1.get_net('ly',None,yoff+(2*ig+1)*crs_h,yoff+(2*ig+1)*crs_h,1) # Y coordinate
			if cntd==ndrv_h-1:
				xd_end=xcor+crs_w 
				print("xd_end=%.3e"%(xd_end))
		#---------------------------------------------
		# place coarse cells
		#---------------------------------------------
		for cntc in range(ncrs_h):
			if ig!=nstg-1:	
				netmap1.get_net('Ns',None,ig,ig,1) # stg
				netmap1.get_net('Ns',None,ig,ig,1) # stg
			else:
				netmap1.get_net('Ns',None,None,'last',1) # stg
				netmap1.get_net('Ns',None,None,'last',1) # stg
			if cntc==0:
				xtry=xd_end
			else:
				xtry=xcor+crs_w
			netmap1.get_net('nc',None,2*cntc,2*cntc,1) # coarse cell 
			netmap1.get_net('nc',None,2*cntc+1,2*cntc+1,1) # coarse cell 
			xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
			print("%.2e, %d"%(xcor,skip))
			netmap1.get_net('Lx',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('Lx',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('Ly',None,yoff+2*ig*crs_h,yoff+2*ig*crs_h,1) # Y coordinate
			netmap1.get_net('Ly',None,yoff+(2*ig+1)*crs_h,yoff+(2*ig+1)*crs_h,1) # Y coordinate
			if cntc==ncrs_h-1:
				xc_end=xcor+crs_w 
				print("xc_end=%.3e"%(xc_end))
		#---------------------------------------------
		# place right fine cells
		#---------------------------------------------
		xfr_start=xc_end+nspace*fine_w
		for cntf in range(nfine_h_h):
			if ig!=nstg-1:	
				netmap1.get_net('NS',None,ig,ig,1) # stg
				netmap1.get_net('NS',None,ig,ig,1) # stg
			else:
				netmap1.get_net('NS',None,None,'last',1) # stg
				netmap1.get_net('NS',None,None,'last',1) # stg
			if cntf==0:
				xtry=xfr_start
			else:
				xtry=xcor+fine_w
			netmap1.get_net('nf',None,2*cntf+nfine_h,2*cntf+nfine_h,1) # fine cell
			netmap1.get_net('nf',None,2*cntf+nfine_h+1,2*cntf+nfine_h+1,1) # fine cell
			xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
			netmap1.get_net('LX',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('LX',None, xcor, xcor, 1) # X coordinate 
			netmap1.get_net('LY',None,yoff+2*ig*crs_h,yoff+2*ig*crs_h,1) # Y coordinate 
			netmap1.get_net('LY',None,yoff+(2*ig+1)*crs_h,yoff+(2*ig+1)*crs_h,1) # Y coordinate 
			if cntf==nfine_h_h-1:
				xfr_end=xcor+fine_w
		if ND>0:
			#---------------------------------------------
			# place left off-coarse cells
			#---------------------------------------------
			for cntd in range(int(ND/4),int(ND/2)):
				if ig!=nstg-1:	
					netmap1.get_net('nS',None,ig,ig,1) # stg
					netmap1.get_net('nS',None,ig,ig,1) # stg
				else:
					netmap1.get_net('nS',None,None,'last',1) # stg
					netmap1.get_net('nS',None,None,'last',1) # stg
				netmap1.get_net('nD',None,2*cntd,2*cntd,1) # fine cell idx
				netmap1.get_net('nD',None,2*cntd+1,2*cntd+1,1) # fine cell idx2
				if cntd==0:
					xtry=xfr_end
				else:
					xtry=xcor+crs_w
				xcor,skip=xcorCal_skipwt(xtry, crs_w, welltap_w, welltap_xc, fine_w)
				netmap1.get_net('DX', None, xcor, xcor, 1) # X coordinate 
				netmap1.get_net('DX', None, xcor, xcor, 1) # X coordinate 
				netmap1.get_net('DY',None,yoff+2*ig*crs_h,yoff+2*ig*crs_h,1) # Y coordinate
				netmap1.get_net('DY',None,yoff+(2*ig+1)*crs_h,yoff+(2*ig+1)*crs_h,1) # Y coordinate
				if cntd==int(ND/2)-1:
					xdc_end=xcor+crs_w

	with open(outputDir+"custom_place.tcl","w") as w_tcl:
		for line in lines:
			netmap1.printline(line,w_tcl)

# calculates and returns the x-coordinate considering the welltap placements
def xcorCal_skipwt ( cell_xc, cell_w, welltap_w, welltap_xc, xoff):
	c_start=cell_xc
	c_end=c_start+cell_w
	skip=0
	for iwt in range(len(welltap_xc)):
		wt_start=welltap_xc[iwt]
		wt_end=welltap_xc[iwt]+welltap_w
		if (c_start <= wt_start and c_end >=wt_start) or (c_start <= wt_end and c_end >= wt_end): # skip when overlap
			xcor= wt_end+xoff
#			print("INFO: welltap overlap with cell. xcor moved from %.3e to %.3e"%(c_start,xcor))
			skip=1
	if skip==0: # no overlap with any welltaps
		xcor=c_start
#		print("INFO: no overlap with welltaps")
	return xcor,skip 



def editPin_gen_se(Ndrv,Ncc,Nfc,Nstg,formatDir,wfile_name,platform):
	nCC=Ncc*Nstg
	nFC=Nfc*Nstg
	nPout=Nstg*2
	
	#rfile=open(formatDir+'/form_floorplan_test.tcl','r')
	#rfile=open('ignore_form_floorplan.tcl','r')
	rfile=open(formatDir+'/form_'+platform+'_dco_pre_place_se.tcl','r')
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
	
	#--- distribute PH_P_OUT, PH_N_OUT ---
	if platform=='tsmc65lp':
		nm2.get_net('po',None,0,Nstg//2,1)
		nm2.get_net('Po',None,Nstg//2+1,Nstg-1,1)
	elif platform=='gf12lp':
		nm2.get_net('po',None,0,Nstg-1,1)

	Nfc_h = int(Nstg*Nfc/2)
	Nfc_rem = Nstg*Nfc - Nfc_h	
	Ncc_h = int(Nstg*Ncc/2)	
	Ncc_rem = Nstg*Ncc - Ncc_h	
	lines=list(rfile.readlines())
	iline=0
	for line in lines:
		if line[0:2]=='@E':
			nm1=txt_mds.netmap()
			if iline==0: 
				nm1.get_net('f1','FC[',iline*Nfc_h,iline*Nfc_h+(Nfc_h-1),1)
				nm1.get_net('fb','FCB[',iline*Nfc_h,iline*Nfc_h+(Nfc_h-1),1)
				nm1.get_net('c1','CC[',iline*Ncc_h,iline*Ncc_h+(Ncc_h-1),1)
			else: 
				nm1.get_net('f1','FC[',iline*Nfc_h,Nstg*Nfc-1,1)
				nm1.get_net('fb','FCB[',iline*Nfc_h,Nstg*Nfc-1,1)
				nm1.get_net('c1','CC[',iline*Ncc_h,Nstg*Ncc-1,1)
			nm1.printline(line,wfile)
			iline=iline+1
		else:
			nm2.printline(line,wfile)

def pre_dltdc_custom_place(formatDir,outputDir,dltdc_dim,cccell_dim,finecell_dim,dff_dim,ncc_fb,nfc_h,nstg_fb,ndrv_fb,nspace,nxoff,nyoff, version, ndrv_ref, ncc_ref, pre_ncc_fb, pre_ndrv_fb, pre_nstg_fb, pre_ncc_ref, pre_ndrv_ref, pre_nstg_ref, np_nstg, npb_ncc, np_ncc,np_ndrv,pp_nstg, pp_ncc, pp_drv, fm_ncc):
	r_c = open(formatDir+"form_pre_dltdc_custom_place.tcl","r")
	lines=list(r_c.readlines())

	dltdc_w=dltdc_dim[0]
	dltdc_h=dltdc_dim[1]
	cc_w=cccell_dim[0]
	cc_h=cccell_dim[1]
	fine_w=finecell_dim[0]
	fine_h=finecell_dim[1]
	dff_w=dff_dim[0]
	dff_h=dff_dim[1]
	xoff=nxoff*fine_w	
	yoff=nyoff*fine_h

	netmap1=txt_mds.netmap()
	#=====================================================
	# pre-dltdc: place from right => left
	# design params: pre-dltdc 
	pre_ndrv_fb = 1;
	pre_ndrv_ref = 2;
	pre_ncc_fb = 4;
	pre_ncc_ref = 2;
	
	np_ndrv = 4;
	pp_ndrv = 2;
	
	np_ncc = 4;
	np_nstg = 3; 
	pp_nstg = 4; 
	pp_ncc = 6;

	pre_nstg_ref_ls = 1;
	pre_nstg_ref = 10; 
	pre_nstg_fb = 4;
	# DPs: dltdc delay line	
	nstg = 10; 
	nfc_fb = 6;
	nfc_ref = 6;
	ndrv_fb = 1;
	ndrv_ref = 2;
	ncc_fb = 4;
	ncc_ref = 2;
	dco_num_ph = 5;

	# x-positions
	embtdc_start = dltdc_w - xoff - dff_w
	smpl_edge_sel_start = embtdc_start - xoff - dff_w
	pre_dco_path_start = smpl_edge_sel_start - xoff -cc_w		
	pre_dco_path_end = pre_dco_path_start - cc_w*(pre_ncc_fb + pre_ndrv_fb)*pre_nstg_fb*cc_w +cc_w
	pp_start = pre_dco_path_end - xoff - cc_w
	np_start = pp_start - cc_w 
#	pp_end = pp_start - pp_nstg*cc_w 

	# embtdc
#	for ig in range(


	#=====================================================
	# dltdc
	xfl_end=xoff+nfc_h*2*fine_w
	xd_start=xfl_end + nspace*fine_w	
	xd_end=xd_start + ndrv_fb*cc_w*2
	xc_end=xd_end + ncc_fb*cc_w*2
	xdff_start=xc_end+nspace*fine_w
	xdff_end=xdff_start+dff_w
	xdr_start=xdff_end+nspace*fine_w
	xdr_end=xdr_start+ndrv_ref*cc_w*2
	xcr_start=xdr_end
	xcr_end=xcr_start+ncc_ref*cc_w*2
	xfr_start=xcr_end + nspace*fine_w # ref
	xfr_end=xfr_start+fine_w*2*nfc_h
	for ig in range(nstg): # for each stage
		for cntf in range(nfc_h*2):
			# for fb path
			netmap1.get_net('fs',None,ig,ig,1) # stg
			netmap1.get_net('nf',None,cntf,cntf,1) # fine cell
			netmap1.get_net('fx', None, xoff+cntf*fine_w, xoff+cntf*fine_w, 1) # X coordinate 
			netmap1.get_net('fy',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
			# for ref path 
			netmap1.get_net('FS',None,ig,ig,1) # stg
			netmap1.get_net('NF',None,cntf,cntf,1) # fine cell
			netmap1.get_net('FX', None, xfr_start+cntf*fine_w, xfr_start+cntf*fine_w, 1) # X coordinate 
			netmap1.get_net('FY',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate 
		for cntd in range(ndrv_fb):
			netmap1.get_net('ns',None,ig,ig,1) # stg
			netmap1.get_net('nd',None,cntd,cntd,1) # driver cell 
			netmap1.get_net('lx',None, xd_start+cntd*cc_w*2, xd_start+cntd*cc_w*2, 1) # X coordinate 
			netmap1.get_net('ly',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
			netmap1.get_net('NS',None,ig,ig,1) # stg
			netmap1.get_net('ND',None,cntd,cntd,1) # driver cell 
			netmap1.get_net('LX',None, xd_start+cntd*cc_w*2+cc_w, xd_start+cntd*cc_w*2+cc_w, 1) # X coordinate 
			netmap1.get_net('LY',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
		for cntd in range(ndrv_ref):
			netmap1.get_net('rs',None,ig,ig,1) # stg
			netmap1.get_net('rd',None,cntd,cntd,1) # driver cell 
			netmap1.get_net('rx',None, xdr_start+cntd*cc_w*2, xdr_start+cntd*cc_w*2, 1) # X coordinate 
			netmap1.get_net('ry',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
			netmap1.get_net('RS',None,ig,ig,1) # stg
			netmap1.get_net('RD',None,cntd,cntd,1) # driver cell 
			netmap1.get_net('RX',None, xdr_start+cntd*cc_w*2+cc_w, xdr_start+cntd*cc_w*2+cc_w, 1) # X coordinate 
			netmap1.get_net('RY',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
		for cntc in range(ncc_fb):
			netmap1.get_net('Ns',None,ig,ig,1) # stg
			netmap1.get_net('nc',None,cntc,cntc,1) # coarse cell 
			netmap1.get_net('Lx',None, xd_end+cntc*cc_w*2, xd_end+cntc*cc_w*2, 1) # X coordinate 
			netmap1.get_net('Ly',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate 
			netmap1.get_net('cS',None,ig,ig,1) # stg
			netmap1.get_net('nC',None,cntc,cntc,1) # coarse cell 
			netmap1.get_net('cX',None, xd_end+cntc*cc_w*2+cc_w, xd_end+cntc*cc_w*2+cc_w, 1) # X coordinate 
			netmap1.get_net('cY',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
		for cntc in range(ncc_ref):
			netmap1.get_net('Rs',None,ig,ig,1) # stg
			netmap1.get_net('Rc',None,cntc,cntc,1) # coarse cell 
			netmap1.get_net('Rx',None, xdr_end+cntc*cc_w*2, xdr_end+cntc*cc_w*2, 1) # X coordinate 
			netmap1.get_net('Ry',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
			netmap1.get_net('rS',None,ig,ig,1) # stg
			netmap1.get_net('rC',None,cntc,cntc,1) # coarse cell 
			netmap1.get_net('rX',None, xdr_end+cntc*cc_w*2+cc_w, xdr_end+cntc*cc_w*2+cc_w, 1) # X coordinate 
			netmap1.get_net('rY',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate
		#---------------------------------------------
		# place dffs 
		#---------------------------------------------
		netmap1.get_net('nS',None,ig,ig,1) # stg
	#	netmap1.get_net('lX',None, xfr_end+nspace*fine_w, xfr_end+nspace*fine_w, 1) # X coordinate 
		netmap1.get_net('lX',None, xdff_start, xdff_start, 1) # X coordinate 
		netmap1.get_net('lY',None,yoff+ig*cc_h,yoff+ig*cc_h,1) # Y coordinate 

	with open(outputDir+"custom_place.tcl","w") as w_tcl:
		for line in lines:
			netmap1.printline(line,w_tcl)


def dco_inv_flow_genus(formatDir,flowDir,dcoName,bleach,ndrv,nstg,platform,INV_name):
	print ('#======================================================================')
	print('# setting up flow directory for dco')
	print ('#======================================================================')
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	#--- copy scripts files to flowDir/scripts/ ---
	shutil.copyfile(formatDir+'dco_floorplan.tcl',flowDir+'/scripts/innovus/floorplan.tcl')	
	shutil.copyfile(formatDir+'pdpll_pre_init.tcl',flowDir+'/scripts/innovus/pre_init.tcl')	
	shutil.copyfile(formatDir+'form_kbr_always_source.tcl',flowDir+'/scripts/innovus/always_source.tcl')	
	shutil.copyfile(formatDir+'dco_power_intent.cpf',flowDir+'/scripts/innovus/power_intent.cpf')	
	shutil.copyfile(formatDir+'form_kbr_dco_post_init.tcl',flowDir+'/scripts/innovus/post_init.tcl')	
	shutil.copyfile(formatDir+'dco_pre_route.tcl',flowDir+'/scripts/innovus/pre_route.tcl')	
	shutil.copyfile(formatDir+'dco_post_postroute.tcl',flowDir+'/scripts/innovus/post_postroute.tcl')	
	shutil.copyfile(formatDir+'dco_post_signoff.tcl',flowDir+'/scripts/innovus/post_signoff.tcl')	
	shutil.copyfile(formatDir+'cadre_Makefile_genus',flowDir+'/Makefile')	
	shutil.copyfile(formatDir+'form_genus.constraints.tcl', flowDir+'/scripts/genus/constraints.tcl')
	shutil.copyfile(formatDir+'form_genus.filelist.tcl', flowDir+'/scripts/genus/genus.filelist.tcl')
	shutil.copyfile(formatDir+'form_genus.read_design.tcl', flowDir+'/scripts/genus/genus.read_design.tcl')


	#--- generate  include.mk file ---
	rmkfile=open(formatDir+'/form_include_genus.mk','r')
	nm1=txt_mds.netmap()
	nm1.get_net('iN',dcoName,None,None,None)
	nm1.get_net('pf',platform,None,None,None)
	with open(flowDir+'include.mk','w') as wmkfile:
		lines_const=list(rmkfile.readlines())
		for line in lines_const:
			nm1.printline(line,wmkfile)
	#--- generate verilog file ---
	nm1=txt_mds.netmap()
	rvfile=open(formatDir+'/form_dco_inv.v','r')
	nm1.get_net('iN',dcoName,None,None,None)
	nm1.get_net('nM',None,nstg,nstg,1)
	nm1.get_net('nD',None,ndrv,ndrv,1)
	nm1.get_net('NC',INV_name,None,None,None)
	nm1.get_net('CN',INV_name,None,None,None)

	with open(flowDir+'src/'+dcoName+'.v','w') as wvfile:
		lines_const=list(rvfile.readlines())
		for line in lines_const:
			nm1.printline(line,wvfile)
