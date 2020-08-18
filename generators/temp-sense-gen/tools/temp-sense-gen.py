#!/usr/bin/env python3.7
#------------------------------------------------------------------------------
# TEMP-SENSE GEN WRAPPER
# IDEA & POSH Integration Excercises
# Date: 04/18/2018
#------------------------------------------------------------------------------
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
import TEMP_netlist
import readparamgen
import os
import time
from readparamgen import check_search_done, platformConfig, designName, args, jsonSpec
#from subprocess import call


genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

head_tail_0 = os.path.split(os.path.abspath(genDir))
head_tail_1 = os.path.split(head_tail_0[0])
privateGenDir = os.path.relpath(os.path.join(genDir, '../../', 'private', head_tail_1[1], head_tail_0[1]))
print(head_tail_0)
print(head_tail_1)
print(privateGenDir)
flowDir = os.path.join(privateGenDir , './flow')
print("flowDir: " + flowDir)
extDir = genDir + '../../private/generators/temp-sense-gen/extraction'
simDir = genDir + '../../private/generators/temp-sense-gen/hspice'
srcDir = genDir + './src'


#------------------------------------------------------------------------------
# Clean the workspace
#------------------------------------------------------------------------------
print('#----------------------------------------------------------------------')
print('# Cleaning the workspace...')
print('#----------------------------------------------------------------------')
if (args.clean):
 p = sp.Popen(['make','bleach_all'], cwd=flowDir)
 p.wait()
 for file in os.listdir(flowDir + '/src/'):
  os.remove(flowDir + '/src/' + file)
   	
 print('Workspace clean done. Exiting the flow.')
 sys.exit(0)

for file in os.listdir(simDir + '/'):
   if not os.path.isdir(simDir + '/' + file):
      os.remove(simDir + '/' + file)
if os.path.isdir(simDir + '/run'):
   shutil.rmtree(simDir + '/run', ignore_errors=True)
if os.path.isdir(extDir + '/run'):
   shutil.rmtree(extDir + '/run', ignore_errors=True)

# if (args.clean):
# print('Workspace cleaning done. Exiting the flow.')
# sys.exit(0)

try:
   os.mkdir(extDir + '/run')
except OSError:
   print('Unable to create the "run" directory in "extraction" folder')

try:
   os.mkdir(simDir + '/run')
except OSError:
   print('Unable to create the "run" directory in "hspice" folder')
#------------------------------------------------------------------------------
# Initialize the config variables
#------------------------------------------------------------------------------

if args.mode != 'verilog':
   if not os.path.isdir(privateGenDir):   
      print('Error. Private directory does not exist. ' + \
            'Please use only \'verilog\' mode.')
      sys.exit(1)



temp, power, error, ninv, nhead, hist = check_search_done()
print ('Error : ' , error)
print('Inv : ' , ninv)
print('Header : ' , nhead)
print('History : ' , hist)
#print("Number of bits:")
#nbit=int(input())
print("INV:{0}\nHEADER:{1}\n".format(ninv,nhead))






print('#----------------------------------------------------------------------')
print('# Verilog Generation')
print('#----------------------------------------------------------------------')


time.sleep(2)



if args.platform == 'tsmc65lp' :
  print("Selecting Aux Cells from platform: " + args.platform)
  aux1 = 'NAND2X1RVT_ISOVDD'
  aux2 = 'INVXRVT_ISOVDD'
  aux3 = 'BUFX4RVT_ISOVDD'
  aux4 = 'BUFX4RVT_ISOVDD'
  aux5 = 'HEADERX1RVT'
  aux6 = 'LC1P2TO3P6X1RVT_VDDX4'
if args.platform == 'gf12lp' :
  print("Selecting Aux Cells from platform: " + args.platform)
  aux1 = 'NAND2_X0P4N_A10P5PP84TR_C14'
  aux2 = 'INVP_X0P4N_A10P5PP84TR_C14'
  aux3 = 'BUF_X0P4N_A10P5PP84TR_C14'
  aux4 = 'BUF_X0P4N_A10P5PP84TR_C14'
  aux5 = 'HEAD14'
  aux6 = 'SLC_cell'
