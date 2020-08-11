#!/usr/bin/env python3

#======== Verilog wrapper ==========
import sys
import getopt
import math
import subprocess as sp
import fileinput
import re
import shutil
import numpy as np
import argparse
import json
import glob

import operator

import function
import os
import CDC_netlist

from readparamgen import check_search_done, platformConfig, designName, args, jsonSpec
import time
import re

#------------------------------------------------------------------------------
# Clean the workspace
#------------------------------------------------------------------------------
print('#----------------------------------------------------------------------')
print('# Cleaning the workspace...')
print('#----------------------------------------------------------------------')
#p = sp.Popen(['make','bleach_all'], cwd=flowDir)
#p.wait()

genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

head_tail_0 = os.path.split(os.path.abspath(genDir))
head_tail_1 = os.path.split(head_tail_0[0])
privateGenDir = os.path.relpath(os.path.join(genDir, '../../', 'private', head_tail_1[1], head_tail_0[1]))

print(head_tail_0)
print(head_tail_1)
print(privateGenDir)


#flowDir = genDir + './flow'
flowDir = os.path.join(privateGenDir , './flow')
extDir = genDir + '../../private/generators/cdc-gen//extraction'
simDir = genDir + '../../private/generators/cdc-gen//hspice'
srcDir = genDir + './src'



for file in os.listdir(simDir + '/'):
   if not os.path.isdir(simDir + '/' + file):
      os.remove(simDir + '/' + file)
if os.path.isdir(simDir + '/run'):
   shutil.rmtree(simDir + '/run', ignore_errors=True)
if os.path.isdir(extDir + '/run'):
   shutil.rmtree(extDir + '/run', ignore_errors=True)

try:
   os.mkdir(extDir + '/run')
except OSError:
   print('Unable to create the "run" directory in "extraction" folder')

try:
   os.mkdir(simDir + '/run')
except OSError:
   print('Unable to create the "run" directory in "hspice" folder')

if args.mode != 'verilog':
   if not os.path.isdir(privateGenDir):   
      print('Error. Private directory does not exist. ' + \
            'Please use only \'verilog\' mode.')
      sys.exit(1)


npre, ninv, power_min, error_min = check_search_done()
#print("Number of INV(odd number):")
#ninv=int(input())-1
#print("Number of PRECHARGESW:")
#npre=int(input())
#print("Number of HEADER:")
#nhead=int(input())
print("INV:{0} PreSW:{1}".format(ninv,npre))

ninv=int(ninv)
print('#----------------------------------------------------------------------')
print('# Verilog Generation')
print('#----------------------------------------------------------------------')




time.sleep(2)

# Define the internal variables used
#ptCell = 'PT_UNIT_CELL'



if args.platform == 'tsmc65lp' :
  print("Selecting Aux Cells from platform: " + args.platform)
  aux1 = 'INVXRVT_ISOVDD'
  aux2 = 'BUFX4RVT_ISOVDD'
  aux3 = 'INV_X1M_A9TR'
  aux4 = 'BUF_X4M_A9TR'
  aux5 = 'NAND2_X1M_A9TR'
  aux6 = 'INV_X2M_A9TR'
  aux7 = 'NOR2_X1M_A9TR'
  aux8 = 'NAND3_X1M_A9TR'
  aux9 = 'XNOR2_X1M_A9TR'
  aux10 = 'PRECHARGEX1'
  aux11 = 'LC1P2TO3P6X1RVT_VDDX4'
  aux12 = 'DFFRPQ_X1M_A9TR'
