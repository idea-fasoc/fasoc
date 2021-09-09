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
parseList=[0,1,0,0,0,1]  #[specfile,platform,outputDir,pex_verify,runVsim,mode]
specfile,platform,outputDir,pexVerify,runVsim,outMode=preparations.command_parse(parseList)

configFile=absGenDir + './../../config/platform_config.json'
aLib,mFile,calibreRulesDir,hspiceModel=preparations.config_parse(outMode,configFile,platform)

#------------------------------------------------------------------------------
# Initialize the config variables
#------------------------------------------------------------------------------
formatDir=absGenDir + '/formats/'
pvtFormatDir=absPvtDir + '/formats/'

absPvtDir_plat=absPvtDir+platform+'/'
#hspiceDir=absPvtDir_plat +  '/HSPICE/'
#hspiceDir='/tmp/kmkwon_sim/HSPICE_3st/'
#hspiceDir='/tmp/kmkwon_sim/HSPICE_mod/' # modeling
#hspiceDir='/tmp/kmkwon_sim/HSPICE_mod2/' # modeling
#hspiceDir='/tmp/kmkwon_sim/HSPICE_mod2_2st/' # modeling
#hspiceDir='/tmp/kmkwon_sim/HSPICE_mod3/' # modeling
hspiceDir='/tmp/kmkwon_sim/HSPICE_mod3_halfFC/' # modeling
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
	welltap_dim=[0,0]
	welltap_xc=[0,0]
	cp_version=0 # custom_place version
	FC_version=0 # dco_FC single ended version
	ND=0 # always-off NCCs
elif platform=='gf12lp':
	fc_en_type = 2 # dco_FC en => decrease frequency
	modelVersion='Alpha' 
	dco_flowDir = absPvtDir_plat + 'flow_dco_KBR/'
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
	cp_version=2 # custom_place version
	FC_version=2 # dco_FC single ended version
	ND=6 # always-off NCCs

#------------------------------------------------------------------------------
#  design & test_env sets definition
#------------------------------------------------------------------------------
sys.setrecursionlimit(10000)  #expand the recursion limit if exceeded
vm1=txt_mds.varmap()
# 5stg only
vm1.get_var('n_drv',5,5,1)  #[1]=n_drv
vm1.get_var('n_stg',5,5,1)  #[3]=n_stg

vm1.cal_nbigcy()
vm1.combinate()

temp=[25] #tmep[0] is the nominal val

# search design solution
#------------------------------------------------------------------------------
#  result definition
#------------------------------------------------------------------------------
num_meas=3 #freq, per, iavg
index=1
show=0
print_error=1

#INV_name = 'INVP_X0P6F_A10P5PP84TR_C14'
INV_name = 'INVP_X0P5N_A9PP84TR_C14'

run_flow=1
run_dig_flow=1
gen_model=1

tapeout_mode=0
bleach=1
synth=1
apr=1
pex=1
tb_netlist=1
lvs=0
ninterp=2
num_core=4
if tapeout_mode==0:
	pex_sim_time=8e-9
else:
	pex_sim_time=8e-9

dcoNames=[]
finesim=1

preparations.dir_tree_genus(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform)

if run_flow==1:
	for i in range(1,len(vm1.comblist[0])):
		Ndrv=vm1.comblist[0][i]
		Nstg=vm1.comblist[1][i]
		dcoName='dco_%dndrv_%dnstg'%(Ndrv,Nstg)
		dcoNames.append(dcoName)
		print(dcoName)
		print(dcoNames)
		if run_dig_flow==1:
			run_digital_flow.dco_inv_flow_genus(pvtFormatDir,dco_flowDir,dcoName,bleach,Ndrv,Nstg,platform,INV_name)