if args.platform == 'sky130':
  print("Selecting Aux Cells from platform: " + args.platform)
  aux1 = 'scs8hs_nand2_1'
  aux2 = 'scs8hs_inv_1'
  aux3 = 'scs8hs_buf_1'
  aux4 = 'scs8hs_buf_1'
  aux5 = 'HEADER'
  aux6 = 'SLC'


##change
aLib1 = platformConfig['aux_lib'] + aux1 + '/latest/'
aLib2 = platformConfig['aux_lib'] + aux2 + '/latest/'
aLib3 = platformConfig['aux_lib'] + aux3 + '/latest/'
aLib4 = platformConfig['aux_lib'] + aux4 + '/latest/'
aLib5 = platformConfig['aux_lib'] + aux5 + '/latest/'
aLib6 = platformConfig['aux_lib'] + aux6 + '/latest/'

aLib = platformConfig['aux_lib']

calibreRulesDir = platformConfig['calibreRules']

ninv=ninv+1
TEMP_netlist.gen_temp_netlist(ninv,nhead,aux1,aux2,aux3,aux4,aux5, srcDir)

print(designName)

shutil.copyfile(srcDir + '/TEMP_ANALOG_lv.nl.v',   flowDir + '/src/' + 'TEMP_ANALOG_lv.nl' + '.v')
shutil.copyfile(srcDir + '/TEMP_ANALOG_hv.nl.v',   flowDir + '/src/' + 'TEMP_ANALOG_hv.nl' + '.v')
shutil.copyfile(srcDir + '/TEMP_AUTO_def.v',   flowDir + '/src/' + 'TEMP_AUTO_def' + '.v')
shutil.copyfile(srcDir + '/tempsenseInst.v',   flowDir + '/src/' + designName  + '.v')

shutil.copyfile(srcDir + '/counter.v',   flowDir + '/src/' + 'counter' + '.v')

with open(flowDir + '/src/' + designName  + '.v', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'tempsenseInst*', r' ' + \
                  designName, filedata)
with open(flowDir + '/src/' + designName + '.v', 'w') as file:
   file.write(filedata)


print('#----------------------------------------------------------------------')
print('# Verilog Generated')
print('#----------------------------------------------------------------------')
#------------------------------------------------------------------------------
# Configure Synth and APR scripts
#------------------------------------------------------------------------------
designAreaVerilog= 2621.44 + 2621.4*0.001*nhead
jsonSpec['results'] = {'platform': args.platform}
jsonSpec['results'].update({'area': designAreaVerilog})
jsonSpec['results'].update({'error': error})
jsonSpec['results'].update({'power': power})

with open(args.outputDir + '/' + designName + '.json', 'w') as resultSpecfile:
   json.dump(jsonSpec, resultSpecfile, indent=True)

time.sleep(2)
print()
if args.mode == 'verilog':
  print("Exiting tool....")
  #sys.exit(1)
  exit()

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