if args.platform == 'gf12lp' :
  print("Selecting Aux Cells from platform: " + args.platform)
  aux1 = 'INVP_X0P4N_A10P5PP84TR_C14'
  aux2 = 'BUF_X0P4N_A10P5PP84TR_C14'
  aux3 = 'INVP_X0P4N_A10P5PP84TR_C14'
  aux4 = 'BUF_X0P4N_A10P5PP84TR_C14'
  aux5 = 'NAND2_X0P4N_A10P5PP84TR_C14'
  aux6 = 'INVP_X0P4N_A10P5PP84TR_C14'
  aux7 = 'NOR2_X0P4N_A10P5PP84TR_C14'
  aux8 = 'NAND3_X0P4N_A10P5PP84TR_C14'
  aux9 = 'XNOR2_X0P6N_A10P5PP84TR_C14'
  aux10 = 'PRECHARGEX1'
  aux11 = 'SLC_cell'
  aux12 = 'DFFRPQ_X1N_A10P5PP84TR_C14'


##change
# #aLib1 = platformConfig['aux_lib'] + '/libs/' + aux1
# aLib2 = platformConfig['aux_lib'] + '/libs/' + aux2
# aLib3 = platformConfig['aux_lib'] + '/libs/' + aux3
# aLib4 = platformConfig['aux_lib'] + '/libs/' + aux4
# aLib5 = platformConfig['aux_lib'] + '/libs/' + aux5
# aLib6 = platformConfig['aux_lib'] + '/libs/' + aux6
# aLib7 = platformConfig['aux_lib'] + '/libs/' + aux7
# aLib8 = platformConfig['aux_lib'] + '/libs/' + aux8
# aLib9 = platformConfig['aux_lib'] + '/libs/' + aux9
# aLib10 = platformConfig['aux_lib'] + '/libs/' + aux10
# aLib11 = platformConfig['aux_lib'] + '/libs/' + aux11
# aLib12 = platformConfig['aux_lib'] + '/libs/' + aux12

##change
aLib1 = platformConfig['aux_lib'] + aux1 + '/latest/'
aLib2 = platformConfig['aux_lib'] + aux2 + '/latest/'
aLib3 = platformConfig['aux_lib'] + aux3 + '/latest/'
aLib4 = platformConfig['aux_lib'] + aux4 + '/latest/'
aLib5 = platformConfig['aux_lib'] + aux5 + '/latest/'
aLib6 = platformConfig['aux_lib'] + aux6 + '/latest/'
aLib7 = platformConfig['aux_lib'] + aux7 + '/latest/'
aLib8 = platformConfig['aux_lib'] + aux8 + '/latest/'
aLib9 = platformConfig['aux_lib'] + aux9 + '/latest/'
aLib10 = platformConfig['aux_lib'] + aux10 + '/latest/'
aLib11 = platformConfig['aux_lib'] + aux11 + '/latest/'
aLib12 = platformConfig['aux_lib'] + aux12 + '/latest/'

aLib = platformConfig['aux_lib']

calibreRulesDir = platformConfig['calibreRules']

CDC_netlist.gen_cdc_invchainiso(ninv,aux1,aux2,srcDir)
CDC_netlist.gen_cdc_invchain(ninv,aux3,aux4,srcDir)
CDC_netlist.gen_cdc_nxt_edge_gen(aux4,aux5,aux6,aux7,srcDir)
CDC_netlist.gen_cdc_dly_comp(aux6,aux5,aux4,aux8,aux9,srcDir)
CDC_netlist.gen_cdc_analog(npre,aux10,aux11,srcDir)
CDC_netlist.gen_cdc_cnt(aux12,aux3,aux5,aux4,srcDir)
CDC_netlist.gen_cdc_top(aux6,aux4,srcDir)

