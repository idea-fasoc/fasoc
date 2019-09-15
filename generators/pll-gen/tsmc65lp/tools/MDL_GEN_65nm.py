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

genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")
pllDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../../")
head_tail_0 = os.path.split(os.path.abspath(pllDir))
head_tail_1 = os.path.split(head_tail_0[0])
sys.path.append(genDir + './../pymodules/')

import Pll_gen_setup
import HSPICE_mds
import Math_model
import imp
import HSPICE_netlist
import HSPICE_tb
import HSPICE_result
#import HSPICE_result_FC
#import HSPICErf_result
import HSPICE_tbrf
import MKfile
import HSPICE_Kwrt
import HSPICE_Kpnwrt
#Kg_solver=imp.load_source('Kg_solver','./model/Kg_solver.py')
import Kg_solver

privateGenDir = os.path.relpath(os.path.join(genDir, '../../../', 'private', head_tail_1[1], head_tail_0[1]))
privatePyDir = os.path.join(privateGenDir , './pymodules/')
sys.path.append(privatePyDir)
import HSPICE_subckt
#------------------------------------------------------------------------------
# Initialize the config variables
#------------------------------------------------------------------------------
tech_node='65nm'

genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")




hspiceDir=genDir +  'HSPICE/'
formatDir=genDir + 'formats/'

aux_FC = formatDir+'form_DCO_FC.sp'
aux_CC = formatDir+'form_DCO_CC.sp'
netlistDir=hspiceDir+'NETLIST/'
resultDir=hspiceDir+'DUMP_result/'
resultrfDir=hspiceDir+'DUMPrf_result/'
tbDir=hspiceDir+'TB/'
tbrfDir=hspiceDir+'TBrf/'

aLib = ''
sCell = ''
sLib = ''
digitalFlow = 'digital_flow'
simTool = 'hspice'
extTool = 'calibre'
netlistTool = 'calibredrv'
extDir = 'extraction'
simDir = 'hspice'
num_core=4

#--------------------------------------------------------
# parse the command
#--------------------------------------------------------
parseList=[0,1,0,0,0,0]  #[specfile,platform,outputDir,pex_verify,runVsim,mode]
specfile,platform,outputDir,pexVerify,runVsim,outMode=Pll_gen_setup.command_parse(parseList)

configFile=genDir + './../../../config/platform_config.json'
aLib,mFile,calibreRulesDir,hspiceModel=Pll_gen_setup.config_parse(configFile,platform)

#------------------------------------------------------------------------------
#  make HSPICE directory tree
#------------------------------------------------------------------------------
hspice=1
Pll_gen_setup.dir_tree(hspice,0)

#------------------------------------------------------------------------------
#  Sub-circuit definition for dco_CC
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#  design & test_env sets definition
#------------------------------------------------------------------------------
sys.setrecursionlimit(10000)  #expand the recursion limit if exceeded
vm1=HSPICE_mds.varmap()
vm1.get_var('n_cc',8,16,8)   #[0]=n_cc
vm1.get_var('n_drv',8,16,8)  #[1]=n_drv
vm1.get_var('n_fc',16,32,16)  #[2]=n_fc
vm1.get_var('n_stg',8,10,1)  #[3]=n_stg
vm1.cal_nbigcy()
vm1.combinate()

vdd=[1.2]   #vdd[0] is the nominal val
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
write_model_file='model/pre_pll_model.json'
show=0
print_error=1
#------------------------------------------------------------------------------
#  netlist.sp, tb.sp generation
#------------------------------------------------------------------------------
subckt=HSPICE_subckt.gen_subckt_65nm(netlistDir,aux_CC,aux_FC)
#
try:
	for i in range(1,len(vm1.comblist[0])):
		netlist=HSPICE_netlist.gen_netlist(netlistDir,formatDir,vm1.comblist[0][i],vm1.comblist[1][i],vm1.comblist[2][i],vm1.comblist[3][i],vm1.comblist[3][i],1)
		tb=HSPICE_tb.gen_tb(hspiceModel,tbDir,formatDir,vm1.comblist[0][i],vm1.comblist[1][i],vm1.comblist[2][i],vm1.comblist[3][i],vm1.comblist[3][i],1,vdd,temp,500)
	print("%d number of tb.sp generated"%(len(vm1.comblist[0])-1))
except:
	print('error encountered during netlist/tb generation')
#------------------------------------------------------------------------------
# Makefile generation for hspice simulation
#------------------------------------------------------------------------------
mkfile=MKfile.gen_mkfile_v2(formatDir,hspiceDir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],0,num_core,0)

#------------------------------------------------------------------------------
# Run HSPICE sim
#------------------------------------------------------------------------------
#p=sp.Popen(['make','hspicesim'])
#p.wait()

#------------------------------------------------------------------------------
# Read transient sim result, receive nominal frequencies
#------------------------------------------------------------------------------
idK,Kg,freq,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=HSPICE_result.gen_result_v3(resultDir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],num_meas,index,show,vdd,temp)
#print (result_exist)
#print (freq[0][0][0])
#-------------------------------------
# generate & verify math model
#-------------------------------------
CF,Cc,Cf,CF_err,Cc_err,Cf_err=Math_model.math_model_gen(vm1,netlistDir,formatDir,vdd,temp,tech_node,resultrfDir,num_core,resultDir,index,show,num_meas)
Iavg_const=Math_model.math_model_verify(formatDir,write_model_file,CF,Cc,Cf,dm,result_exist,freq,Fmax,Fmin,Fres,Iavg,print_error)

#------------------------------------------------------------------------------
# rf_testbench.sp generation
#------------------------------------------------------------------------------
#rf=HSPICE_tbrf.gen_tbrf_v3(hspiceModel,formatDir,tbrfDir,dm,freq,result_exist,vdd,temp)
#mkfile=MKfile.gen_mkfile_v2(formatDir,hspiceDir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],1,num_core,result_exist)

#------------------------------------------------------------------------------
# Run HSPICErf sim
#------------------------------------------------------------------------------
#p=sp.Popen(['make','hspicerfsim'])
#p.wait()

#------------------------------------------------------------------------------
# Read rf data, generate PN constant for 10MHz
#------------------------------------------------------------------------------
#Kpn=HSPICErf_result.gen_resultrf(ncell,ndrv,nfc,stg_start,stg_swp,Ncf,fcidx,num_meas+1,0,freq_cc)
#Kpn_avg,Ekpn=HSPICErf_result.gen_printpn(ncell_1,ndrv_1,nfc_1,stg_swp,Kg_1)

#------------------------------------------------------------------------------
# Write the frequency related constants
#------------------------------------------------------------------------------
#write_Kpn=HSPICE_Kpnwrt.write_Kpn(ncell_1,ndrv_1,nfc_1,Kpn_avg,Ekpn)
#


