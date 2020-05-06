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
absPvtDir = os.path.join(absGenDir,"../../../private/generators/pll-gen/")
print("absGenDir=%s"%(absGenDir))
print("absPvtDir=%s"%(absPvtDir))
genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")
pllDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../../")
head_tail_0 = os.path.split(os.path.abspath(pllDir))
head_tail_1 = os.path.split(head_tail_0[0])

sys.path.append(genDir + './../pymodules/')

import MKfile
import Tb_verilog_gen
import HSPICE_mds
import HSPICE_tb
import HSPICE_result
import Math_model
import Design_solution
import Cadre_flow
import Pex_gen
import Pll_gen_setup
import Flow_setup
import FFdco_flow 
import PDpll_flow 
import Beta_pex_gen 
import Beta_tb 
import Beta_HSPICEpex_netlist
import Beta_HSPICE_result

privateGenDir = os.path.relpath(os.path.join(genDir, '../../../', 'private', head_tail_1[1], head_tail_0[1]))
privatePyDir = os.path.join(privateGenDir , './pymodules/')
#print("privateGenDir=%s"%(privateGenDir))
#sys.exit(1)
#sys.path.append(privatePyDir)
#import HSPICE_subckt


#--------------------------------------------------------
#	public directories
#--------------------------------------------------------
verilogSimDir=genDir + 'verilog_sim/'
verilogSrcDir=genDir + 'verilogs/'
formatDir=genDir + 'formats/'
homeDir=os.getcwd() # this is for absolute path for aux cell path in .spi
homeDir=homeDir+'/'
configFile=genDir + './../../../config/platform_config.json'
vdd=[1.2]
temp=[25]

#--------------------------------------------------------
# parse the command & config.json
#--------------------------------------------------------

parseList=[1,1,1,1,1,1]  #[specfile,platform,outputDir,pex_verify,run_vsim,mode]
specfile,platform,outputDir,pexVerify,runVsim,outMode=Pll_gen_setup.command_parse(parseList)
specIn=open(specfile,'r')

aLib,mFile,calibreRulesDir,hspiceModel=Pll_gen_setup.config_parse(outMode,configFile,platform)
dco_CC_lib=aLib+'/dco_CC/latest/'
dco_FC_lib=aLib+'/dco_FC/latest/'

#--------------------------------------------------------
# directory path settings
#--------------------------------------------------------
#	private directories
#--------------------------------------------------------
netlistDir = os.path.join(privateGenDir , './tsmc65lp/HSPICE/pex_NETLIST/')
tbDir = os.path.join(privateGenDir , './tsmc65lp/HSPICE/pex_TB/')
pvtFormatDir = os.path.join(privateGenDir , './tsmc65lp/formats/')
extDir = os.path.join(privateGenDir , './tsmc65lp/extraction/')
simDir = os.path.join(privateGenDir , './tsmc65lp/HSPICE/')
fs_simDir = os.path.join(privateGenDir , './tsmc65lp/FINESIM/')
absSimDir = os.path.join(absPvtDir , './tsmc65lp/HSPICE/')
fs_absSimDir = os.path.join(absPvtDir , './tsmc65lp/FINESIM/')
ffdco_flowDir = os.path.join(privateGenDir , './tsmc65lp/flow_ffdco/')
outbuff_div_flowDir = os.path.join(privateGenDir, './tsmc65lp/flow_outbuff_div/')
pdpll_flowDir = os.path.join(privateGenDir, './tsmc65lp/flow_pdpll/')
dcoFlowDir = os.path.join(privateGenDir , './tsmc65lp/flow_dco/')
#--------------------------------------------------------
# check for private directory 
#--------------------------------------------------------
if outMode=='macro' or outMode=='full':
	if os.path.isdir(privateGenDir)!=1:
		print("Error: Need private directory for mode 'macro' or 'full'. Currently not there.")
		sys.exit(1)
	sys.path.append(privatePyDir)
	import HSPICE_subckt
	#--------------------------------------------------------
	#	read the aux-cells	
	#--------------------------------------------------------
	W_CC,H_CC,W_FC,H_FC=Pll_gen_setup.dco_aux_parse(ffdco_flowDir,dco_CC_lib,dco_FC_lib)
	W_CC,H_CC,W_FC,H_FC=Pll_gen_setup.dco_aux_parse(pdpll_flowDir,dco_CC_lib,dco_FC_lib)
	A_CC=W_CC*H_CC
	A_FC=W_FC*H_FC

#--------------------------------------------------------
# generate directory tree 
#--------------------------------------------------------
print ('#======================================================================')
print ('# check directory tree and generate missing directories')
print ('#======================================================================')
#==hspice directory tree==
hspice=1
finesim=1
Pll_gen_setup.dir_tree(outMode,privateGenDir,hspice,finesim,outputDir,extDir,calibreRulesDir)
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
	IB_PN = float(jsonSpec['specifications']['inband_PN']) #in dBc
	dco_PWR = float(jsonSpec['specifications']['dco_PWR']) 