shutil.copyfile(srcDir + '/cdcInst.v',   flowDir + '/src/' + designName + '.v')
shutil.copyfile(srcDir + '/CDCW_CNT.v',   flowDir + '/src/' + 'CDCW_CNT' + '.v')
shutil.copyfile(srcDir + '/CDC_ANALOG.nl.v',   flowDir + '/src/' + 'CDC_ANALOG.nl' + '.v')
shutil.copyfile(srcDir + '/DLY_COMP.nl.v',   flowDir + '/src/' + 'DLY_COMP.nl' + '.v')
shutil.copyfile(srcDir + '/NEXT_EDGE_GEN.nl.v',   flowDir + '/src/' + 'NEXT_EDGE_GEN.nl' + '.v')
shutil.copyfile(srcDir + '/CDC_ANALOG2.nl.v',   flowDir + '/src/' + 'CDC_ANALOG2.nl' + '.v')
shutil.copyfile(srcDir + '/INVCHAIN_ISOVDD.nl.v',   flowDir + '/src/' + 'INVCHAIN_ISOVDD.nl' + '.v')

with open(flowDir + '/src/' + designName  + '.v', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'cdcInst*', r' ' + \
                  designName, filedata)
with open(flowDir + '/src/' + designName + '.v', 'w') as file:
   file.write(filedata)

print('#----------------------------------------------------------------------')
print('# Verilog Generated')
print('#----------------------------------------------------------------------')

# designAreaVerilog= 2621.44 + 2621.4*0.001*nhead
# jsonSpec['results'] = {'platform': args.platform}
# jsonSpec['results'].update({'area': designAreaVerilog})
# jsonSpec['results'].update({'error': error})
# jsonSpec['results'].update({'power': power})

# with open(args.outputDir + '/' + designName + '.json', 'w') as resultSpecfile:
#    json.dump(jsonSpec, resultSpecfile, indent=True)

time.sleep(2)
if args.mode == 'verilog':
  print("Exiting tool....")
  exit()
#------------------------------------------------------------------------------
# Configure Synth and APR scripts
#------------------------------------------------------------------------------
print('#----------------------------------------------------------------------')
print('# Configuring Synth and APR scripts...')
print('#----------------------------------------------------------------------')

with open(flowDir + '/include.mk', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'export DESIGN_NAME :=.*', r'export DESIGN_NAME := ' + \
                  designName, filedata)
filedata = re.sub(r'export PLATFORM *:=.*', r'export PLATFORM    := ' + \
                  args.platform, filedata)
with open(flowDir + '/include.mk', 'w') as file:
   file.write(filedata)


# Update the verilog file list for Synthesis
with open(flowDir + '/scripts/dc/dc.filelist.tcl', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'append MAIN_SOURCE_FILE.*', r'append MAIN_SOURCE_FILE ' + \
                  '\"' + designName + '.v\"', filedata)
filedata = re.sub(r'#+append', r'append', filedata)
with open(flowDir + '/scripts/dc/dc.filelist.tcl', 'w') as file:
   file.write(filedata)



# Update the constraints
with open(flowDir + '/scripts/dc/constraints.tcl', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'#+set_dont_touch', r'set_dont_touch', filedata)
with open(flowDir + '/scripts/dc/constraints.tcl', 'w') as file:
   file.write(filedata)

flowPtExportDir = flowDir+"/blocks/PT_UNIT_CELL/export"
if not os.path.exists(flowPtExportDir):
  os.makedirs(flowPtExportDir)


