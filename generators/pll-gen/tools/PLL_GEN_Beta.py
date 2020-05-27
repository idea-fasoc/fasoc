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
parseList=[1,1,1,1,1,1]  #[specfile,platform,outputDir,pex_verify,run_vsim,mode]
specfile,platform,outputDir,pexVerify,runVsim,outMode=preparations.command_parse(parseList)
specIn=open(specfile,'r')

aLib,mFile,calibreRulesDir,hspiceModel=preparations.config_parse(outMode,configFile,platform)
dco_CC_lib=aLib+'/dco_CC/latest/'
dco_FC_lib=aLib+'/dco_FC/latest/'

#========================================================
# directory path settings
#========================================================
#	public directories
#--------------------------------------------------------
verilogSimDir=absGenDir + 'verilog_sim/'
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
dco_flowDir = absPvtDir_plat + 'flow_dco/'
outbuff_div_flowDir = absPvtDir_plat + 'flow_outbuff_div/'
#outbuff_div_flowDir = pvtFormatDir +platform+ '_flow_outbuff_div/'

if platform=='tsmc65lp':
	fc_en_type = 1 # dco_FC en => increase frequency
	modelVersion='Beta' 
	dco_flowDir = absPvtDir_plat + 'flow_dco/'
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
	custom_lvs=1
elif platform=='gf12lp':
	fc_en_type = 2 # dco_FC en => decrease frequency
	modelVersion='Alpha' 
	dco_flowDir = absPvtDir_plat + 'flow_dco/'
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
	min_p_str_l= 4
	p_rng_w= 1.6 
	p_rng_s= 0.8
	p2_rng_w= 1.2
	p2_rng_s= 0.8
	max_r_l=5
	pll_max_r_l=8
	outbuff_div=0
	tdc_dff='DFFRPQL_X1N_A10P5PP84TR_C14'
	H_stdc=0.672
	custom_lvs=0
#========================================================
# generate directory tree 
#========================================================
print ('#======================================================================')
print ('# check directory tree and generate missing directories')
print ('#======================================================================')
preparations.dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir)

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
	preparations.aux_copy_export(dco_flowDir,dco_CC_lib,dco_FC_lib)
	preparations.aux_copy_export(pll_flowDir,dco_CC_lib,dco_FC_lib)
	W_CC,H_CC,W_FC,H_FC=preparations.aux_parse_size(dco_CC_lib,dco_FC_lib)
	A_CC=W_CC*H_CC
	A_FC=W_FC*H_FC

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
	Fnom_min = float(jsonSpec['specifications']['Fnom_min'])
	Fnom_max = float(jsonSpec['specifications']['Fnom_max'])
	FCR_min = float(jsonSpec['specifications']['FCR_min'])
	Fmax = float(jsonSpec['specifications']['Fmax'])
	Fmin = float(jsonSpec['specifications']['Fmin'])
	Fres = float(jsonSpec['specifications']['Fres'])
	dco_PWR = float(jsonSpec['specifications']['dco_PWR'])
	try: 
		IB_PN = float(jsonSpec['specifications']['inband_PN']) #in dBc
		spec_priority={"Fnom":"dummy","IB_PN":"lo","Fmax":"hi","Fmin":"lo","Fres":"lo","FCR":"hi","dco_PWR":"lo"}					
	except:
		IB_PN=-200 # in case not specified: use dummy value 
		spec_priority={"Fnom":"dummy","Fmax":"hi","Fmin":"lo","Fres":"lo","FCR":"hi","dco_PWR":"lo"}					
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
	mult_Con= 2
	mult_Coff= 2 
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
Ndrv_range=[2,22,4]
Nfc_range=[10,30,4]
Ncc_range=[10,30,4]
Nstg_range=[4,16,4]
vdd=[1.2]
temp=[25]

