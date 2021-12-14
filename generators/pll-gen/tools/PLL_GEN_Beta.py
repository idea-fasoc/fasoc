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
formatDir=absGenDir + 'formats/'

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
pll_flowDir = absPvtDir_plat + 'flow_pdpll/'
outbuff_div_flowDir = absPvtDir_plat + 'flow_outbuff_div/'
dco_flowDir = absPvtDir_plat + 'flow_dco/'

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
	dead_CC=0
	cp_version=0 # custom_place version
	welltap_dim=[0,0]
	welltap_xc=[0,0]
elif platform=='gf12lp':
	fc_en_type = 2 # dco_FC en => decrease frequency
	modelVersion='Alpha_pex' 
	fc_en_type = 2 # dco_FC en => decrease frequency
	sim_time = 20e-9
	corner_lib='TT' 
	tech_node='12' 
	wellpin=1 
	edge_sel=0
	if track==9:
		buf_small='BUFH_X2N_A9PP84TR_C14'
		buf_big='BUFH_X8N_A9PP84TR_C14'
		buf1_name='BUFH_X8N_A9PP84TR_C14'
		buf2_name='BUFH_X10N_A9PP84TR_C14'
		buf3_name='BUFH_X10N_A9PP84TR_C14'
		#tdc_dff='DFFRPQL_X1N_A9PP84TR_C14'
		tdc_dff='DFFQ_X1N_A9PP84TR_C14'
	else:
		buf_small='BUFH_X2N_A10P5PP84TR_C14'
		buf_big='BUFH_X8N_A10P5PP84TR_C14'
		buf1_name='BUFH_X8N_A10P5PP84TR_C14'
		buf2_name='BUFH_X10N_A10P5PP84TR_C14'
		buf3_name='BUFH_X10N_A10P5PP84TR_C14'
		#tdc_dff='DFFRPQL_X1N_A10P5PP84TR_C14'
		tdc_dff='DFFQ_X1N_A10P5PP84TR_C14'
	bufz='placeHolder'
	min_p_rng_l= 4
	min_p_str_l= 5
	p_rng_w= 1.6 
	p_rng_s= 0.8
	p2_rng_w= 1.2
	p2_rng_s= 0.8
	max_r_l=5
	pll_max_r_l=8
	outbuff_div=0
	H_stdc=0.672
	custom_lvs=0
	cust_place=1
	single_ended=1
	FC_half=1
	CC_stack=3
	pex_spectre=0
	vdd=[0.8]
	dead_CC=8
	cp_version=2 # custom_place version
	dco_CC_name = 'dco_CC_se_3st'
	dco_FC_name = 'dco_FC_se2_half'
	welltap_dim=[0.924, 0.672]
	welltap_xc=[50,95]
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
#========================================================
# generate directory tree 
#========================================================
print ('#======================================================================')
print ('# check directory tree and generate missing directories')
print ('#======================================================================')
preparations.dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform,vsimDir)

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
	preparations.aux_copy_export(pll_flowDir,dco_CC_lib,dco_FC_lib)
	W_CC,H_CC,W_FC,H_FC=preparations.aux_parse_size(dco_CC_lib,dco_FC_lib)
	A_CC=W_CC*H_CC
	A_FC=W_FC*H_FC
else: # dummy areas for verilog mode
	A_CC=0.01;
	A_FC=0.01;

#--------------------------------------------------------
# read input
#--------------------------------------------------------
print ('#======================================================================')
print ('# reading input files')
print ('#======================================================================')

jsonSpec = json.load(specIn)

if jsonSpec['generator'] != 'pll-gen':
	print ('Error: Generator specification must be \"pll-gen\".')
	sys.exit(1)

try:
	designName = jsonSpec['module_name']
	Fref = float(jsonSpec['specifications']['frequency']['reference']) # 10/12/21
	Fnom_min = float(jsonSpec['specifications']['frequency']['nom_min'])
	Fnom_max = float(jsonSpec['specifications']['frequency']['nom_max'])
	Fmax = float(jsonSpec['specifications']['frequency']['max'])
	Fmin = float(jsonSpec['specifications']['frequency']['min'])
	Fres = float(jsonSpec['specifications']['frequency']['res'])
	FCR_min = float(jsonSpec['specifications']['FCR_min'])
	dco_PWR = float(jsonSpec['specifications']['dco_PWR'])*1e-3 # pwr will be in (mW)
	try: 
		IB_PN = float(jsonSpec['specifications']['inband_PN']) #in dBc
		spec_priority={"Fnom":"dummy","IB_PN":"lo","Fmax":"hi","Fmin":"lo","Fres":"lo","FCR":"hi","dco_PWR":"lo"}					
	except:
		IB_PN=-200 # in case not specified: use dummy value 
		spec_priority={"Fnom":"dummy","Fmax":"hi","Fmin":"lo","Fres":"lo","FCR":"hi","dco_PWR":"lo"}					
		#spec_priority={"FCR":"hi","Fnom":"dummy","Fmax":"hi","Fmin":"lo","Fres":"lo","dco_PWR":"lo"}					
