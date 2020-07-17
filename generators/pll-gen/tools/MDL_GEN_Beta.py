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
hspiceDir='/tmp/kmkwon_sim/HSPICE_3st/'
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
	FC_half=0
	CC_stack=3
	pex_spectre=0
	vdd=[0.8]   #vdd[0] is the nominal val

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

aLib = ''
sCell = ''
sLib = ''
num_core=4

#------------------------------------------------------------------------------
#  make HSPICE directory tree
#------------------------------------------------------------------------------
hspice=1
finesim=0

preparations.dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform)
dco_CC_name,dco_FC_name=preparations.aux_copy_export(dco_flowDir,dco_CC_lib,dco_FC_lib)
#------------------------------------------------------------------------------
#  design & test_env sets definition
#------------------------------------------------------------------------------
sys.setrecursionlimit(10000)  #expand the recursion limit if exceeded
vm1=txt_mds.varmap()
vm1.get_var('n_cc',30,30,1)   #[0]=n_cc
vm1.get_var('n_drv',5,5,1)  #[1]=n_drv
vm1.get_var('n_fc',40,40,1)  #[2]=n_fc
vm1.get_var('n_stg',5,5,1)  #[3]=n_stg
vm1.cal_nbigcy()
vm1.combinate()

temp=[25] #tmep[0] is the nominal val

#------------------------------------------------------------------------------
#  result definition
#------------------------------------------------------------------------------
Ncf=1000
#fcidx_1=2*(nfc_1//4)
#fcidx_2=2*(nfc_2//4)
#fcidx_3=2*(nfc_3//4)
num_meas=3 #freq, per, iavg
index=1
show=0
print_error=1
#------------------------------------------------------------------------------
#  netlist.sp, tb.sp generation
#------------------------------------------------------------------------------

preparations.aux_copy_spice(dco_CC_lib,dco_FC_lib,netlistDir)

for i in range(1,len(vm1.comblist[0])):
	Ncc=vm1.comblist[0][i]
	Ndrv=vm1.comblist[1][i]
	Nfc=vm1.comblist[2][i]
	Nstg=vm1.comblist[3][i]
	designName='%dndrv_%dncc_%dnstg_%dnfc'%(Ndrv,Ncc,Nstg,Nfc)
	netlist=run_pre_sim.gen_netlist(netlistDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,Nstg,1,wellpin,designName)
	tb=run_pre_sim.gen_tb(hspiceModel,tbDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,vdd,temp,fc_en_type,sim_time,corner_lib,designName,netlistDir)
print("%d number of tb.sp generated"%(len(vm1.comblist[0])-1))
#------------------------------------------------------------------------------
# Makefile generation for hspice simulation
#------------------------------------------------------------------------------
mkfile=run_pre_sim.gen_mkfile_v2(formatDir,hspiceDir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],0,num_core,0,tech_node)


#------------------------------------------------------------------------------
# Run HSPICE sim
#------------------------------------------------------------------------------
#p=sp.Popen(['make','hspicesim%(s)'%(tech_node)])
#p.wait()

#------------------------------------------------------------------------------
# Read transient sim result, receive nominal frequencies
#------------------------------------------------------------------------------
#idK,Kg,freq,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=run_pre_sim.gen_result(resultDir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],num_meas,index,show,vdd,temp,fc_en_type)

#-------------------------------------
# generate & verify math model
#-------------------------------------
#CF,Cc,Cf,CF_err,Cc_err,Cf_err=modeling.math_model_gen(vm1,netlistDir,formatDir,vdd,temp,platform,resultrfDir,num_core,resultDir,index,show,num_meas)
#Iavg_const=modeling.math_model_verify(formatDir,mFile,CF,Cc,Cf,dm,result_exist,freq,Fmax,Fmin,Fres,Iavg,print_error)

#------------------------------------------------------------------------------
# rf_testbench.sp generation
#------------------------------------------------------------------------------
#rf=run_pre_sim.gen_tbrf(hspiceModel,formatDir,tbrfDir,dm,freq,result_exist,vdd,temp)
#mkfile=run_pre_sim.gen_mkfile_v2(formatDir,hspiceDir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],1,num_core,result_exist)

#------------------------------------------------------------------------------
# Run HSPICErf sim
#------------------------------------------------------------------------------
#p=sp.Popen(['make','hspicerfsim'])
#p.wait()

#------------------------------------------------------------------------------
# Read rf data, generate PN constant for 10MHz
#------------------------------------------------------------------------------
#Kpn=run_pre_sim.gen_resultrf(ncell,ndrv,nfc,stg_start,stg_swp,Ncf,fcidx,num_meas+1,0,freq_cc)
#Kpn_avg,Ekpn=HSPICErf_result.gen_printpn(ncell_1,ndrv_1,nfc_1,stg_swp,Kg_1)

#------------------------------------------------------------------------------
# Write phase noise constant 
#------------------------------------------------------------------------------
#write_Kpn=run_pre_sim.write_Kpn(ncell_1,ndrv_1,nfc_1,Kpn_avg,Ekpn)
#

#==============================================================================
# post-pex modeling 
#==============================================================================

tapeout_mode=1
bleach=0
synth=1
apr=1
pex=1
lvs=0
ninterp=2
num_core=4
pex_sim_time=20e-9
dcoNames=[]
finesim=1
for i in range(1,len(vm1.comblist[0])):
	Ncc=vm1.comblist[0][i]
	Ndrv=vm1.comblist[1][i]
	Nfc=vm1.comblist[2][i]
	Nstg=vm1.comblist[3][i]
	dcoName='dco_%dndrv_%dncc_%dnstg_%dnfc'%(Ndrv,Ncc,Nstg,Nfc)
	dcoNames.append(dcoName)
	print(dcoName)
	print(dcoNames)
#	W_dco,H_dco=run_digital_flow.dco_flow(pvtFormatDir,dco_flowDir,dcoName,bleach,Ndrv,Ncc,Nfc,Nstg,W_CC,H_CC,W_FC,H_FC,synth,apr,verilogSrcDir,platform,edge_sel,buf_small,buf_big,bufz,min_p_rng_l,min_p_str_l,p_rng_w,p_rng_s,p2_rng_w,p2_rng_s,max_r_l,cust_place,single_ended,FC_half,CC_stack,dco_CC_name,dco_FC_name)
	if lvs==1:
		run_digital_flow.buf_custom_lvs(calibreRulesDir,dco_flowDir,extDir,dcoName,pvtFormatDir,platform)
	if pex==1:
#		run_pex_flow.gen_post_pex_netlist(platform, dcoName, pvtFormatDir, dco_flowDir, extDir, calibreRulesDir, wellpin, pex_spectre)
		run_pex_sim.gen_dco_pex_wrapper(extDir,pex_netlistDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,ninterp,dcoName,fc_en_type,FC_half,pex_spectre)
		if pex_spectre==0:
			run_pex_sim.gen_tb_wrapped(hspiceModel,pex_tbDir,pvtFormatDir,Ncc,Ndrv,Nfc,Nstg,vdd,temp,fc_en_type,pex_sim_time,corner_lib,dcoName,pex_netlistDir,finesim,single_ended,FC_half,pex_spectre,tapeout_mode)

run_pex_sim.gen_mkfile_pex(pvtFormatDir,hspiceDir,pex_resDir,pex_tbDir,num_core,dcoNames,tech_node,finesim)
sys.exit(1)