if args.platform == 'tsmc65lp' :   
  shutil.copyfile(aLib + '/'  + aux1 + '/latest/' + aux1 + '_tt.db',   flowPtExportDir + "/" + aux1 + '_tt.db')
  shutil.copyfile(aLib + '/'  + aux2 + '/latest/' + aux2 + '_tt.db',   flowPtExportDir + "/" + aux2 + '_tt.db')
  shutil.copyfile(aLib + '/'  + aux10 + '/latest/' + aux10 + '_tt.db',   flowPtExportDir + "/" + aux10 + '_tt.db')
  shutil.copyfile(aLib + '/'  + aux11 + '/latest/' + aux11 + '_tt.db',   flowPtExportDir + "/" + aux11 + '_tt.db')

  shutil.copyfile(aLib + '/'  + aux1 + '/latest/' + aux1 + '_tt.lib',   flowPtExportDir + "/" + aux1 + '_tt.lib')
  shutil.copyfile(aLib + '/'  + aux2 + '/latest/' + aux2 + '_tt.lib',   flowPtExportDir + "/" + aux2 + '_tt.lib')
  shutil.copyfile(aLib + '/'  + aux10 + '/latest/' + aux10 + '_tt.lib',   flowPtExportDir + "/" + aux10 + '_tt.lib')
  shutil.copyfile(aLib + '/'  + aux11 + '/latest/' + aux11 + '_tt.lib',   flowPtExportDir + "/" + aux11 + '_tt.lib')

  shutil.copyfile(aLib + '/'  + aux1 + '/latest/' + aux1 + '_tt.lef',   flowPtExportDir + "/" + aux1 + '_tt.lef')
  shutil.copyfile(aLib + '/'  + aux2 + '/latest/' + aux2 + '_tt.lef',   flowPtExportDir + "/" + aux2 + '_tt.lef')
  shutil.copyfile(aLib + '/'  + aux10 + '/latest/' + aux10 + '_tt.lef',   flowPtExportDir + "/" + aux10 + '_tt.lef')
  shutil.copyfile(aLib + '/'  + aux11 + '/latest/' + aux11 + '_tt.lef',   flowPtExportDir + "/" + aux11 + '_tt.lef')

  shutil.copyfile(aLib + '/'  + aux1 + '/latest/' + aux1 + '_tt.cdl',   flowPtExportDir + "/" + aux1 + '_tt.cdl')
  shutil.copyfile(aLib + '/'  + aux2 + '/latest/' + aux2 + '_tt.cdl',   flowPtExportDir + "/" + aux2 + '_tt.cdl')
  shutil.copyfile(aLib + '/'  + aux10 + '/latest/' + aux10 + '_tt.cdl',   flowPtExportDir + "/" + aux10 + '_tt.cdl')
  shutil.copyfile(aLib + '/'  + aux11 + '/latest/' + aux11 + '_tt.cdl',   flowPtExportDir + "/" + aux11 + '_tt.cdl')

  shutil.copyfile(aLib + '/'  + aux1 + '/latest/' + aux1 + '_tt.gds',   flowPtExportDir + "/" + aux1 + '_tt.gds')
  shutil.copyfile(aLib + '/'  + aux2 + '/latest/' + aux2 + '_tt.gds',   flowPtExportDir + "/" + aux2 + '_tt.gds')
  shutil.copyfile(aLib + '/'  + aux10 + '/latest/' + aux10 + '_tt.gds',   flowPtExportDir + "/" + aux10 + '_tt.gds')
  shutil.copyfile(aLib + '/'  + aux11 + '/latest/' + aux11 + '_tt.gds',   flowPtExportDir + "/" + aux11 + '_tt.gds')

if args.platform == 'gf12lp' :
  shutil.copyfile(aLib + '/' + aux10 + '/latest/'  + aux10 + '.db',   flowPtExportDir + "/" + aux10 + '.db')
  shutil.copyfile(aLib + '/' + aux11 + '/latest/'  + aux11 + '.db',   flowPtExportDir + "/" + aux11 + '.db')
  shutil.copyfile(aLib + '/' + aux10 + '/latest/'  + aux10 + '.db',   flowPtExportDir + "/" + aux10 + '.lib')
  shutil.copyfile(aLib + '/' + aux11 + '/latest/'  + aux11 + '.db',   flowPtExportDir + "/" + aux11 + '.lib')
  shutil.copyfile(aLib + '/' + aux10 + '/latest/'  + aux10 + '.db',   flowPtExportDir + "/" + aux10 + '.lef')
  shutil.copyfile(aLib + '/' + aux11 + '/latest/'  + aux11 + '.db',   flowPtExportDir + "/" + aux11 + '.lef')
  shutil.copyfile(aLib + '/' + aux10 + '/latest/'  + aux10 + '.db',   flowPtExportDir + "/" + aux10 + '.cdl')
  shutil.copyfile(aLib + '/' + aux11 + '/latest/'  + aux11 + '.db',   flowPtExportDir + "/" + aux11 + '.cdl')
  shutil.copyfile(aLib + '/' + aux10 + '/latest/'  + aux10 + '.db',   flowPtExportDir + "/" + aux10 + '.gds')
  shutil.copyfile(aLib + '/' + aux11 + '/latest/'  + aux11 + '.db',   flowPtExportDir + "/" + aux11 + '.gds')