#shutil.copyfile(aLib + '/cdl/' + aux1 + '.cdl',  flowPtExportDir + "/" + aux1 + '.cdl')
if args.platform == 'tsmc65lp' :   
  shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '_tt.db',   flowPtExportDir + "/" + aux1 + '_tt.db')
  shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '_tt.db',   flowPtExportDir + "/" + aux2 + '_tt.db')
  shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '_tt.db',   flowPtExportDir + "/" + aux3 + '_tt.db')
  shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '_tt.db',   flowPtExportDir + "/" + aux4 + '_tt.db')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '_tt.db',   flowPtExportDir + "/" + aux5 + '_tt.db')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '_tt.db',   flowPtExportDir + "/" + aux6 + '_tt.db')

  shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '_tt.lib',   flowPtExportDir + "/" + aux1 + '_tt.lib')
  shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '_tt.lib',   flowPtExportDir + "/" + aux2 + '_tt.lib')
  shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '_tt.lib',   flowPtExportDir + "/" + aux3 + '_tt.lib')
  shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '_tt.lib',   flowPtExportDir + "/" + aux4 + '_tt.lib')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '_tt.lib',   flowPtExportDir + "/" + aux5 + '_tt.lib')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '_tt.lib',   flowPtExportDir + "/" + aux6 + '_tt.lib')

  shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '_tt.lef',   flowPtExportDir + "/" + aux1 + '_tt.lef')
  shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '_tt.lef',   flowPtExportDir + "/" + aux2 + '_tt.lef')
  shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '_tt.lef',   flowPtExportDir + "/" + aux3 + '_tt.lef')
  shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '_tt.lef',   flowPtExportDir + "/" + aux4 + '_tt.lef')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '_tt.lef',   flowPtExportDir + "/" + aux5 + '_tt.lef')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '_tt.lef',   flowPtExportDir + "/" + aux6 + '_tt.lef')

  shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '_tt.cdl',   flowPtExportDir + "/" + aux1 + '_tt.cdl')
  shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '_tt.cdl',   flowPtExportDir + "/" + aux2 + '_tt.cdl')
  shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '_tt.cdl',   flowPtExportDir + "/" + aux3 + '_tt.cdl')
  shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '_tt.cdl',   flowPtExportDir + "/" + aux4 + '_tt.cdl')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '_tt.cdl',   flowPtExportDir + "/" + aux5 + '_tt.cdl')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '_tt.cdl',   flowPtExportDir + "/" + aux6 + '_tt.cdl')

  shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '_tt.gds',   flowPtExportDir + "/" + aux1 + '_tt.gds')
  shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '_tt.gds',   flowPtExportDir + "/" + aux2 + '_tt.gds')
  shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '_tt.gds',   flowPtExportDir + "/" + aux3 + '_tt.gds')
  shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '_tt.gds',   flowPtExportDir + "/" + aux4 + '_tt.gds')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '_tt.gds',   flowPtExportDir + "/" + aux5 + '_tt.gds')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '_tt.gds',   flowPtExportDir + "/" + aux6 + '_tt.gds')

if args.platform == 'gf12lp' :
  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.db',   flowPtExportDir + "/" + aux1 + '.db')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.db',   flowPtExportDir + "/" + aux2 + '.db')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.db',   flowPtExportDir + "/" + aux3 + '.db')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.db',   flowPtExportDir + "/" + aux4 + '.db')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.db',   flowPtExportDir + "/" + aux5 + '.db')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.db',   flowPtExportDir + "/" + aux6 + '.db')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.lib',   flowPtExportDir + "/" + aux1 + '.lib')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.lib',   flowPtExportDir + "/" + aux2 + '.lib')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.lib',   flowPtExportDir + "/" + aux3 + '.lib')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.lib',   flowPtExportDir + "/" + aux4 + '.lib')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.lib',   flowPtExportDir + "/" + aux5 + '.lib')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.lib',   flowPtExportDir + "/" + aux6 + '.lib')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.lef',   flowPtExportDir + "/" + aux1 + '.lef')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.lef',   flowPtExportDir + "/" + aux2 + '.lef')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.lef',   flowPtExportDir + "/" + aux3 + '.lef')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.lef',   flowPtExportDir + "/" + aux4 + '.lef')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.lef',   flowPtExportDir + "/" + aux5 + '.lef')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.lef',   flowPtExportDir + "/" + aux6 + '.lef')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.cdl',   flowPtExportDir + "/" + aux1 + '.cdl')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.cdl',   flowPtExportDir + "/" + aux2 + '.cdl')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.cdl',   flowPtExportDir + "/" + aux3 + '.cdl')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.cdl',   flowPtExportDir + "/" + aux4 + '.cdl')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.cdl',   flowPtExportDir + "/" + aux5 + '.cdl')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.cdl',   flowPtExportDir + "/" + aux6 + '.cdl')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.gds',   flowPtExportDir + "/" + aux1 + '.gds')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.gds',   flowPtExportDir + "/" + aux2 + '.gds')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.gds',   flowPtExportDir + "/" + aux3 + '.gds')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.gds',   flowPtExportDir + "/" + aux4 + '.gds')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.gds',   flowPtExportDir + "/" + aux5 + '.gds')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.gds',   flowPtExportDir + "/" + aux6 + '.gds')
  

