#sort_via_1d_mult test
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

genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

sys.path.append(genDir + './../pymodules/')

import Pll_gen_setup
import MKfile
import HSPICE_mds
import HSPICE_result
import HSPICE_tb
import HSPICEpex_netlist
import Math_model
import Pex_gen
import re
import Flow_setup
import Cadre_flow
#ndrv=8
#ncc=16
#nfc=16
#nstg=8
ninterp=2

configFile=genDir + './../../../config/platform_config.json'

rawPexDir=genDir + 'extraction/run'
formatDir=genDir + 'formats/'
modelDir=genDir + 'model/'
netlistDir=genDir + 'HSPICE/pex_NETLIST/'
tbDir=genDir + 'HSPICE/pex_TB/'
extDir=genDir + 'extraction/'
flowDir=genDir + 'flow_dco/'
simDir = genDir + 'HSPICE/'
resultDir=simDir+'pex_DUMP_result/'
tech_node='65nm'
resultrfDir=simDir+'DUMPrf_result/'
num_core=4
homeDir=genDir
homeDir=homeDir+'/'

vdd=[1.2]   #vdd[0] is the nominal val
temp=[25] #tmep[0] is the nominal val

vm1=HSPICE_mds.varmap()
vm1.get_var('n_cc',8,16,8)   #[0]=n_cc
vm1.get_var('n_drv',8,16,8)  #[1]=n_drv
vm1.get_var('n_fc',16,32,16)  #[2]=n_fc
vm1.get_var('n_stg',10,12,2)  #[3]=n_stg

vm1.cal_nbigcy()
vm1.combinate()

nccList=vm1.comblist[0]
ndrvList=vm1.comblist[1]
nfcList=vm1.comblist[2]
nstgList=vm1.comblist[3]
#--------------------------------------------------------
# parse the command & config.json
#--------------------------------------------------------

parseList=[0,1,0,0,0,0]  #[specfile,platform,outputDir,pex_verify,run_vsim,mode]
specfile,platform,outputDir,pexVerify,runVsim,outMode=Pll_gen_setup.command_parse(parseList)
aLib,mFile,calibreRulesDir,hspiceModel=Pll_gen_setup.config_parse(configFile,platform)
dco_CC_lib=aLib+'/dco_CC/export/'
dco_FC_lib=aLib+'/dco_FC/export/'

W_CC,H_CC,W_FC,H_FC=Pll_gen_setup.dco_aux_parse(flowDir,dco_CC_lib,dco_FC_lib)

#-------------------------------------------
# Width and Height of the auxcells: for area calculation
#-------------------------------------------
bleach=1
design=1
pex=1

for i in range(1,len(vm1.comblist[0])):
	ndrv=vm1.comblist[1][i]
	ncc=vm1.comblist[0][i]
	nfc=vm1.comblist[2][i]
	nstg=vm1.comblist[3][i]
	designName='dco_%ddrv_%dcc_%dfc_%dstg'%(ndrv,ncc,nfc,nstg)
	Cadre_flow.dco_flow_pex(calibreRulesDir,netlistDir,formatDir,homeDir+flowDir,rawPexDir,extDir,simDir,ndrv,ncc,nfc,nstg,ninterp,W_CC,H_CC,W_FC,H_FC,bleach,design,pex)
#------------------------------------------------------------------------------
#  make HSPICE directory tree
#------------------------------------------------------------------------------
hspice=1
Pll_gen_setup.dir_tree(hspice,0)

#-------------------------------------------
# generate testbench
#-------------------------------------------
for i in range(1,len(vm1.comblist[0])):
	ndrv=vm1.comblist[1][i]
	ncc=vm1.comblist[0][i]
	nfc=vm1.comblist[2][i]
	nstg=vm1.comblist[3][i]
	designName='dco_%ddrv_%dcc_%dfc_%dstg'%(ndrv,ncc,nfc,nstg)
	sav=0
	tb=HSPICE_tb.gen_tb_pex(hspiceModel,tbDir,formatDir,ncc,ndrv,nfc,nstg,nstg,1,vdd,temp,600,designName,sav)
print("%d number of testbench generated on "%(len(vm1.comblist[0]))+tbDir)

#-------------------------------------------
# generate makefile
#-------------------------------------------

num_core=4
hspiceDir=genDir + 'HSPICE/'
hspiceResDir=genDir + 'pex_DUMP_result'
tbDirName=genDir + 'pex_TB'
MKfile.gen_mkfile_pex(formatDir,hspiceDir,hspiceResDir,tbDirName,nccList,ndrvList,nfcList,nstgList,num_core)

