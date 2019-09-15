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

privateGenDir = os.path.relpath(os.path.join(genDir, '../../../', 'private', head_tail_1[1], head_tail_0[1]))
privatePyDir = os.path.join(privateGenDir , './pymodules/')
#sys.path.append(privatePyDir)
#import HSPICE_subckt


#--------------------------------------------------------
#	public directories
#--------------------------------------------------------
verilogSimDir=genDir + 'verilog_sim/'
formatDir=genDir + 'formats/'
#flowDir=genDir + 'flow_pll/'

#homeDir=genDir
homeDir=os.getcwd() # this is for absolute path for aux cell path in .spi
homeDir=homeDir+'/'


configFile=genDir + './../../../config/platform_config.json'

flowDir = os.path.join(privateGenDir , './tsmc65lp/flow_pll/')
#designName='synth_pll'

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
	W_CC,H_CC,W_FC,H_FC=Pll_gen_setup.dco_aux_parse(flowDir,dco_CC_lib,dco_FC_lib)
	A_CC=W_CC*H_CC
	A_FC=W_FC*H_FC

#--------------------------------------------------------
# directory path settings
#--------------------------------------------------------
#	private directories
#--------------------------------------------------------
#netlistDir=genDir + 'HSPICE/pex_NETLIST/'
netlistDir = os.path.join(privateGenDir , './tsmc65lp/HSPICE/pex_NETLIST/')
#tbDir=genDir + 'HSPICE/pex_TB/'
tbDir = os.path.join(privateGenDir , './tsmc65lp/HSPICE/pex_TB/')
pvtFormatDir = os.path.join(privateGenDir , './tsmc65lp/formats/')
#extDir=genDir + 'extraction/'
extDir = os.path.join(privateGenDir , './tsmc65lp/extraction/')
#simDir='HSPICE/'
simDir = os.path.join(privateGenDir , './tsmc65lp/HSPICE/')
absSimDir = os.path.join(absPvtDir , './tsmc65lp/HSPICE/')
flowDir = os.path.join(privateGenDir , './tsmc65lp/flow_pll/')
dcoFlowDir = os.path.join(privateGenDir , './tsmc65lp/flow_dco/')
#--------------------------------------------------------
# generate directory tree 
#--------------------------------------------------------
print ('#======================================================================')
print ('# check directory tree and generate missing directories')
print ('#======================================================================')
#==hspice directory tree==
hspice=1
Pll_gen_setup.dir_tree(outMode,privateGenDir,hspice,outputDir,extDir,calibreRulesDir)
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
except:
	print('Error: wrong categories in spec.json, refer to provided example')
	sys.exit(1)	

if Fnom_min >= Fnom_max:
	print('Error: Fnom_min should be greater than Fnom_max')
	sys.exit(1)	

#FCR_min = float(jsonSpec['specifications']['FCR_min'])
FCR_min=1

#mFile='/test_model.json' # test purpose to check publicModel

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

print('model constants read properly: CF=%e, mult_Con=%e'%(CF,mult_Con))

#--------------------------------------------------------
# search design solutions
#--------------------------------------------------------
print ('#======================================================================')
print ('# searching for design solution')
print ('#======================================================================')

# design space definition: [start,end,step]
Ndrv_range=[10,20,2]
Nfc_range=[30,40,2]
Ncc_range=[10,20,2]
Nstg_range=[8,28,2]

passed_designs, passed_specs=Design_solution.ds_Fnom_pex(Fnom_min,Fnom_max,FCR_min,CF,Cf,Cc,Iavg_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC,mult_Con,mult_Coff,0)

#--------------------------------------------------------
# select the design with least area(Alpha version)
#--------------------------------------------------------
areaMdl=[]
for ii in range(len(passed_specs)):
	areaMdl.append(passed_specs[ii][5])

sys.setrecursionlimit(10000)  #expand the recursion limit if exceeded
try:
	HSPICE_mds.sort_via_1d_mult(areaMdl,passed_specs,passed_designs)
except:
	print("sorting failed due to recursion limit: using the first design that meets the spec")

final_specs=passed_specs[0]
[Ndrv,Ncc,Nfc,Nstg]=passed_designs[0]
[Fnom_mdl,Fmax_mdl,Fmin_mdl,Fres_mdl,FCR_mdl,Pwr_mdl,Area_mdl]=passed_specs[0]
print ('#======================================================================')
print ('# selected design solution: ndrv=%d, ncc=%d, nfc=%d, nstg=%d'%(Ndrv,Ncc,Nfc,Nstg))
print ('#======================================================================')

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
# generate PLL
#--------------------------------------------------------
flat=1 # flattened pll
#---!! current CADRE flow does only valid DRC: LVS needs to be carried out on pll-gen side !!---
#==verilog gen==
Flow_setup.pll_flow_setup(outMode,designName,genDir,outputDir,formatDir,flowDir,Ndrv,Ncc,Nfc,Nstg)