if args.platform == 'sky130':
  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.db',   flowPtExportDir + "/" + aux1 + '.db')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.db',   flowPtExportDir + "/" + aux2 + '.db')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.db',   flowPtExportDir + "/" + aux3 + '.db')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.db',   flowPtExportDir + "/" + aux4 + '.db')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.db',   flowPtExportDir + "/" + aux5 + '.db')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.db',   flowPtExportDir + "/" + aux6 + '.db')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.lib',   flowPtExportDir + "/" + aux1 + '.lib')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.lib',   flowPtExportDir + "/" + aux2 + '.lib')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.lib',   flowPtExportDir + "/" + aux3 + '.lib')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.lib',   flowPtExportDir + "/" + aux4 + '.lib')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.lib',   flowPtExportDir + "/" + aux5 + '.lib')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.lib',   flowPtExportDir + "/" + aux6 + '.lib')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.lef',   flowPtExportDir + "/" + aux1 + '.lef')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.lef',   flowPtExportDir + "/" + aux2 + '.lef')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.lef',   flowPtExportDir + "/" + aux3 + '.lef')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.lef',   flowPtExportDir + "/" + aux4 + '.lef')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.lef',   flowPtExportDir + "/" + aux5 + '.lef')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.lef',   flowPtExportDir + "/" + aux6 + '.lef')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.cdl',   flowPtExportDir + "/" + aux1 + '.cdl')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.cdl',   flowPtExportDir + "/" + aux2 + '.cdl')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.cdl',   flowPtExportDir + "/" + aux3 + '.cdl')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.cdl',   flowPtExportDir + "/" + aux4 + '.cdl')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.cdl',   flowPtExportDir + "/" + aux5 + '.cdl')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.cdl',   flowPtExportDir + "/" + aux6 + '.cdl')

  #shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.gds',   flowPtExportDir + "/" + aux1 + '.gds')
  #shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.gds',   flowPtExportDir + "/" + aux2 + '.gds')
  #shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.gds',   flowPtExportDir + "/" + aux3 + '.gds')
  #shutil.copyfile(aLib + '/' + aux4 + '/latest/'  + aux4 + '.gds',   flowPtExportDir + "/" + aux4 + '.gds')
  shutil.copyfile(aLib + '/' + aux5 + '/latest/'  + aux5 + '.gds',   flowPtExportDir + "/" + aux5 + '.gds')
  shutil.copyfile(aLib + '/' + aux6 + '/latest/'  + aux6 + '.gds',   flowPtExportDir + "/" + aux6 + '.gds')


#shutil.copyfile(aLib + '/gds/' + ptCell + '.gds2', flowPtExportDir + "/" + ptCell + '.gds2')

time.sleep(1)

print('#----------------------------------------------------------------------')
print('# Synthesis...')
print('#----------------------------------------------------------------------')
time.sleep(1)
print("Checking required files....")



time.sleep(1)

#TEMP_netlist.gen_temp_coutnterbits(nbit)
#synthesis

#------------------------------------------------------------------------------
# Run Synthesis and APR
#------------------------------------------------------------------------------

# Run the Synthesis flow
print("flowDir: " + flowDir)

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
coreDim = math.ceil(math.sqrt(coreCellArea*2.3)/5)*8
with open(flowDir + '/scripts/innovus/always_source.tcl', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'set core_width.*', r'set core_width    ' + \
        str(coreDim) + ' ;# Core Area Width', filedata)
filedata = re.sub(r'set core_height.*', r'set core_height   ' + \
        str(coreDim) + ' ;# Core Area Height', filedata)
with open(flowDir + '/scripts/innovus/always_source.tcl', 'w') as file:
   file.write(filedata)

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


print('#----------------------------------------------------------------------')
print('# LVS finished')
print('#----------------------------------------------------------------------')


time.sleep(2)

p = sp.Popen(['make','drc'], cwd=flowDir)
p.wait()



print('#----------------------------------------------------------------------')
print('# DRC finished')
print('#----------------------------------------------------------------------')



#shutil.copytree(flow + '/export', args.outputDir)
p = sp.Popen(['cp', './results/calibre/'+designName+'.merged.gds.gz', \
        '../../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.merged.gds.gz'], cwd=flowDir)
p.wait()
p = sp.Popen(['cp', './export/'+designName+'.lef', \
        '../../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.lef'], cwd=flowDir)
p.wait()
p = sp.Popen(['cp', './export/'+designName+'_typ.lib', \
         '../../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.lib'], cwd=flowDir)