#-------------------------------------------
# run pex HSPICE sim
#-------------------------------------------
try:
	p = sp.Popen(['make','pex_hspicesim'])
	p.wait()
except:
	print('problem with pex_hspicesim')
	sys.exit(1)

#-------------------------------------------
# read pex sim results
#-------------------------------------------
num_meas=3 #freq, per, iavg
index=1
show=1
idK,Kg,Fnom,Fmax,Fmin,Fres,FCR,Iavg,result_exist,dm=HSPICE_result.gen_result_v3(resultDir,vm1.comblist[0],vm1.comblist[1],vm1.comblist[2],vm1.comblist[3],num_meas,index,show,vdd,temp)
print ("Fmax=")
print (Fmax)
print ("Fnom=")
print (Fnom)
print ("Fmin=")
print (Fmin)

preMdl=open(modelDir+'pre_pll_model.json','r')
jsonMdl= json.load(preMdl)
CF= float(jsonMdl['pll_model_constants']['CF'])
Cc= float(jsonMdl['pll_model_constants']['Cc'])
Cf= float(jsonMdl['pll_model_constants']['Cf'])
#-------------------------------------------
# generate model constants for pex
#-------------------------------------------
multCcon=[]
multCcoff=[]
pexIavgConst=[]
for nd in result_exist:
	Fmax_meas=Fmax[nd][0][0]
	Fmin_meas=Fmin[nd][0][0]
	Fnom_meas=Fnom[nd][0][0]
	Iavg_meas=Iavg[nd][0][0]
	Fres_meas=Fres[nd][0][0]
	FCR_meas=FCR[nd][0][0]

	Ndrv=dm[nd][0]
	Ncc=dm[nd][1]
	Nfc=dm[nd][3]
	Nstg=dm[nd][2]
	Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,freqCoverRatio,Ctotal= Math_model.spec_cal(Ndrv,Ncc,Nfc,Nstg,Cc,Cf,CF)
	Fmax_pex_ratio=Fmax_mdl/Fmax_meas
	Fmin_pex_ratio=Fmin_mdl/Fmin_meas
	mult_Con=Fmax_pex_ratio
	mult_Coff=(Ndrv+Ncc)/Ndrv*Fmin_pex_ratio-mult_Con
	print(mult_Con,mult_Coff)
	Fmax_mdl,Fmin_mdl,Fres_mdl,Fnom_mdl,FCR_mdl,Ctotal= Math_model.spec_cal_pex65(Ndrv,Ncc,Nfc,Nstg,Cc,Cf,CF,mult_Con,mult_Coff)
	Fmax_pex_ratio=Fmax_mdl/Fmax_meas
	Fnom_pex_ratio=Fnom_mdl/Fnom_meas
	Fmin_pex_ratio=Fmin_mdl/Fmin_meas
	Fres_pex_ratio=Fres_mdl/Fres_meas
	FCR_pex_ratio=FCR_mdl/FCR_meas
	Iavg_const=Iavg_meas/Ctotal
	if Fmax_meas< Fnom_meas or Fnom_meas < Fmin_meas or Fmax_meas < Fmin_meas:
		print("*** wrong result on design %d"%(nd))
	else:
		print("*** right result on design %d"%(nd))
		multCcon.append(mult_Con)
		multCcoff.append(mult_Coff)
		pexIavgConst.append(Iavg_const)
	print("Fmax, Fnom, Fmin, Fres, FCR, Iavg_const =")
	print(Fmax_pex_ratio,Fnom_pex_ratio,Fmin_pex_ratio,Fres_pex_ratio,FCR_pex_ratio,Iavg_const)

#-------------------------------------------
# average the constant
#-------------------------------------------
mult_Con=sum(multCcon)/len(multCcon)
mult_Coff=sum(multCcoff)/len(multCcoff)
pex_Iavg_const=sum(pexIavgConst)/len(pexIavgConst)

#-------------------------------------------
# write pex_model.json
#-------------------------------------------
preMdl=open(modelDir+'pre_pll_model.json','r')
jsonMdl= json.load(preMdl)
jsonMdl['pex coefficients']={'mult_Con':mult_Con}
jsonMdl['pex coefficients'].update({'mult_Coff':mult_Coff})
jsonMdl['pex coefficients'].update({'pex_Iavg_const':abs(pex_Iavg_const)})

with open(modelDir+'pll_model.json','w') as resultSpecfile:
	json.dump(jsonMdl, resultSpecfile, indent=True)
	print('*** pll_model including pex effect generated on: '+modelDir+'pll_model.json')

