#!/usr/bin/env python3

#======================================================================
# pll generator python wrapper
# input: specIn.json
# output: specOut.json, synth_pll.v, synth_pll.gds.gz,
#   	  controller verilog sim result, dco hspice sim result
#======================================================================

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

absGenDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../")
absPvtDir = os.path.join(absGenDir,"../../private/generators/pll-gen/")
print("absGenDir=%s"%(absGenDir))
print("absPvtDir=%s"%(absPvtDir))
sys.path.append(absGenDir + './pymodules/')

import txt_mds
import modeling 
import preparations
import run_digital_flow
import run_pex_flow 
import run_pex_sim 
import run_pre_sim 

pvtPyDir = os.path.join(absPvtDir , './pymodules/')
configFile=absGenDir + './../../config/platform_config.json'

#========================================================
# parse the command & config.json
#========================================================
parseList=[1,1,1,1,1,1,1,1]  #[specfile,platform,outputDir,pex_verify,run_vsim,mode,synth_tool,track]
specfile,platform,outputDir,pexVerify,runVsim,outMode,synthTool,track=preparations.command_parse(parseList)
specIn=open(specfile,'r')

aLib,mFile,calibreRulesDir,hspiceModel=preparations.config_parse(outMode,configFile,platform)

#========================================================
# directory path settings
#========================================================
#	public directories
#--------------------------------------------------------
vsimDir=absGenDir + 'verilog_sim/'
verilogSrcDir=absGenDir + 'verilogs/'
formatDir=absGenDir + 'formats/BLE/' 
#--------------------------------------------------------
#	private directories
#--------------------------------------------------------
pvtFormatDir = absPvtDir + 'formats/'

absPvtDir_plat=absPvtDir+platform+'/'
hspiceDir=absPvtDir_plat +  '/HSPICE/'
netlistDir=hspiceDir+'NETLIST/'
tbDir=hspiceDir+'TB/'
tbrfDir=hspiceDir+'TBrf/'
extDir = absPvtDir_plat + 'extraction/'
finesimDir = absPvtDir_plat + 'FINESIM/'
pll_flowDir = absPvtDir_plat + 'flow_ble_pll/'
tdc_flowDir = absPvtDir_plat + 'flow_ble_tstdc/'
outbuff_div_flowDir = absPvtDir_plat + 'flow_outbuff_div/'
dco_flowDir = absPvtDir_plat + 'flow_ble_dco/'
tstdc_flowDir = absPvtDir_plat + 'flow_tstdc_counter/'

if synthTool=='genus':
	dco_flowDir = absPvtDir_plat + 'flow_dco_genus/'
	pll_flowDir = absPvtDir_plat + 'flow_pdpll_genus/'
	print('INFO: genus is selected for synth-tool. _genus will be tailed after flow directories')

#outbuff_div_flowDir = pvtFormatDir +platform+ '_flow_outbuff_div/'

if platform=='tsmc65lp':
	fc_en_type = 1 # dco_FC en => increase frequency
	modelVersion='Beta' 
	fc_en_type = 1 # dco_FC en => increase frequency
	sim_time = 40e-9
	corner_lib='tt_lib'
	tech_node='65'
	wellpin=0 # aux-cell well pin  
	edge_sel=1
	buf_small='BUFH_X2M_A9TR'
	buf_big='BUFH_X9M_A9TR'
	bufz='BUFZ_X4M_A9TR'
	min_p_rng_l= 4
	min_p_str_l= 3
	p_rng_w= 1.6 
	p_rng_s= 0.8
	p2_rng_w= 1.6
	p2_rng_s= 0.8
	max_r_l=5
	pll_max_r_l=8
	outbuff_div=1
	tdc_dff='DFFRPQ_X0P5M_A9TR'
	H_stdc=1.8
	custom_lvs=0
	cust_place=0
	single_ended=0
	CC_stack=2
	FC_half=0
	pex_spectre=0
	vdd=[1.2]
	cp_version=0 # custom_place version
	welltap_dim=[0,0]
	welltap_xc=[0,0]
	ND=0 # always-off NCCs