p.wait()
p = sp.Popen(['cp', './export/'+designName+'_typ.db', \
          '../../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.db'], cwd=flowDir)
p.wait()
p = sp.Popen(['cp', './export/'+designName+'.lvs.v', \
          '../../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.v'], cwd=flowDir)
p.wait()
p = sp.Popen(['cp', '../extraction/sch/'+designName+'.spi', \
          '../../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.spi'], cwd=flowDir)
p.wait()


time.sleep(2)
print()
if args.mode == 'macro':
  print("Exiting tool....")
  exit()


time.sleep(2)

print('# Exporting files....')
time.sleep(1)

p = sp.Popen(['make','export'], cwd=flowDir)
p.wait()

# if platform != 'gf12lp':
#   p = sp.Popen(['make','export'], cwd=flowDir)
#   p.wait()


with open(flowDir + '/reports/innovus/' + designName + \
     '.main.htm.ascii', 'r') as file:
   filedata = file.read()
m = re.search('Total area of Chip: ([0-9.]*)', filedata)
if m:
   designArea = float(m.group(1))
else:
   print('APR Failed')
   sys.exit(1)


#------------------------------------------------------------------------------
# Generate post PEX netlist
#------------------------------------------------------------------------------
#Generate pre PEX netlist and gds files
# cdlInclude = ''
# cdlParse   = ''
# with open(flowDir + '/scripts/innovus/generated/' + designName + \
#      '.cdlList', 'r') as file:
#    filedata = file.readlines()
# for line in filedata:
#    cdlInclude = cdlInclude + ' -s ' + line.rstrip()
#    cdlParse   = cdlParse + ' -lsr ' + line.rstrip()

# # NOTE: The exported version of the gds is not merged (i.e. doesn't include standard cells)
#  p = sp.Popen(['cp', flowDir+'/export/'+designName+'.gds.gz', \
#          extDir+'/layout/'+designName+'.gds.gz'])
# p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
#          extDir+'/layout/'+designName+'.gds.gz'])
# p.wait()

# Copy the cdl netlist to extraction directory
for file in glob.glob(flowDir+'/results/calibre/lvs/_'+designName+'*.sp'):
   shutil.copy(file, extDir+'/sch/'+designName+'.spi')

# Copy the merged gds file to extraction directory
p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
         extDir+'/layout/'+designName+'.gds.gz'])
p.wait()

# Clean the space
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

# # Configure the PEX rule files
# for file in os.listdir(calibreRulesDir + '/'):
#    if not os.path.isdir(simDir + '/' + file):
#       shutil.copy2(calibreRulesDir+'/'+file, extDir+'/run/')
# 
# with open(extDir+'/ruleFiles/_calibre.rcx_'+args.platform, 'r') as file:
#    filedata = file.read()
# filedata = filedata.replace('design', designName)
# with open(extDir+'/run/_calibre.rcx_', 'w') as file:
#    file.write(filedata)
# 
# # Run Calibre RCX
# p = sp.Popen(['calibre','-xrc','-phdb','-nowait','-turbo','1',
#              '_calibre.rcx_'],cwd=extDir+'/run')
# p.wait()
# p = sp.Popen(['calibre','-xrc','-pdb','-rcc','-turbo','1','-nowait',
#              '_calibre.rcx_'],cwd=extDir+'/run')
# p.wait()
# p = sp.Popen(['calibre','-xrc','-fmt','-all','-nowait','_calibre.rcx_'],
#              cwd=extDir+'/run')
# p.wait()
# print('# Temperature Sensor - Post PEX netlist Generated')

if args.platform == 'gf12lp':
   with open(flowDir + '/scripts/innovus/generated/' + designName + \
          '.beolStack', 'r') as file:
      filedata = file.read()
   os.environ['BEOL_STACK'] = filedata.rstrip()
   with open(flowDir + '/scripts/innovus/generated/' + designName + \
          '.techLvsDir', 'r') as file:
      filedata = file.read()
   os.environ['TECHDIR_LVS'] = filedata.rstrip()
   with open(flowDir + '/scripts/innovus/generated/' + designName + \
          '.techPexDir', 'r') as file:
      filedata = file.read()
   os.environ['TECHDIR_XACT'] = filedata.rstrip()
   os.environ['PEX_RUN'] = 'TRUE'