except:
	print('Error: wrong categories in spec.json, refer to provided example')
	sys.exit(1)	

#===============================================================
# generate dictionary list for spec priority 
#===============================================================
spec_priority={"Fnom":"dummy","IB_PN":"lo","Fmax":"hi","Fmin":"lo","Fres":"lo","FCR":"lo","dco_PWR":"lo"}					

if Fnom_min >= Fnom_max:
	print('Error: Fnom_min should be greater than Fnom_max')
	sys.exit(1)	

# when there is no model file, generate one
if not os.path.isfile(mFile):
	if outMode=='verilog': # use public model
		mFile=os.path.join(genDir,'./publicModel/pll_model.json')
		print('*** public model file is used: %s'%(mFile))
	elif outMode=='macro' or outMode=='full':	
		p = sp.Popen(['python','tools/MDL_GEN_65nm.py','--platform',platform])
		p.wait()
		p = sp.Popen(['python','tools/PEX_MDL_GEN_65nm.py','--platform',platform])
		p.wait()

try:
	f = open(mFile, 'r')
	print('*** model file from platform_config.json is properly read')
except ValueError as e:
	print ('Model file creation failed')
	sys.exit(1)
#---------------------------------------------------------------------------------------
# read model file
#---------------------------------------------------------------------------------------
modelFile=open(mFile)
jsonModel= json.load(modelFile)
CF= jsonModel['pll_model_constants']['CF']
Cc= jsonModel['pll_model_constants']['Cc']
Cf= jsonModel['pll_model_constants']['Cf']
A_CC= jsonModel['pll_model_constants']['A_CC']
A_FC= jsonModel['pll_model_constants']['A_FC']
Iavg_const= jsonModel['pll_model_constants']['Iavg_const']
mult_Con= jsonModel['pex coefficients']['mult_Con']
mult_Coff= jsonModel['pex coefficients']['mult_Coff']
pex_Iavg_const=jsonModel['pex coefficients']['pex_Iavg_const']
PN_const= jsonModel['pll_model_constants']['1M_PN_const']

print('model constants read properly: CF=%e, mult_Con=%e'%(CF,mult_Con))
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

pass_flag,passed_designs,passed_specs,specRangeDic=Design_solution.ds_Fnom_v2(spec_priority,Fmax,Fmin,Fres,Fnom_min,Fnom_max,FCR_min,IB_PN,dco_PWR,CF,Cf,Cc,mult_Con,mult_Coff,Iavg_const,PN_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC)


#--------------------------------------------------------
# select the design with least area(Alpha version) 
#--------------------------------------------------------
if pass_flag==1:
	areaMdl=[]
	for ii in range(len(passed_specs)):
		areaMdl.append(passed_specs[ii][5])
		
	sys.setrecursionlimit(10000)  #expand the recursion limit if exceeded
	try:
		HSPICE_mds.sort_via_1d_mult(areaMdl,passed_specs,passed_designs)
	except:
		print("sorting failed due to recursion limit: using the first design that meets the spec")
	print ('passed_specs=')
	print (passed_specs[0])
	final_specs=passed_specs[0]
	[Ndrv,Ncc,Nfc,Nstg]=passed_designs[0]
	[Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,FCR_mdl,Pwr_mdl,Area_mdl,IB_PN_mdl]=passed_specs[0]
	print ('#======================================================================')
	print ('# selected design solution: ndrv=%d, ncc=%d, nfc=%d, nstg=%d'%(Ndrv,Ncc,Nfc,Nstg))
	print ('# expected specs: Fnom=%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2e, Pwr=%e'%(Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,IB_PN_mdl,Pwr_mdl))
	print ('# required specs: Fnom_min,max=%.2e,%.2e, Fmax=%.2e, Fmin=%.2e, Fres=%.2e, IB_PN=%.2e'%(Fnom_min,Fnom_max,Fmax,Fmin,Fres,IB_PN))
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
#---!! current CADRE flow does only valid DRC: LVS needs to be carried out on pll-gen side !!---
#==verilog gen==
Flow_setup.pll_flow_setup(outMode,designName,genDir,outputDir,formatDir,pdpll_flowDir,Ndrv,Ncc,Nfc,Nstg,verilogSrcDir)