time.sleep(1)


print('#----------------------------------------------------------------------')
print('# Synthesis...')
print('#----------------------------------------------------------------------')


time.sleep(1)
print("Checking required files....")
time.sleep(1)

#------------------------------------------------------------------------------
# Run Synthesis and APR
#------------------------------------------------------------------------------
exit()
p = sp.Popen(['make','synth'], cwd=flowDir)
p.wait()



# Get the cell area estimate from synthesis report
with open(flowDir + '/reports/dc/' + designName + '.mapped.area.rpt', \
     'r')as file:
   filedata = file.read()
m = re.search('Total cell area: *([0-9.]*)', filedata)
if m:
   coreCellArea = float(m.group(1))
else:
   print("Synthesis Failed")
   sys.exit(1)

# Calculate and update the core cell area dimensions
coreDim = math.ceil(math.sqrt(coreCellArea*8)/5)*5
with open(flowDir + '/scripts/innovus/always_source.tcl', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'set core_width.*', r'set core_width    ' + \
        str(coreDim) + ' ;# Core Area Width', filedata)
filedata = re.sub(r'set core_height.*', r'set core_height   ' + \
        str(coreDim) + ' ;# Core Area Height', filedata)
with open(flowDir + '/scripts/innovus/always_source.tcl', 'w') as file:
   file.write(filedata)

print('#----------------------------------------------------------------------')
print('# Place and Route')
print('#----------------------------------------------------------------------')

time.sleep(1)
# Run the APR flow
p = sp.Popen(['make','design'], cwd=flowDir)
p.wait()

print('#----------------------------------------------------------------------')
print('# Place and Route finished')
print('#----------------------------------------------------------------------')


time.sleep(2)

p = sp.Popen(['make','lvs'], cwd=flowDir)
p.wait()


with open(flowDir+'/results/calibre/lvs/_'+designName+'.lvs.v_stdCellPhyDefs.v_icovlPhyDefs.v_dummy.v.sp', 'r') as file:
   filedata = file.read()
filedata = filedata.replace('OUT_FALL[0] VSS VDD VNW VPW', 'OUT_FALL[0] VSS VDD VDD_CDCANALOG VNW VPW')
filedata = filedata.replace('VSS VNW VPW cdcInst_LC_CDC_ANALOG_0', 'VSS VDD_CDCANALOG VPW cdcInst_LC_CDC_ANALOG_0')
with open(flowDir+'/results/calibre/lvs/_'+designName+'.lvs.v_stdCellPhyDefs.v_icovlPhyDefs.v_dummy.v.sp', 'w') as file:
   file.write(filedata)

time.sleep(2)

with open(flowDir+'/results/calibre/lvs/_lvs.ruleset_', 'r') as file:
   filedata = file.read()
filedata = filedata.replace('lvs.ruleset', 'results/calibre/lvs/lvs.ruleset')
filedata = filedata.replace('lvs.report', 'results/calibre/lvs/lvs.report')
filedata = filedata.replace('svdb', 'results/calibre/lvs/svdb')
filedata = filedata.replace('erc.results', 'results/calibre/lvs/erc.results')
filedata = filedata.replace('erc.summary', 'results/calibre/lvs/erc.summary')