# Configure the PEX rule files
for file in os.listdir(calibreRulesDir + '/'):
   if not os.path.isdir(calibreRulesDir + '/' + file):
      shutil.copy2(calibreRulesDir+'/'+file, extDir+'/run/')

with open(extDir+'/runsets/pex.runset.'+ args.platform, 'r') as file:
   filedata = file.read()
filedata = filedata.replace('design', designName)
with open(extDir+'/run/pex.runset', 'w') as file:
   file.write(filedata)

# Run Calibre RCX
if args.platform == 'gf12lp':
   p = sp.Popen(['calibre','-gui','-xact','-batch','-runset',
                'pex.runset'],cwd=extDir+'/run')
   p.wait()
else:
   p = sp.Popen(['calibre','-gui','-pex','-batch','-runset',
                'pex.runset'],cwd=extDir+'/run')
   p.wait()




#------------------------------------------------------------------------------
# Run Hspice Sims
#------------------------------------------------------------------------------


p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.pex',
             simDir+'/spice/'])
p.wait()
p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.pxi', 
             simDir+'/spice/'])
p.wait()



with open(extDir+'/run/'+designName+'.pex.netlist', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'\.subckt .*\n(\+.*\n)*', r'.subckt ' + designName + \
                  ' VSS VDD DOUT[12] DOUT[13] lc_out DOUT[15] DOUT[2] VIN en DOUT[14] DOUT[11] out outb DOUT[23] DOUT[9] DOUT[16] DOUT[22] DOUT[1] DOUT[0] CLK_REF DOUT[10] DOUT[18] DOUT[3] DOUT[21] DOUT[19] DOUT[8] DOUT[4] DOUT[17] DOUT[20] DONE DOUT[6] DOUT[7] DOUT[5] SEL_CONV_TIME[1] RESET_COUNTERn SEL_CONV_TIME[3] SEL_CONV_TIME[0] SEL_CONV_TIME[2] \n', filedata)
with open(simDir+'/spice/'+designName+'.pex.netlist', 'w') as file:
   file.write(filedata)

print('# Temperature Sensor - Modify netlist')

with open(simDir+'/ModelSimFile/tempsense_'+args.platform+'.sp', 'r') as file:
   filedata = file.read()
filedata = filedata.replace('MODEL_PATH', platformConfig['hspiceModels'])
filedata = filedata.replace('designName', designName)
#filedata = filedata.replace('vin', str(vin))
#filedata = filedata.replace('imax', str(imax))
with open(simDir+'/spice/'+designName+'.sp', 'w') as file:
   file.write(filedata)





##### Directory name for result files
# dir_name = 'run'


# ##### Result directory generation
# try:
#    os.mkdir(dir_name)
# except file_exist_error:
#    print("Directory ", dir_name , "already exists")


##### simulation points calculation

temp_start = -20
temp_stop = 100
temp_step = 20

temp_points = int((temp_stop - temp_start) / temp_step)+1

stage_var = [int(ninv)-1]
header_var = [int(nhead)]
##### sweep temperature calculation
temp_var=[]
for i in range(0, temp_points+1):
   temp_var.append(temp_start + i*temp_step)

##### template file loading
# r_file = open(simDir+'/ModelSimFile/tempsense_'+args.platform+'.sp', "r")
# lines = r_file.readlines()
# file_name = designName+'.sp'

r_file = open(simDir+'/spice/'+designName+'.sp', "r")
lines = r_file.readlines()
file_name = designName+'.sp'