elif platform=='gf12lp':
	fc_en_type = 2 # dco_FC en => decrease frequency
	modelVersion='Alpha' 
	fc_en_type = 2 # dco_FC en => decrease frequency
	sim_time = 20e-9
	corner_lib='TT' 
	tech_node='12' 
	wellpin=1 
	edge_sel=0
	buf_small='BUFH_X2N_A10P5PP84TR_C14'
	buf_big='BUFH_X8N_A10P5PP84TR_C14'
	bufz='placeHolder'
	min_p_rng_l= 4
	min_p_str_l= 5
	p_rng_w= 1.6 
	p_rng_s= 0.8
	p2_rng_w= 1.2
	p2_rng_s= 0.8
	max_r_l=13
	pll_max_r_l=13
	outbuff_div=0
	tdc_dff='DFFRPQL_X1N_A10P5PP84TR_C14'
	H_stdc=0.672
	custom_lvs=0
	cust_place=1
	single_ended=1
	FC_half=1
	CC_stack=3
	pex_spectre=0
	vdd=[0.8]   #vdd[0] is the nominal val
	welltap_dim=[0.924, 0.672]
	welltap_xc=[50,95]
	cp_version=3 # custom_place version (3: decap)
	FC_version=2 # dco_FC single ended version
	ND=6 # always-off NCCs
if single_ended==0:
	dco_CC_lib=aLib+'/dco_CC/latest/'
	dco_FC_lib=aLib+'/dco_FC/latest/'
else:
	if CC_stack==2:
		dco_CC_lib=aLib+'/dco_CC_se/latest/'
	elif CC_stack==3:
		dco_CC_lib=aLib+'/dco_CC_se_3st/latest/'
	if FC_half==0:
		dco_FC_lib=aLib+'/dco_FC_se/latest/'
	elif FC_half==1:
		dco_FC_lib=aLib+'/dco_FC_se2_half/latest/'

DCDC_CAP_UNIT_lib = aLib+'/DCDC_CAP_UNIT/latest/'
BUFH_X14N_pwr_lib = aLib+'/BUFH_X14N_pwr/latest/'
#========================================================
# generate directory tree 
#========================================================
print ('#======================================================================')
print ('# check directory tree and generate missing directories')
print ('#======================================================================')
preparations.ble_dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform,vsimDir,tdc_flowDir)
#--------------------------------------------------------
# check for private directory 
#--------------------------------------------------------
if outMode=='macro' or outMode=='full':
	if os.path.isdir(absPvtDir)!=1:
		print("Error: Need private directory for mode 'macro' or 'full'. Check README")
		sys.exit(1)
	#--------------------------------------------------------
	#	read the aux-cells	
	#--------------------------------------------------------
	dco_CC_name,dco_FC_name = preparations.aux_copy_export(dco_flowDir,dco_CC_lib,dco_FC_lib)
	preparations.ble_aux_copy_export(dco_flowDir,DCDC_CAP_UNIT_lib,BUFH_X14N_pwr_lib)
	preparations.aux_copy_export(pll_flowDir,dco_CC_lib,dco_FC_lib)
	W_CC,H_CC,W_FC,H_FC=preparations.aux_parse_size(dco_CC_lib,dco_FC_lib)
	A_CC=W_CC*H_CC
	A_FC=W_FC*H_FC
	design_param_json_file = absPvtDir+'ble_design_params.json'
else: # dummy areas for verilog mode
	A_CC=0.01;
	A_FC=0.01;
	design_param_json_file = absGenDir+'ble_design_params.json'



#--------------------------------------------------------
# generate ble_dco 
#--------------------------------------------------------
# decap info
decap_dim = [11.764,13.592]
decap_pin_x = [0.882,6.882]
decap_pin_sp = [6]
# buffer info
buf_x2_dim = [0.42, 0.672]
buf_x4_dim = [0.588, 0.672]
buf_x10_dim = [1.428, 0.672]
buf_x16_dim = [2.268, 0.672]