with open(flowDir+'/results/calibre/lvs/_lvs.ruleset_', 'w') as file:
   file.write(filedata)

p = sp.Popen(['calibre','-spice','results/calibre/lvs/lay.net','-turbo','-hyper','-lvs','-hier','-nowait','results/calibre/lvs/_lvs.ruleset_'], cwd=flowDir)
p.wait()

print('#----------------------------------------------------------------------')
print('# LVS finished')
print('#----------------------------------------------------------------------')


time.sleep(2)

p = sp.Popen(['make','drc'], cwd=flowDir)
p.wait()

print('#----------------------------------------------------------------------')
print('# DRC finished')
print('#----------------------------------------------------------------------')


time.sleep(2)
print()
if args.mode == 'macro':
  print("Exiting tool....")
  sys.exit(1)

print('# Exporting files....')
time.sleep(1)

p = sp.Popen(['make','export'], cwd=flowDir)
p.wait()

with open(flowDir + '/reports/innovus/' + designName + \
     '.main.htm.ascii', 'r') as file:
   filedata = file.read()
m = re.search('Total area of Chip: ([0-9.]*)', filedata)
if m:
   designArea = float(m.group(1))
else:
   print('APR Failed')
   sys.exit(1)


for file in glob.glob(flowDir+'/results/calibre/lvs/_'+designName+'*.sp'):
   shutil.copy(file, extDir+'/sch/'+designName+'.spi')

# Copy the merged gds file to extraction directory
p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
         extDir+'/layout/'+designName+'.gds.gz'])
p.wait()

# Clean the space - uncomment

if os.path.isfile(extDir + '/run/svdb/' + designName + '.dv'):
   os.remove(extDir + '/run/svdb/' + designName + '.dv')
if os.path.isfile(extDir + '/run/svdb/' + designName + '.extf'):
   os.remove(extDir + '/run/svdb/' + designName + '.extf')
if os.path.isfile(extDir + '/run/svdb/' + designName + '.lvsf'):
   os.remove(extDir + '/run/svdb/' + designName + '.lvsf')
if os.path.isfile(extDir + '/run/svdb/' + designName + '.pdsp'):
   os.remove(extDir + '/run/svdb/' + designName + '.pdsp')
if os.path.isfile(extDir + '/run/svdb/' + designName + '.sp'):
   os.remove(extDir + '/run/svdb/' + designName + '.sp')

if os.path.isdir(extDir + '/run/svdb/' + designName + '.phdb'):
   shutil.rmtree(extDir + '/run/svdb/' + designName + '.phdb',
                 ignore_errors=True)
if os.path.isdir(extDir + '/run/svdb/' + designName + '.xdb'):
   shutil.rmtree(extDir + '/run/svdb/' + designName + '.xdb',
                 ignore_errors=True)
if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdb'):
   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdb',
                 ignore_errors=True)
if os.path.isdir(extDir + '/run/svdb/' + 'template'):
   shutil.rmtree(extDir + '/run/svdb/' + 'template',
                 ignore_errors=True)

# Configure the PEX rule files
for file in os.listdir(calibreRulesDir + '/'):
   if not os.path.isdir(simDir + '/' + file):
      shutil.copy2(calibreRulesDir+'/'+file, extDir+'/run/')

with open(extDir+'/ruleFiles/_calibre.rcx_'+args.platform, 'r') as file:
   filedata = file.read()
filedata = filedata.replace('design', designName)
with open(extDir+'/run/_calibre.rcx_', 'w') as file:
   file.write(filedata)

print('#----------------------------------------------------------------------')
print('# Running Calibre RCx')
print('#----------------------------------------------------------------------')

# Run Calibre RCX
p = sp.Popen(['calibre','-xrc','-phdb','-nowait','-turbo','1',
             '_calibre.rcx_'],cwd=extDir+'/run')
p.wait()
p = sp.Popen(['calibre','-xrc','-pdb','-rcc','-turbo','1','-nowait',
             '_calibre.rcx_'],cwd=extDir+'/run')