##### hspice input file generation with stage and header
for i in range(0, len(stage_var)):
   for j in range(0, len(header_var)):
      os.mkdir(genDir + "./%s/inv%d_header%d"%(simDir+'/run/', stage_var[i], header_var[j]))
      for t in range(0, len(temp_var)):
         w_file0 = open(genDir + "./%s/inv%d_header%d/%s_%d.sp"%(simDir+'/run/', stage_var[i], header_var[j], designName, temp_var[t]), "w")
         for line in lines:
            if line[0:2] == '@@':
               nline = line[3:len(line)]
               clist = list(nline)
               for ci in range(0, len(clist)):
                  if clist[ci] == '@':
                     w_file0.write('%e'%(temp_var[t]))
                  elif clist[ci] == '$':
                     w_file0.write('%s'%(simDir+'/run/'))
                  else:
                     w_file0.write(clist[ci])
            else:
               w_file0.write(line)
      w_file1 = open(genDir + "./%s/inv%d_header%d/run_sim"%(simDir+'/run/',stage_var[i], header_var[j]), "w") ##run_simgeneration
      for k in range(0, len(temp_var)):
         dataspice = "hspice  %s_%d.sp >log &\n"%(designName, temp_var[k])
      #   dataspice = "finesim -spice -np 8 %s_%d.sp -o %s_%d >log &\n"%(designName, temp_var[k], designName, temp_var[k])
      #  data = "hspice %s_%e.sp >log &\n"%(file_name, temp_var[k])
         w_file1.write(dataspice)
      w_file2 = open(genDir + "./%s/inv%d_header%d/cal_result"%(simDir+'/run/', stage_var[i], header_var[j]), "w")
      for m in range(0, len(temp_var)-1):

         dataspice = "python result.py %s_%d.mt0 >>code_result\n"%(designName, temp_var[m])
         w_file2.write(dataspice)
      com = "python result_error.py >> code_result_with_error\n"
      w_file2.write(com)
      w_file3 = open(genDir + "./%s/inv%s_header%s/mt0_list"%(simDir+'/run/', stage_var[i], header_var[j]), "w")

      for l in range(0, len(temp_var)-1):
         print("%s    %s"%(temp_var[l],l))
         dataspice = "%s_%d.mt0\n"%(designName, temp_var[l])
         w_file3.write(dataspice)
      shutil.copy2(genDir + "./tools/result.py", '%s/inv%d_header%d'%(simDir+'/run/',stage_var[i], header_var[j]))
      shutil.copy2(genDir + "./tools/result_error.py", '%s/inv%d_header%d'%(simDir+'/run/',stage_var[i], header_var[j]))



folders = os.listdir("%s"%(simDir+'/run/'))

current = os.getcwd()
for folder in folders:
   print(folder)
   print(current)
   print(current)

   os.chdir("%s/%s/%s"%(current,simDir+'/run',folder))
   for k in range(0, len(temp_var)-1):
      sp.call(['hspice', '-mp', '12', '-mt', '32', '-hpp', '-i', designName+'_'+str(temp_var[k])+'.sp', '>','log'+str(temp_var[k])])
      #sp.call(['finesim', '-spice', '-np', '8', designName+'_'+str(temp_var[k])+'.sp', '-o', designName+'_'+str(temp_var[k])])
      #sp.call(['source', 'run_sim'])
      p.wait()
      sp.call(['python', 'result.py', designName+'_'+str(temp_var[k])+'.mt0'])
      #sp.call(['source', 'cal_result'])


#sp.call(['python', 'result_error.py'])
#os.system('python result_error.py')


#sp.call(['python', 'result_error.py', 'mt0_list'])

w_file3.close()


cwd1=os.getcwd()
print(cwd1)

#with open(cwd1+'/mt0_list', 'r') as r_mt0_list:
#   r_mt0_list.read()

r_mt0_list = open("./mt0_list", "r")
print(r_mt0_list)

#print(r_mt0_list.read())
#r_mt0_list = open('/mt0_list', 'r')
#r_mt0_list.read()

##### open mt0 file
#r_mt0_list.read(w_file3)
#mt0_lines=r_mt0.readlines()


##### read mt0_list, remove \n
#r_mt0_list = open(genDir + "./mt0_list", "r")
mt0_files = r_mt0_list.readlines()
new_list = list()
for line in mt0_files:
   stripped = line.strip()
   new_list.append(stripped)

mt0_files = new_list
##### get data from mt0_files with column number of 'data_col'
##### generate list with result data [[temp_var0], [temp_var1], [temp_var2], ...]
data0 = list()
data_temp = list()
for mt0_line in mt0_files:
   print(mt0_line)
   print("%s",cwd1)
   r_file = open(cwd1+"/%s"%(mt0_line))
   mt0_data = r_file.readlines()
   data_col = 1
   data_temp.append(mt0_data[4].split())
for line in data_temp:
   data0.append(line[0])



#
#print(data0)
#### calculate T X freq
data1 = list()