except:
	print('Error: wrong categories in spec.json, refer to provided example')
	sys.exit(1)	

#===============================================================
# generate dictionary list for spec priority 
#===============================================================

if Fnom_min >= Fnom_max:
	print('Error: Fnom_min should be greater than Fnom_max')
	sys.exit(1)	

#---------------------------------------------------------------
# when there is no model file, generate one
#---------------------------------------------------------------
if not os.path.isfile(mFile):
	print ('#======================================================================')
	print ('# There is no model file: '+mFile+' => running modeling procedure')
	print ('#======================================================================')
	if outMode=='verilog': # use public model
		mFile=os.path.join(absGenDir,'./publicModel/'+platform+'_pll_model.json')
		print('INFO: public model file is used: %s'%(mFile))
	elif outMode=='macro' or outMode=='full':	
		p = sp.Popen(['python','tools/MDL_GEN_Beta.py','--platform',platform,'--mode',outMode])
		p.wait()

try:
	f = open(mFile, 'r')
	print('INFO: model file from platform_config.json is properly read')
except ValueError as e:
	print ('Error: Model file creation failed')
	sys.exit(1)

#---------------------------------------------------------------------------------------
# read model file
#---------------------------------------------------------------------------------------
modelFile=open(mFile)
jsonModel= json.load(modelFile)
CF= jsonModel['pll_model_constants']['CF']
Cc= jsonModel['pll_model_constants']['Cc']
Cf= jsonModel['pll_model_constants']['Cf']
Iavg_const= jsonModel['pll_model_constants']['Iavg_const']
try:
	mult_Con= jsonModel['pex coefficients']['mult_Con']
	mult_Coff= jsonModel['pex coefficients']['mult_Coff']
	pex_Iavg_const=jsonModel['pex coefficients']['pex_Iavg_const']
	PN_const= jsonModel['pll_model_constants']['1M_PN_const']
	print("INFO: Current model is Beta version.")
except: # dummies
	mult_Con= 3.9
	mult_Coff= 3.9 
	pex_Iavg_const= 1
	PN_const= 1 
	print("INFO: Current model is Alpha version. Phase noise will not be supported. Generate Beta version model for phase noise.")

#--------------------------------------------------------
# search design solutions 
#--------------------------------------------------------
print ('#======================================================================')
print ('# searching for design solution')
print ('#======================================================================')

# design space definition: [start,end,step]
Ndrv_range=[2,42,2]
Nfc_range=[10,80,2]
Ncc_range=[10,80,2]

if single_ended==1:
	Nstg_range=[3,39,2]
else:
	Nstg_range=[4,28,2]


# test for desig searcher
#Ndrv_range=[30,40,2]
#Nfc_range=[22,24,2]
#Ncc_range=[24,26,2]
#Nstg_range=[5,9,2]

ND=dead_CC
temp=[25]

pass_flag,passed_designs,passed_specs,specRangeDic=modeling.design_solution(spec_priority,Fmax,Fmin,Fres,Fnom_min,Fnom_max,FCR_min,IB_PN,dco_PWR,CF,Cf,Cc,mult_Con,mult_Coff,Iavg_const,PN_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC,modelVersion, FC_half, dead_CC, ND)