p.wait()
p = sp.Popen(['calibre','-xrc','-fmt','-all','-nowait','_calibre.rcx_'],
             cwd=extDir+'/run')
p.wait()
print('# CDC Sensor - Post PEX netlist Generated')

#------------------------------------------------------------------------------
# Run Hspice Sims
#------------------------------------------------------------------------------


p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.pex',
             simDir+'/spice/'])
p.wait()
p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.'+
             designName+'.pxi', simDir+'/spice/'])
p.wait()

with open(extDir+'/run/'+designName+'.pex.netlist', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'\.subckt .*\n(\+.*\n)*', r'.subckt ' + designName + \
                  ' VSS VDD_CDCANALOG VIN LCOUT OSEN PRECHARGE VDD CLK OUT_RISE[21] CONVFINISH OUT_TOTAL[20] OUT_FALL[20] OUT_FALL[21] OUT_TOTAL[0] OUT_RISE[20] SENSE OUT_TOTAL[21] FINISH OUT_RISE[22] CLKF OUT_TOTAL[12] OUT_TOTAL[1] OUT_FALL[22] CLKR OUT_TOTAL[2] OUT_TOTAL[10] OUT_TOTAL[11] OUT_TOTAL[13] OUT_TOTAL[6] OUT_TOTAL[9] OUT_TOTAL[7] OUT_TOTAL[3] OUT_TOTAL[4] OUT_TOTAL[5] OUT_FALL[1] OUT_TOTAL[8] OUT_FALL[0] OUT_RISE[23] OUT_TOTAL[14] OUT_RISE[12] OUT_RISE[14] OUT_RISE[11] OREF OUT_RISE[13] OUT_TOTAL[22] OUT_RISE[9] OUT_RISE[10] OUT_RISE[7] OUT_FALL[4] OUT_TOTAL[15] OUT_FALL[18] OUT_RISE[0] OUT_FALL[2] OUT_RISE[1] OUT_FALL[3] OUT_RISE[4] OUT_FALL[6] OUT_RISE[6] OUT_FALL[7] OUT_FALL[8] OUT_FALL[9] OUT_FALL[10] OUT_FALL[11] OUT_FALL[12] OUT_FALL[13] OUT_FALL[14] OUT_RISE[15] OUT_FALL[15] OUT_RISE[17] OUT_FALL[17] OUT_TOTAL[17] OUT_TOTAL[19] OUT_RISE[18] OUT_RISE[19] OUT_FALL[23] OUT_TOTAL[23] OUT_RISE[3] OUT_TOTAL[16] OUT_RISE[16] OUT_TOTAL[18] OUT_RISE[5] OUT_RISE[8] OUT_FALL[16] OUT_FALL[19] OUT_RISE[2] OUT_FALL[5] \n', filedata)
with open(simDir+'/spice/'+designName+'.pex.netlist', 'w') as file:
   file.write(filedata)

print('# CDC Sensor - Modify netlist')

with open(simDir+'/ModelSimFile/cdc_'+args.platform+'.sp', 'r') as file:
   filedata = file.read()
filedata = filedata.replace('MODEL_PATH', platformConfig['hspiceModels'])
filedata = filedata.replace('designName', designName)
#filedata = filedata.replace('vin', str(vin))
#filedata = filedata.replace('imax', str(imax))
with open(simDir+'/spice/'+designName+'.sp', 'w') as file:
   file.write(filedata)



   ##### need to write caperature start/stop/step
cap_start = 2
cap_step = 9
cap_factor = 2

stage_var = [ninv]
pre_var = [npre]

cap_var=[]
cap_temp=cap_start
for i in range(0, cap_step+1):
  cap_var.append(cap_temp)
  cap_temp=cap_temp*cap_factor

print(stage_var)
print(pre_var)
print(cap_var)