i=0
data_temp = list()
for val in data0:
   if val == 'failed':
      val_cal = 'failed'
   else:
      #print(val_cal)
      print(val)
      val_cal = math.log(1/float(val))*((-20+i*20)+273.15)*0.01
   data1.append(val_cal)
   print("postif")
   i=i+1

#
#
#
##### slope correction & row<->col switch
data2 = list()



print("%s    "%(data1))

data_temp0 = list()
slope_f = 80/(data1[len(data1)-2]-data1[1])
#print(slope_f)
data_temp1 = list()
for k in data1:
   if k == 'failed':
      val = 'failed'
      data2.append(val)
   else:
      val = k * slope_f
      data2.append(val)


#### offset correction
data3 = list()

for val in data2:
   offset = data2[1]
   if val == 'failed':
      val = 'failed'
   else:
      val = val - offset
#  data_temp = list()
#  for val in line:
   data3.append(val)
#  data3.append(data_temp)

##### temperature error calculation
data4 = list()
i=0
for val in data3:
   if val == 'failed':
      val = 'failed'
   else:
      val=(-20+i*20)-val
   data4.append(val)
   i=i+1
#print(data4)


r_result_list = open("./code_result", "r")
result_lines= r_result_list.readlines()
result_list = list()
result_tmep = list()
i=0
print(os.getcwd())
print('Temp  Frequency Power Error ')
for line in result_lines:
   result_list = result_lines[i].split()
   print('%s %s %s %s'%(result_list[0], result_list[1], result_list[2], data4[i]), file=open("all_result", "a"))
   i=i+1

print('# Temperature Sensor - Hspice Sim Completed')


#------------------------------------------------------------------------------
# Parse the Sim Results
#------------------------------------------------------------------------------

r_results_list = open("./all_result", "r")
results_lines=r_results_list.readlines()
new_list = list()
new_list_a = list()
new_list_i = list()

for line in results_lines:
   stripped = line.strip()
   new_list.append(stripped)

results_lines= new_list

for line in results_lines:
   r_array=line.split()
   new_list_a.append(r_array)

results_lines=np.array(new_list_a)

error=abs(np.asfarray(np.array(results_lines[:,3]),float))
power=np.asfarray(np.array(results_lines[:,2]),float)

index_e, value_e = max(enumerate(error), key=operator.itemgetter(1))
index_p, value_p = max(enumerate(power), key=operator.itemgetter(1))


print(results_lines[:,1])

print(value_p,index_p)

print(value_e,index_e)


os.chdir('../../../')



print('Parsing the Sim Results')

if os.path.isdir(args.outputDir):
   for file in os.listdir(args.outputDir):
      os.remove(args.outputDir + '/' + file)
else:
   try:
      os.mkdir(args.outputDir)
   except OSError:
      print('Unable to create the output directory')

cwd1=os.getcwd()
print(cwd1)

print(flowDir)
print(genDir)

#shutil.copytree(flow + '/export', args.outputDir)
p = sp.Popen(['cp', './flow/export/'+designName+'.gds.gz', \
        '../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.gds.gz'])
p.wait()
p = sp.Popen(['cp', './flow/export/'+designName+'.lef', \
        '../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.lef'])
p.wait()
p = sp.Popen(['cp', './flow/export/'+designName+'_min.lib', \
         '../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.lib'])
p.wait()
p = sp.Popen(['cp', './flow/export/'+designName+'_min.db', \
          '../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.db'])
p.wait()
p = sp.Popen(['cp', './flow/export/'+designName+'.lvs.v', \
          '../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.v'])
p.wait()
p = sp.Popen(['cp', 'extraction/sch/'+designName+'.spi', \
          '../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.spi'])
p.wait()

jsonSpec['results'] = {'platform': args.platform}
jsonSpec['results'].update({'area': designArea})
jsonSpec['results'].update({'error': value_e})
jsonSpec['results'].update({'power': value_p})

with open(args.outputDir + '/' + designName + '.json', 'w') as resultSpecfile:
   json.dump(jsonSpec, resultSpecfile, indent=True)

p = sp.Popen(['cp', args.outputDir+'/'+designName+'.json', \
          '../../../generators/temp-sense-gen/' + args.outputDir+'/'+designName+'.json'])

print('Generator completed successfully ! \n')