pass_flag,passed_designs,passed_specs,specRangeDic=modeling.design_solution(spec_priority,Fmax,Fmin,Fres,Fnom_min,Fnom_max,FCR_min,IB_PN,dco_PWR,CF,Cf,Cc,mult_Con,mult_Coff,Iavg_const,PN_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC,modelVersion)


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
	elif modelVersion=='Alpha':
		[Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,FCR_mdl,Pwr_mdl,Area_mdl]=passed_specs[0]
	print ('#======================================================================')
	print ('# selected design solution: ndrv=%d, ncc=%d, nfc=%d, nstg=%d'%(Ndrv,Ncc,Nfc,Nstg))
	if modelVersion=='Beta':
		print ('# expected specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2e, Pwr=%e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,IB_PN_mdl,Pwr_mdl))
		print ('# required specs: Fnom_min,max=%.2e,%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2e'%(Fnom_min,Fnom_max,Fmax,Fmin,Fres,IB_PN))
	elif modelVersion=='Alpha':
		print ('# expected specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, Pwr=%e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,Pwr_mdl))
		print ('# required specs: Fnom_min,max=%.2e,%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e'%(Fnom_min,Fnom_max,Fmax,Fmin,Fres))
	print ('#======================================================================')

	#------------------------------------------------------------------------------
	# write output json file 
	#------------------------------------------------------------------------------
	jsonSpec['results']={'platform': 'tsmc65lp'}			
	jsonSpec['results'].update({'Fnom':Fnom_mdl})	
	jsonSpec['results'].update({'FCR':FCR_mdl})	
	jsonSpec['results'].update({'Fmax':Fmax_mdl})	
	jsonSpec['results'].update({'Fmin':Fmin_mdl})	
	jsonSpec['results'].update({'Fres':Fres_mdl})	
	jsonSpec['results'].update({'dco_PWR':Pwr_mdl})
	if modelVersion=='Beta':	
		jsonSpec['results'].update({'inband_PN':IB_PN_mdl})	
	jsonSpec['results'].update({'area': Area_mdl})	
	print("model predicted specs generated on "+outputDir+'/pll_spec_out.json')
	with open(outputDir+'/pll_spec_out.json','w') as resultSpecfile:
		json.dump(jsonSpec, resultSpecfile, indent=True)

elif pass_flag==0:
	print("writing failed result.json")
	jsonSpec['results']={'platform': 'tsmc65lp'}			
	for spec in specRangeDic:
		if specRangeDic[spec]==[]: # passed
			jsonSpec['results'].update({spec:"passed"})	
		else:
			jsonSpec['results'].update({"failed "+spec+" min":specRangeDic[spec][0]})	
			jsonSpec['results'].update({"failed "+spec+" max":specRangeDic[spec][1]})	
			print("failed: model predicted specs generated on "+outputDir+'/pll_spec_out.json')
	with open(outputDir+'/pll_spec_out.json','w') as resultSpecfile:
		json.dump(jsonSpec, resultSpecfile, indent=True)

#--------------------------------------------------------
# set default values (Alpha version)
# derive vco period, FCW
#--------------------------------------------------------
Fref=10e6
Kp_o_Ki=100
relBW=0.1
FCW=np.floor(Fnom_mdl/Fref)+1
FCW=int(FCW)
print('FCW=%d'%(FCW))
Fbase=Fmin_mdl # this should be the Fmin_mdl
dFf=Fres_mdl
dFc=dFf*Ndrv*Nfc/FCR_mdl

vco_per=1/(Fref*FCW)/1e-9 # unit: ns
max_per=vco_per*3.125 #??

#--------------------------------------------------------
# generate PLL verilog, flow setups
#--------------------------------------------------------
# verilog gen
pll_name=designName
dcoName=pll_name+'_dco'
bufName='outbuff_div'
run_digital_flow.pll_verilog_gen(outMode,designName,absGenDir,outputDir,formatDir,pll_flowDir,Ndrv,Ncc,Nfc,Nstg,verilogSrcDir,buf_small,bufz,buf_big,edge_sel,dcoName,platform)

if outMode=='macro' or outMode=='full':
	#--------------------------------------------------------
	# generate Feed Forward DCO 
	#--------------------------------------------------------
	dco_bleach=1 # test switch
	dco_synth=1
	dco_apr=1
	W_dco,H_dco=run_digital_flow.dco_flow(pvtFormatDir,dco_flowDir,dcoName,dco_bleach,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,dco_synth,dco_apr,verilogSrcDir,platform,edge_sel,buf_small,buf_big,bufz,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,max_r_l)
	#--------------------------------------------------------
	# generate output buffer, divider 
	#--------------------------------------------------------
	buf_bleach=1
	buf_design=1
	buf_lvs=1
	run_digital_flow.outbuff_div_flow(pvtFormatDir,outbuff_div_flowDir,bufName,platform,buf_bleach,buf_design)
	if buf_lvs==1:
		run_digital_flow.buf_custom_lvs(calibreRulesDir,outbuff_div_flowDir,extDir,bufName,pvtFormatDir,platform)
	#--------------------------------------------------------
	# generate PDpll 
	#--------------------------------------------------------
	pdpll_bleach=1
	pdpll_synth=1 # test switch
	pdpll_apr=1
	W_dco,H_dco,W_pll,H_pll=run_digital_flow.pdpll_flow(pvtFormatDir,pll_flowDir,dco_flowDir,outbuff_div_flowDir,pll_name,dcoName,pdpll_bleach,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,pdpll_synth,pdpll_apr,verilogSrcDir,outbuff_div,tdc_dff,buf_small,buf_big,platform,pll_max_r_l,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,H_stdc)
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
		run_pex_flow.gen_post_pex_netlist(platform, dcoName, pvtFormatDir, dco_flowDir, extDir, calibreRulesDir, wellpin)
		run_pex_sim.gen_dco_pex_wrapper(extDir,pex_netlistDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,ninterp,dcoName,fc_en_type)
		run_pex_sim.gen_tb_wrapped(hspiceModel,pex_tbDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,vdd,temp,fc_en_type,pex_sim_time,corner_lib,dcoName,pex_netlistDir)
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
		jsonSpec['pex sim results'].update({'nominal frequency':Fnom})
		jsonSpec['pex sim results'].update({'minimum frequency':Fmin})
		jsonSpec['pex sim results'].update({'maximum frequency':Fmax})
		jsonSpec['pex sim results'].update({'power':Iavg*vdd[0]})
		jsonSpec['pex sim results'].update({'area':A_core})
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
	jsonSpec['results']={'platform': 'tsmc65lp'}
	jsonSpec['results'].update({'nominal frequency':Fnom_mdl})
	jsonSpec['results'].update({'minimum frequency':Fmin_mdl})
	jsonSpec['results'].update({'maximum frequency':Fmax_mdl})
	jsonSpec['results'].update({'power':Pwr_mdl})
	jsonSpec['results'].update({'area':A_pll})
	jsonSpec['results'].update({'aspect ratio':'1:1'})
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