#--------------------------------------------------------
# digital flow
# everything from below should be conducted in privateDir
#--------------------------------------------------------
if outMode=='macro' or outMode=='full':
	bleach=0 #temp
	synth=1
	design=1
	if design==1:
		print ('#======================================================================')
		print ('# running digital flow of generating synth_pll')
		print ('#======================================================================')
	A_core=Cadre_flow.pll_flow(designName,pvtFormatDir,flowDir,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,FCW,vco_per,max_per,bleach,synth,design,flat)

	#--------------------------------------------------------
	# run LVS
	#--------------------------------------------------------
	lvs=0 #temp
	pex=0
	if lvs==1:
		print ('#======================================================================')
		print ('# check Lvs')
		print ('#======================================================================')
	Pex_gen.post_apr(calibreRulesDir,homeDir+flowDir,extDir,simDir,designName,lvs,pex)
	
	
	#--------------------------------------------------------
	# generate DCO, run analog sim
	#--------------------------------------------------------
	print ('#======================================================================')
	print ('# generating DCO alone for analog simulation: will use existing gds if exists')
	print ('#======================================================================')
	#rawPexDir=genDir + 'extraction/run'
	rawPexDir = os.path.join(extDir , './run/')
	bleach=0
	design=1 #temp
	pex=0  #temp
	W_CC,H_CC,W_FC,H_FC=Pll_gen_setup.dco_aux_parse(dcoFlowDir,dco_CC_lib,dco_FC_lib)
	#Cadre_flow.dco_flow_pex(calibreRulesDir,netlistDir,formatDir,homeDir+dcoFlowDir,rawPexDir,extDir,simDir,Ndrv,Ncc,Nfc,Nstg,2,W_CC,H_CC,W_FC,H_FC,bleach,design,pex)
	Cadre_flow.dco_flow_pex(calibreRulesDir,netlistDir,pvtFormatDir,homeDir+dcoFlowDir,rawPexDir,extDir,simDir,Ndrv,Ncc,Nfc,Nstg,2,W_CC,H_CC,W_FC,H_FC,bleach,design,pex) #pvt path
	dcoDesignName='dco_%ddrv_%dcc_%dfc_%dstg'%(Ndrv,Ncc,Nfc,Nstg)
	
	
	sav=0
	#tb=HSPICE_tb.gen_tb_pex(hspiceModel,tbDir,formatDir,Ncc,Ndrv,Nfc,Nstg,Nstg,1,vdd,temp,600,dcoDesignName,sav)
	tb=HSPICE_tb.gen_tb_pex(hspiceModel,tbDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,Nstg,1,vdd,temp,600,dcoDesignName,sav) #pvt path
	num_core=4
	#hspiceDir=genDir + 'HSPICE/' #pvt path
	hspiceDir=simDir
	#hspiceResDir=genDir + 'pex_DUMP_result'
	#hspiceResDir=os.path.join(simDir,'./pex_DUMP_result/')
	hspiceResDir_name='/pex_DUMP_result/'
	nccList=['Ncc',Ncc]
	ndrvList=['Ndrv',Ndrv]
	nfcList=['Nfc',Nfc]
	nstgList=['Nstg',Nstg]
	tbDirName='pex_TB'
	MKfile.gen_mkfile_pex(formatDir,hspiceDir,hspiceResDir_name,tbDirName,nccList,ndrvList,nfcList,nstgList,num_core)

	#--------------------------------------------------------
	# export deliverables
	# 	since simulation time takes more than a day,
	#	expected specs derived by model can be provided
	#	through setting use_model=1
	#--------------------------------------------------------
	print ('#======================================================================')
	print ('# exporting deliverables')
	print ('#======================================================================')
	p = sp.Popen(['cp', flowDir+'/export/'+designName+'.gds.gz', \
	        outputDir+'/'+designName+'.gds.gz'])
	p.wait()
	p = sp.Popen(['cp', flowDir+'/export/'+designName+'.lef', \
	        outputDir+'/'+designName+'.lef'])
	p.wait()
	p = sp.Popen(['cp', flowDir+'/export/'+designName+'_min.lib', \
	        outputDir+'/'+designName+'.lib'])
	p.wait()
	p = sp.Popen(['cp', flowDir+'/export/'+designName+'_min.db', \
		     outputDir+'/'+designName+'.db'])
	p.wait()
	p = sp.Popen(['cp', flowDir+'/export/'+designName+'.lvs.v', \
		      outputDir+'/'+designName+'.v'])
	p.wait()
	p = sp.Popen(['cp', extDir+'/sch/'+designName+'.spi', \
		      outputDir+'/'+designName+'.spi'])
	p.wait()


#if pexVerify==0:
if outMode!='full': #public
	jsonSpec['results']={'platform': 'tsmc65lp'}
	jsonSpec['results'].update({'nominal frequency':Fnom_mdl})
	jsonSpec['results'].update({'minimum frequency':Fmin_mdl})
	jsonSpec['results'].update({'maximum frequency':Fmax_mdl})
	jsonSpec['results'].update({'power':Pwr_mdl})
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


#-------------------------------------------
# run pex sim (only when outMode=='full')
#-------------------------------------------
#if pexVerify==1:
if outMode=='full': #public
	resultDir=simDir+hspiceResDir_name
	print ('#======================================================================')
	print ('# Running pex simulation for analog performance verification')
	print ('#======================================================================')
	#p = sp.Popen(['make','pex_hspicesim'])
	absTbDir=absSimDir+'pex_TB/'
	p = sp.Popen(['hspice','-i',absTbDir+'tb_%dring%d_osc%d_FC%d.sp'%(Ndrv,Ncc,Nstg,Nfc)])
	p.wait()

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
	idK,Kg,Fnom,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=HSPICE_result.gen_result_v3(tbDir,Ncc,Ndrv,Nfc,Nstg,num_meas,index,show,vdd,temp)

	jsonSpec['pex sim results']={'platform': 'tsmc65lp'}
	jsonSpec['pex sim results'].update({'nominal frequency':Fnom})
	jsonSpec['pex sim results'].update({'minimum frequency':Fmin})
	jsonSpec['pex sim results'].update({'maximum frequency':Fmax})
	jsonSpec['pex sim results'].update({'power':Iavg*vdd[0]})
	jsonSpec['pex sim results'].update({'area':A_core})
	print("measured specs generated on "+outputDir+'/pll_spec_out.json')

	with open(outputDir+'/'+designName+'.json','w') as resultSpecfile:
		json.dump(jsonSpec, resultSpecfile, indent=True)

print('outMode=')
print(outMode)
