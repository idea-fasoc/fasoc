#------------------------------------------------------------------------------
# DCO automatic sim => model wrapper
# added in v2:
# design params are in the form of arrays
# Date: 12/21/2018
#------------------------------------------------------------------------------
import argparse
import sys
import math
import subprocess as sp
import fileinput
import re
import os
import shutil
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

pvtPyDir = os.path.join(absPvtDir, './pymodules/')
sys.path.append(pvtPyDir)
import pvt_run_pre_sim

#--------------------------------------------------------
# parse the command
#--------------------------------------------------------
parseList=[0,1,0,0,0,1,1,1]  #[specfile,platform,outputDir,pex_verify,runVsim,mode,synthTool,track]
specfile,platform,outputDir,pexVerify,runVsim,outMode,synthTool,track=preparations.command_parse(parseList)

configFile=absGenDir + './../../config/platform_config.json'
aLib,mFile,calibreRulesDir,hspiceModel=preparations.config_parse(outMode,configFile,platform)
mFile='/afs/eecs.umich.edu/wics/users/kmkwon/IDEA/fasoc/fasoc/generators/pll-gen/pll_pex_model_gf12lp_FCv2.json'
#mFile='/afs/eecs.umich.edu/wics/users/kmkwon/IDEA/fasoc/fasoc/generators/pll-gen/golden_pll_pex_model_gf12lp.json'
specIn=open('/afs/eecs.umich.edu/wics/users/kmkwon/IDEA/fasoc/fasoc/generators/pll-gen/ble_pll_spec.json','r')
#------------------------------------------------------------------------------
# Initialize the config variables
#------------------------------------------------------------------------------
formatDir=absGenDir + '/formats/'
pvtFormatDir=absPvtDir + '/formats/'
vsimDir=absGenDir + 'verilog_sim/'

absPvtDir_plat=absPvtDir+platform+'/'
#hspiceDir=absPvtDir_plat +  '/HSPICE/'
#hspiceDir='/tmp/kmkwon_sim/HSPICE_3st/'
hspiceDir='/tmp/kmkwon_sim/HSPICE_mod/' # modeling
verilogSrcDir=absGenDir + 'verilogs/'
netlistDir=hspiceDir+'NETLIST/'
pex_netlistDir=hspiceDir+'pex_NETLIST/'
tbDir=hspiceDir+'TB/'
pex_tbDir=hspiceDir+'pex_TB/'
tbrfDir=hspiceDir+'TBrf/'
pex_resDir=hspiceDir+'pex_DUMP_result/'
extDir = absPvtDir_plat + 'extraction/'
finesimDir = absPvtDir_plat + 'FINESIM/'
outbuff_div_flowDir = absPvtDir_plat + 'flow_outbuff_div/'
pll_flowDir = absPvtDir_plat + 'flow_pdpll/'

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
	cust_place=0
	single_ended=0
	CC_stack=2
	FC_half=0
	pex_spectre=0
	vdd=[1.2]   #vdd[0] is the nominal val
	dead_CC=0
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
	min_p_str_l= 5
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
	cust_place=1
	single_ended=1
	FC_half=1
	CC_stack=3
	pex_spectre=0
	vdd=[0.8]   #vdd[0] is the nominal val
	welltap_dim=[]
	dead_CC=1

if pex_spectre==1:
	pex_netlistDir=hspiceDir+'pex_NETLIST_scs/'
	pex_tbDir=hspiceDir+'pex_TB_scs/'
	pex_resDir=hspiceDir+'pex_DUMP_result_scs/'
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
		dco_FC_lib=aLib+'/dco_FC_se_half/latest/'
W_CC,H_CC,W_FC,H_FC=preparations.aux_parse_size(dco_CC_lib,dco_FC_lib)

A_CC=W_CC*H_CC
A_FC=W_FC*H_FC
aLib = ''
sCell = ''
sLib = ''
num_core=4

#------------------------------------------------------------------------------
#  make HSPICE directory tree
#------------------------------------------------------------------------------
hspice=1
finesim=0

preparations.dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform,vsimDir)
dco_CC_name,dco_FC_name=preparations.aux_copy_export(dco_flowDir,dco_CC_lib,dco_FC_lib)

#---------------------------------------------------------------------------------------
# read model file
#---------------------------------------------------------------------------------------
try:
	f = open(mFile, 'r')
	print('INFO: model file from platform_config.json is properly read')
except ValueError as e:
	print ('Error: Model file creation failed')
	sys.exit(1)
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
except:
	print('Error: wrong categories in spec.json, refer to provided example')
	sys.exit(1)	
#--------------------------------------------------------
# search design solutions 
#--------------------------------------------------------
print ('#======================================================================')
print ('# searching for design solution')
print ('#======================================================================')

# design space definition: [start,end,step]
#Ndrv_range=[20,20,1]
#Nfc_range=[10,40,5]
#Ncc_range=[10,30,5]
#Nstg_range=[5,5,1]
Ndrv_range=[28,28,1]
Nfc_range=[16,16,1]
Ncc_range=[24,24,1]
Nstg_range=[5,5,1]
ND =6 
temp=[25]


pass_flag,passed_designs,passed_specs,specRangeDic=modeling.design_solution(spec_priority,Fmax,Fmin,Fres,Fnom_min,Fnom_max,FCR_min,IB_PN,dco_PWR,CF,Cf,Cc,mult_Con,mult_Coff,Iavg_const,PN_const,vdd,Ndrv_range,Nfc_range,Ncc_range,Nstg_range,A_CC,A_FC,modelVersion, FC_half, dead_CC, ND)


sys.exit(1)