##### caplate file loading
##r_file = open(file_name, "r")
##lines = r_file.readlines()

r_file = open(simDir+'/spice/'+designName+'.sp', "r")
lines = r_file.readlines()
file_name = designName+'.sp'



##### hspice input file generation with stage and pre
for i in range(0, len(stage_var)):
  for j in range(0, len(pre_var)):
    os.mkdir("./%s/stage%d_pre%d"%(simDir+'/run/', stage_var[i], pre_var[j]))
    #CDC_netlist.gen_CDC_netlist(dir_name, stage_var[i], pre_var[j])
    for t in range(0, len(cap_var)):
      w_file0 = open(genDir + "./%s/stage%d_pre%d/%s_%s.sp"%(simDir+'/run/', stage_var[i], pre_var[j], designName, str(cap_var[t])), "w")
      for line in lines:
        if line[0:2] == '@@':
          nline = line[3:len(line)]
          clist = list(nline)
          for ci in range(0, len(clist)):
            if clist[ci] == '@':
              w_file0.write('%d'%(cap_var[t]))
            elif clist[ci] == '$':
              w_file0.write('%s'%(simDir+'/run/'))
            else:
              w_file0.write(clist[ci])
        else:
          w_file0.write(line)
    w_file1 = open(genDir + "./%s/stage%d_pre%d/run_sim"%(simDir+'/run/',stage_var[i], pre_var[j]), "w") ##run_simgeneration
    for k in range(0, len(cap_var)):
      data = "finesim -mode spicexd %s_%s.sp >log &\n"%(designName, str(cap_var[k]))
      w_file1.write(data)
    w_file2 = open(genDir + "./%s/stage%d_pre%d/cal_result"%(simDir+'/run/', stage_var[i], pre_var[j]), "w")
    for m in range(0, len(cap_var)):
      data = "python code.py %s_%e.mt0 >>code_result\n"%(designName, cap_var[m])
      w_file2.write(data)
    shutil.copy2(genDir + "./tools/code.py", '%s/stage%d_pre%d'%(simDir+'/run/',stage_var[i], pre_var[j]))
    shutil.copy2(genDir + "./tools/code_measure.inc", '%s/stage%d_pre%d'%(simDir+'/run/',stage_var[i], pre_var[j]))
    shutil.copy2(genDir + "./tools/result_error.py", '%s/stage%d_pre%d'%(simDir+'/run/',stage_var[i], pre_var[j]))
    w_file3=open("./%s/stage%d_pre%d/mt_merge"%(simDir+'/run/', stage_var[i], pre_var[j]),"w")

    for l in range(0,len(cap_var)):
      data = "python code.py %s_%e.mt0 >>code_result\n"%(designName,cap_var[l])
      w_file3.write(data)

w_file3.close()
w_file0.close()


folders = os.listdir("%s"%(simDir+'/run/'))

#current = os.getcwd()
for folder in folders:
    print(folder)
#    #os.chdir("%s/%s/%s"%(current,simDir+'/run',folder))
    os.chdir("%s/%s"%(simDir+'/run',folder))
    for k in range(0, len(cap_var)):
      arg = designName+'_'+str(cap_var[k])+'.sp'
      print(designName+'_'+str(cap_var[k])+'.sp')
      #sp.call(['finesim', designName+'_'+str(cap_var[k])+'.sp', '>','log'+str(cap_var[k])])

      command = "finesim"+" "+"-mode spicexd"+" "+arg
      #sp.call(["finesim", arg])
      os.system(command)
      print(command)
      p.wait()
      #exit()
#      #sp.call(['python', 'code.py', designName+'_'+str(cap_var[k])+'.mt0'])





# for folder in folders:
#   print(folder)
#   os.chdir("%s/%s"%(simDir+'/run',folder))
#   os.system("chmod +x run_sim")
#   os.system("source ./run_sim")
#   p.wait()