#--------------------------------------------------------
# select the design with least area
#--------------------------------------------------------
if pass_flag==1:
	areaMdl=[]
	for ii in range(len(passed_specs)):
		areaMdl.append(passed_specs[ii][5])
		
	sys.setrecursionlimit(10000)  #expand the recursion limit if exceeded
	try:
		txt_mds.sort_via_1d_mult(areaMdl,passed_specs,passed_designs)
	except:
		print("sorting failed due to recursion limit: using the first design that meets the spec")
	print ('passed_specs=')
	print (passed_specs[0])
	final_specs=passed_specs[0]
	[Ndrv,Ncc,Nfc,Nstg]=passed_designs[0]
	if modelVersion=='Beta':
		[Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,FCR_mdl,Pwr_mdl,Area_mdl,IB_PN_mdl]=passed_specs[0]
	elif modelVersion=='Alpha' or modelVersion=='Alpha_pex':
		[Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,FCR_mdl,Pwr_mdl,Area_mdl]=passed_specs[0]
	print ('#======================================================================')
	print ('# selected design solution: ndrv=%d, ncc=%d, nfc=%d, nstg=%d'%(Ndrv,Ncc,Nfc,Nstg))
	if modelVersion=='Beta':
		print ('# expected specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2e, Pwr=%e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,IB_PN_mdl,Pwr_mdl))
		print ('# required specs: Fnom_min,max=%.2e,%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2e'%(Fnom_min,Fnom_max,Fmax,Fmin,Fres,IB_PN))
	elif modelVersion=='Alpha' or modelVersion=='Alpha_pex':
		print ('# expected specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, Pwr=%e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,Pwr_mdl))
		print ('# required specs: Fnom_min,max=%.2e,%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e'%(Fnom_min,Fnom_max,Fmax,Fmin,Fres))
	print ('#======================================================================')

	#------------------------------------------------------------------------------
	# write output json file 
	#------------------------------------------------------------------------------
	jsonSpec['results']={'platform': platform}			
	jsonSpec['results']['frequency']={'nom': Fnom_mdl}			
#	jsonSpec['results']['frequency'].update({'nom':Fnom_mdl})	
	jsonSpec['results']['frequency'].update({'max':Fmax_mdl})	
	jsonSpec['results']['frequency'].update({'min':Fmin_mdl})	
	jsonSpec['results']['frequency'].update({'res':Fres_mdl})	
	jsonSpec['results'].update({'FCR':FCR_mdl})	
	jsonSpec['results'].update({'dco_PWR':Pwr_mdl*1e3}) # in mW
	if modelVersion=='Beta':	
		jsonSpec['results'].update({'inband_PN':IB_PN_mdl})	
	jsonSpec['results'].update({'area': Area_mdl})	
	print("model predicted specs generated on "+outputDir+'/pll_spec_out.json')
	with open(outputDir+'/pll_spec_out.json','w') as resultSpecfile:
		json.dump(jsonSpec, resultSpecfile, indent=True)


elif pass_flag==0:
	fail_wrote=0
	print("writing failed result.json")
	jsonSpec['results']={'platform': platform}			
	#for spec in specRangeDic:
	for spec in spec_priority:
		#if specRangeDic[spec]==[]: # passed
		if specRangeDic[spec]==[] and fail_wrote==0: # passed
			jsonSpec['results'].update({spec:"passed"})	
		elif fail_wrote==0:
			jsonSpec['results'].update({"failed "+spec+" min":specRangeDic[spec][0]})	
			jsonSpec['results'].update({"failed "+spec+" max":specRangeDic[spec][1]})
			fail_wrote=1	
			print("failed: model predicted specs generated on "+outputDir+'/pll_spec_out.json')
	with open(outputDir+'/pll_spec_out.json','w') as resultSpecfile:
		json.dump(jsonSpec, resultSpecfile, indent=True)

#--------------------------------------------------------
# set default values (Alpha version)
# derive vco period, FCW
#--------------------------------------------------------
#Fref=10e6
#Kp_o_Ki=100
Kp_o_Ki=16
relBW=0.1
FCW=np.floor(Fnom_mdl/Fref)+1
FCW=int(FCW)
Fcenter = FCW*Fref
print('FCW=%d'%(FCW))
#Fbase=Fmin_mdl # this should be the Fmin_mdl
dFf=Fres_mdl
if FC_half==1:
	dFc=dFf*Nstg*Nfc*2/FCR_mdl
else:
	dFc=dFf*Nstg*Nfc/FCR_mdl
Fbase=Fcenter - dFc*Ncc*Nstg/2 # this should be the Fmin_mdl
Kp = 2*3.14*relBW*Fref/Fres_mdl/2 # 2 is for fractional bit mismatch in the controller 
Ki = Kp/Kp_o_Ki

vco_per=1/(Fref*FCW)/1e-9 # unit: ns
max_per=vco_per*3.125 #??

#--------------------------------------------------------
# generate PLL verilog, flow setups
#--------------------------------------------------------
# verilog gen
pll_name=designName
dcoName=pll_name+'_dco'
bufName='outbuff_div'
# verilog-sim
simOptions = ['BEH_SIM','SHORT_SIM','DCO_FC_HALF']
tdc_width = int(np.floor(np.log2(Nstg*2)) + 2)


if platform=='tsmc65lp':
	run_digital_flow.pll_verilog_gen(outMode,designName,absGenDir,outputDir,formatDir,pll_flowDir,Ndrv,Ncc,Nfc,Nstg,verilogSrcDir,buf_small,bufz,buf_big,edge_sel,dcoName,platform)
else:
	run_digital_flow.pll_verilog_gen_v2(outMode,designName,absGenDir,outputDir,formatDir,pll_flowDir,Ndrv,Ncc,Nfc,Nstg,verilogSrcDir,buf_small,bufz,buf_big,edge_sel,dcoName,platform,ND,dco_CC_name,dco_FC_name,buf1_name,buf2_name,buf3_name,tdc_width,Fcenter,Fbase,dFc,dFf,tdc_dff)
	run_pre_sim.run_pre_vsim(formatDir, vsimDir, FCW, Nstg, Ncc, Nfc, simOptions,tdc_width,dcoName, designName, Fref, Kp,outputDir)

tapeout_mode=0

if outMode=='macro' or outMode=='full':
	#--------------------------------------------------------
	# generate Feed Forward DCO 
	#--------------------------------------------------------
	dco_bleach=1 # test switch
	dco_synth=1
	dco_apr=1
	W_dco,H_dco=run_digital_flow.dco_flow(pvtFormatDir,dco_flowDir,dcoName,dco_bleach,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,dco_synth,dco_apr,verilogSrcDir,platform,edge_sel,buf_small,buf_big,bufz,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,max_r_l,cust_place,single_ended,FC_half,CC_stack,dco_CC_name,dco_FC_name,cp_version,welltap_dim,welltap_xc,ND,outputDir,synthTool,track)
	#--------------------------------------------------------
	# generate output buffer, divider 
	#--------------------------------------------------------
	buf_bleach=1
	buf_design=1
	buf_lvs=0
	if outbuff_div==1:
		run_digital_flow.outbuff_div_flow(pvtFormatDir,outbuff_div_flowDir,bufName,platform,buf_bleach,buf_design)
		if buf_lvs==1:
			run_digital_flow.buf_custom_lvs(calibreRulesDir,outbuff_div_flowDir,extDir,bufName,pvtFormatDir,platform)
	#--------------------------------------------------------
	# generate PDpll 
	#--------------------------------------------------------
	pdpll_bleach=1
	pdpll_synth=1 # test switch
	pdpll_apr=1
	W_dco,H_dco,W_pll,H_pll=run_digital_flow.pdpll_flow(pvtFormatDir,pll_flowDir,dco_flowDir,outbuff_div_flowDir,pll_name,dcoName,pdpll_bleach,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,pdpll_synth,pdpll_apr,verilogSrcDir,outbuff_div,tdc_dff,buf_small,buf_big,platform,pll_max_r_l,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,H_stdc,FCW,vco_per,outputDir,synthTool,track)
	A_core=W_pll*H_pll

	#--------------------------------------------------------
	# run independent lvs 
	#--------------------------------------------------------
	if custom_lvs==1:
		VDDnames=['VDD','VDD_DCO','VDD_BUF']
		lvs=1  # do lvs for default
		pex=0
		buf=1
		run_digital_flow.pdpll_custom_lvs(VDDnames,buf,bufName,pll_name+'_dco',calibreRulesDir,pll_flowDir,extDir,pvtFormatDir,platform,pll_name,lvs,pex)

	if outMode=='full': 
		#--------------------------------------------------------
		# run analog sim
		#--------------------------------------------------------
		print ('#======================================================================')
		print ('# running post-pex analog sim for DCO alone')
		print ('#======================================================================')
		run_pex_flow.gen_post_pex_netlist(platform, dcoName, pvtFormatDir, dco_flowDir, extDir, calibreRulesDir, wellpin, pex_spectre)
		run_pex_sim.gen_dco_pex_wrapper(extDir,pex_netlistDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,ninterp,dcoName,fc_en_type,FC_half)
		run_pex_sim.gen_tb_wrapped(hspiceModel,pex_tbDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,vdd,temp,fc_en_type,pex_sim_time,corner_lib,dcoName,pex_netlistDir,single_ended, pex_spectre,tapeout_mode)
		dcoNames=[dcoName]
		run_pex_sim.gen_mkfile_pex(pvtFormatDir,hspiceDir,pex_resDir,pex_tbDir,num_core,dcoNames,tech_node)

		#-------------------------------------------
		# read pex sim results
		#-------------------------------------------
		print ('#======================================================================')
		print ('# Reading pex simulation results')
		print ('#======================================================================')
		num_meas=3 #freq, per, iavg
		index=1
		show=1
		Ncc=['ncell',Ncc]
		Ndrv=['ndrv',Ndrv]
		Ndrv=['ndrv',Ndrv]
		#idK,Kg,Fnom,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=HSPICE_result.gen_result_v3(resultDir,Ncc,Ndrv,Nfc,Nstg,num_meas,index,show,vdd,temp)
		idK,Kg,Fnom,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=run_pex_sim.gen_result_v3(tbDir,Ncc,Ndrv,Nfc,Nstg,num_meas,index,show,vdd,temp)

		jsonSpec['pex sim results']={'platform': 'tsmc65lp'}
		jsonSpec['pex sim results']['frequency']={'nom':Fnom}
		jsonSpec['pex sim results']['frequency'].update({'min':Fmin})
		jsonSpec['pex sim results']['frequency'].update({'max':Fmax})
		jsonSpec['pex sim results'].update({'power':Iavg*vdd[0]*1e3}) # in mW
		jsonSpec['pex sim results'].update({'area':A_core}) # in um^2 (need to check)
		print("measured specs generated on "+outputDir+'/pll_spec_out.json')

		with open(outputDir+'/'+designName+'.json','w') as resultSpecfile:
			json.dump(jsonSpec, resultSpecfile, indent=True)
		
	#--------------------------------------------------------
	# export deliverables
	# 	since simulation time takes more than a day,
	#	expected specs derived by model can be provided
	#	through setting use_model=1
	#--------------------------------------------------------
	print ('#======================================================================')
	print ('# exporting deliverables')
	print ('#======================================================================')
	p = sp.Popen(['cp', pll_flowDir+'/export/'+designName+'.gds.gz', \
	        outputDir+'/'+designName+'.gds.gz'])
	p.wait()
	p = sp.Popen(['cp', pll_flowDir+'/export/'+designName+'.lef', \
	        outputDir+'/'+designName+'.lef'])
	p.wait()
	p = sp.Popen(['cp', pll_flowDir+'/export/'+designName+'_min.lib', \
	        outputDir+'/'+designName+'.lib'])
	p.wait()
	p = sp.Popen(['cp', pll_flowDir+'/export/'+designName+'_min.db', \
		     outputDir+'/'+designName+'.db'])
	p.wait()
	p = sp.Popen(['cp', pll_flowDir+'/export/'+designName+'.lvs.v', \
		      outputDir+'/'+designName+'.v'])
	p.wait()
	p = sp.Popen(['cp', extDir+'/sch/'+designName+'.spi', \
		      outputDir+'/'+designName+'.spi'])
	p.wait()

if outMode!='full': #public
	#== calculate estimated area ==
	A_dco=1.5*(A_CC*Ncc*Nstg+A_FC*Nfc*Nstg)
	A_pll=A_dco*1.5	
	jsonSpec['results']={'platform': platform}
	jsonSpec['results']['frequency']={'nom':Fnom_mdl}
	jsonSpec['results']['frequency'].update({'min':Fmin_mdl})
	jsonSpec['results']['frequency'].update({'max':Fmax_mdl})
	jsonSpec['results'].update({'power':Pwr_mdl*1e3}) # in mW
	jsonSpec['results'].update({'area':A_pll}) # in um^2  (need to check)
	jsonSpec['results'].update({'aspect_ratio':'1:1'})
	if outMode=='macro' or outMode=='full':
		jsonSpec['results'].update({'area':A_core})
	print("model predicted specs generated on "+outputDir+'/'+designName+'.json')
	with open(outputDir+'/'+designName+'.json','w') as resultSpecfile:
		json.dump(jsonSpec, resultSpecfile, indent=True)


#--------------------------------------------------------
# run verilog sim only if runVsim==1
#--------------------------------------------------------
if runVsim==1:
	print ('#======================================================================')
	print ('# Running verilog simulation of controller for digital functional verification')
	print ('#======================================================================')

	verTbDir=absGenDir + 'verilog_sim/tb/'
	verDir=absGenDir + 'verilog_sim/'
	simvision=0
	run_pre_sim.tb_verilog_gen(formatDir,verTbDir,relBW,Kp_o_Ki,Fref,dFf,dFc,FCW,Fbase,Ndrv,Ncc,Nfc,Nstg)

	p = sp.Popen(['./:run'],cwd=verDir)
	p.wait()

	if simvision==1:
		p = sp.Popen(['simvision &'],cwd=verDir)
		p.wait()