if outMode=='macro' or outMode=='full':
	#--------------------------------------------------------
	# generate Feed Forward DCO 
	#--------------------------------------------------------
	pll_name=designName
	bleach_dco=0 # test switch
	ffdco_synth=1
	ffdco_apr=1
	W_dco,H_dco=FFdco_flow.ffdco_flow(pvtFormatDir,ffdco_flowDir,pll_name,bleach_dco,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,ffdco_synth,ffdco_apr,verilogSrcDir)
	
	#--------------------------------------------------------
	# generate outbuff_div 
	#--------------------------------------------------------
	outbuff_div_bleach=0
	outbuff_div_design=0
	FFdco_flow.outbuff_div_flow(outbuff_div_flowDir,outbuff_div_bleach,outbuff_div_design)

	#--------------------------------------------------------
	# generate PDpll 
	#--------------------------------------------------------
	pdpll_synth=1 # test switch
	pdpll_apr=1
	pdpll_bleach=0
	W_dco,H_dco,W_pll,H_pll=PDpll_flow.pdpll_flow(pvtFormatDir,pdpll_flowDir,ffdco_flowDir,outbuff_div_flowDir,pll_name,pdpll_bleach,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,pdpll_synth,pdpll_apr,verilogSrcDir)
	A_core=W_pll*H_pll	
	#--------------------------------------------------------
	# run independent lvs 
	#--------------------------------------------------------
	VDDnames=['VDD','VDD_DCO','VDD_BUF']
	lvs=1  # do lvs for default
	pex=0
	buf=1
	Beta_pex_gen.post_apr_HM(VDDnames,buf,'outbuff_div',pll_name+'_ffdco',calibreRulesDir,homeDir+pdpll_flowDir,extDir,pll_name,lvs,pex)

	if outMode=='full': 
		#--------------------------------------------------------
		# run analog sim
		#--------------------------------------------------------
		print ('#======================================================================')
		print ('# running post-pex analog sim for DCO alone')
		print ('#======================================================================')
		#-------------------------------------------
		# generate testbench
		#-------------------------------------------
		finesim=1
		testbench=1
		if testbench==1:
			sav=1
			tb=Beta_tb.gen_tb_pex(CF*mult_Con,Cc*mult_Con,Cf*mult_Con,hspiceModel,finesim,fs_simDir+'pex_TB/',pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,Nstg,1,vdd,temp,25,pll_name+'_ffdco',sav)

		lvs=0		
		pex=0		
		Pex_gen.post_apr(calibreRulesDir,absPvtDir+ffdco_flowDir,extDir,simDir,pll_name+'_ffdco',lvs,pex)
		#-------------------------------------------
		# generate pex Netlist (wrapped netlist)
		#-------------------------------------------
		Beta_HSPICEpex_netlist.gen_dco_pex_netlist(extDir+'/run',fs_absSimDir+'pex_NETLIST/',pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,2,pll_name+'_ffdco')
		#-------------------------------------------
		# copy .pxi, .pex
		#-------------------------------------------
		p = sp.Popen(['cp',extDir+'/run/'+pll_name+'_ffdco.pex.netlist.'+pll_name+'_ffdco.pxi',fs_simDir+'pex_NETLIST/'+pll_name+'_ffdco.pex.netlist.'+pll_name+'_ffdco.pxi'])
		p.wait()
		p = sp.Popen(['cp',extDir+'/run/'+pll_name+'_ffdco.pex.netlist.pex',fs_simDir+'pex_NETLIST/'+pll_name+'_ffdco.pex.netlist.pex'])
		p.wait()
		#-------------------------------------------
		# run finesim 
		#-------------------------------------------
		p = sp.Popen(['finesim','./../pex_TB/tb_'+pll_name+'_ffdco.sp'],cwd=fs_simDir+'pex_DUMP_result')
		p.wait()
		sys.exit(1)

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
		idK,Kg,Fnom,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=Beta_HSPICE_result.gen_result_v3(tbDir,Ncc,Ndrv,Nfc,Nstg,num_meas,index,show,vdd,temp)

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
	p = sp.Popen(['cp', pdpll_flowDir+'/export/'+designName+'.gds.gz', \
	        outputDir+'/'+designName+'.gds.gz'])
	p.wait()
	p = sp.Popen(['cp', pdpll_flowDir+'/export/'+designName+'.lef', \
	        outputDir+'/'+designName+'.lef'])
	p.wait()
	p = sp.Popen(['cp', pdpll_flowDir+'/export/'+designName+'_min.lib', \
	        outputDir+'/'+designName+'.lib'])
	p.wait()
	p = sp.Popen(['cp', pdpll_flowDir+'/export/'+designName+'_min.db', \
		     outputDir+'/'+designName+'.db'])
	p.wait()
	p = sp.Popen(['cp', pdpll_flowDir+'/export/'+designName+'.lvs.v', \
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

	verTbDir=genDir + 'verilog_sim/tb/'
	verDir=genDir + 'verilog_sim/'
	simvision=0
	Tb_verilog_gen.tb_verilog_gen(formatDir,verTbDir,relBW,Kp_o_Ki,Fref,dFf,dFc,FCW,Fbase,Ndrv,Ncc,Nfc,Nstg)

	p = sp.Popen(['./:run'],cwd=verDir)
	p.wait()

	if simvision==1:
		p = sp.Popen(['simvision &'],cwd=verDir)
		p.wait()