run_dco_flow=1
run_dig_flow=1
gen_model=0

tapeout_mode=1
bleach=0
synth=0
apr=0
pex=0
tb_netlist=0
lvs=0
ninterp=2
num_core=4

tdc_bleach=0
tdc_synth=0
tdc_apr=0

pll_bleach=0
pll_synth=0
pll_apr=0


if tapeout_mode==0:
	pex_sim_time=8e-9
else:
	pex_sim_time=8e-9

dcoName='ble_dco'
finesim=1

# verilog gen

#preparations.read_ble_params(absGenDir+'ble_design_params.json')
dco_design_params,tstdc_counter_design_params = run_digital_flow.ble_verilog_gen(outMode,outputDir,formatDir,design_param_json_file)
buf = run_digital_flow.ble_verilog_gen(outMode,outputDir,formatDir,absGenDir+'ble_design_params.json')

if run_dco_flow==1:
	W_dco,H_dco=run_digital_flow.dco_flow_decap_pwr2(pvtFormatDir,dco_flowDir,dcoName,bleach,W_CC,H_CC,W_FC,H_FC,synth,apr,outputDir,platform,edge_sel,buf_small,buf_big,bufz,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,max_r_l,cust_place,single_ended,FC_half,CC_stack,dco_CC_name,dco_FC_name,cp_version,welltap_dim,welltap_xc,decap_dim,dco_design_params)
	run_digital_flow.ble_tstdc_flow(pvtFormatDir,tdc_flowDir,tdc_bleach,W_CC,H_CC,W_FC,H_FC,tdc_synth,tdc_apr,outputDir,tstdc_counter_design_params)
	run_digital_flow.ble_pll_top_flow(pvtFormatDir,pll_flowDir,pll_bleach,pll_synth,pll_apr,outputDir)
	run_pex_flow.gen_post_pex_netlist(platform, dcoName, pvtFormatDir, dco_flowDir, extDir, calibreRulesDir, wellpin, pex_spectre)
	sys.exit(1)


#	Ncc=20
#	Ndrv=24
#	Nfc=24
#	Nstg=5
#	#dcoName='dco_%dndrv_%dncc_%dnstg_%dnfc'%(Ndrv,Ncc,Nstg,Nfc)
#	dcoName='ble_dco'
#	dcoNames.append(dcoName)
#	print(dcoName)
#	print(dcoNames)
#	if run_dig_flow==1:
#		W_dco,H_dco=run_digital_flow.dco_flow_decap_pwr2(pvtFormatDir,dco_flowDir,dcoName,bleach,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir,platform,edge_sel,buf_small,buf_big,bufz,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,max_r_l,cust_place,single_ended,FC_half,CC_stack,dco_CC_name,dco_FC_name,cp_version,welltap_dim,welltap_xc,ND, decap_dim)
#	print("W/H of DCO: %.3f, %.3f"%(W_dco, H_dco))
#	if lvs==1:
#		run_digital_flow.buf_custom_lvs(calibreRulesDir,dco_flowDir,extDir,dcoName,pvtFormatDir,platform)
#	if pex==1:
#		run_pex_flow.gen_post_pex_netlist(platform, dcoName, pvtFormatDir, dco_flowDir, extDir, calibreRulesDir, wellpin, pex_spectre)
#	if tb_netlist==1:
#		run_pex_sim.gen_dco_pex_wrapper(extDir,pex_netlistDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,ninterp,dcoName,fc_en_type,FC_half,pex_spectre)
#		if pex_spectre==0:
#			run_pex_sim.gen_tb_wrapped(hspiceModel,pex_tbDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,vdd,temp,fc_en_type,pex_sim_time,corner_lib,dcoName,pex_netlistDir,finesim,single_ended,FC_half,pex_spectre,tapeout_mode)
	
#	run_pex_sim.gen_mkfile_pex(pvtFormatDir,hspiceDir,pex_resDir,pex_tbDir,num_core,dcoNames,tech_node,finesim)




