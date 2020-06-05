#!/usr/bin/env python3.7
#------------------------------------------------------------------------------
# ADC GEN WRAPPER
# IDEA & POSH Integration Excercises
# Date: 06/05/2019
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
import ADC_netlist
import readparamgen
import os
import time
from readparamgen import check_search_done, platformConfig, designName, args, jsonSpec, main
#from subprocess import call
#------------------------------------------------------------------------------
# Clean the workspace
#------------------------------------------------------------------------------
print('#----------------------------------------------------------------------')
print('# Cleaning the workspace...')
print('#----------------------------------------------------------------------')
#p = sp.Popen(['make','bleach_all'], cwd=flowDir)
#p.wait()
#Future: need to remove this after comparator aux cell is characterized
#for file in os.listdir(flowDir + '/src/'):
#   os.remove(flowDir + '/src/' + file)
# Define the internal variables used
genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

head_tail_0 = os.path.split(os.path.abspath(genDir))
head_tail_1 = os.path.split(head_tail_0[0])
privateGenDir = os.path.relpath(os.path.join(genDir, '../../', 'private', head_tail_1[1], head_tail_0[1]))
print(genDir)
print(privateGenDir)
#ptCell = 'PT_UNIT_CELL'

flowDir = os.path.join(privateGenDir , './flow')
extDir = genDir + '../../private/generators/adc-gen/extraction'
simDir = genDir + '../../private/generators/adc-gen/hspice'
srcDir = genDir + './src'


for file in os.listdir(simDir + '/'):
   if not os.path.isdir(simDir + '/' + file):
      os.remove(simDir + '/' + file)
if os.path.isdir(simDir + '/run'):
   shutil.rmtree(simDir + '/run', ignore_errors=True)
if os.path.isdir(extDir + '/run'):
   shutil.rmtree(extDir + '/run', ignore_errors=True)

#if (args.clean):
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


power_with_inx, fsampling, resolution, enob, area, nisw, ncsw = main()

print('Fsampling : ' , fsampling)
print('Resolution : ' , resolution)
print('ENOB : ' , enob)
print('Power : ' , power_with_inx)
print('Area : ' , area)
print('nisw : ' , nisw)
print('ncsw : ' , ncsw)

print('\n')
print('#----------------------------------------------------------------------')
print('# Verilog Generation')
print('#----------------------------------------------------------------------')


time.sleep(2) 


aux1 = 'SW_INPUT'
aux2 = 'SW_VCM'
aux3 = 'UNIT_CAP'
#aux4 = 'BUFX4RVT_ISOVDD'
#aux5 = 'HEADERX1RVT'
#aux6 = 'LC1P2TO3P6X1RVT_VDDX4'


###change

aLib1 = platformConfig['aux_lib'] + aux1 + '/latest/'
aLib2 = platformConfig['aux_lib'] + aux2 + '/latest/'
aLib3 = platformConfig['aux_lib'] + aux3 + '/latest/'

aLib = platformConfig['aux_lib']


calibreRulesDir = platformConfig['calibreRules']

ADC_netlist.gen_adc_netlist(resolution, nisw, ncsw, simDir, genDir)

print('#----------------------------------------------------------------------')
print('# Verilog Generated')
print('#----------------------------------------------------------------------')
designAreaVerilog= 1000
jsonSpec['results'] = {'platform': args.platform}
jsonSpec['results'].update({'area': designAreaVerilog})
jsonSpec['results'].update({'enob': enob})
jsonSpec['results'].update({'power': power_with_inx})

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

with open(flowDir + '/scripts/dc/constraints.tcl', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'#+set_dont_touch', r'set_dont_touch', filedata)
with open(flowDir + '/scripts/dc/constraints.tcl', 'w') as file:
   file.write(filedata)

flowPtExportDir = flowDir+"/blocks/PT_UNIT_CELL/export"
if not os.path.exists(flowPtExportDir):
  os.makedirs(flowPtExportDir)


shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.db',   flowPtExportDir + "/" + aux1 + '.db')
shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.db',   flowPtExportDir + "/" + aux2 + '.db')
shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.db',   flowPtExportDir + "/" + aux3 + '.db')

shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.lib',   flowPtExportDir + "/" + aux1 + '.lib')
shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.lib',   flowPtExportDir + "/" + aux2 + '.lib')
shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.lib',   flowPtExportDir + "/" + aux3 + '.lib')

shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.lef',   flowPtExportDir + "/" + aux1 + '.lef')
shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.lef',   flowPtExportDir + "/" + aux2 + '.lef')
shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.lef',   flowPtExportDir + "/" + aux3 + '.lef')

shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.cdl',   flowPtExportDir + "/" + aux1 + '.cdl')
shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.cdl',   flowPtExportDir + "/" + aux2 + '.cdl')
shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.cdl',   flowPtExportDir + "/" + aux3 + '.cdl')

shutil.copyfile(aLib + '/' + aux1 + '/latest/'  + aux1 + '.gds',   flowPtExportDir + "/" + aux1 + '.gds')
shutil.copyfile(aLib + '/' + aux2 + '/latest/'  + aux2 + '.gds',   flowPtExportDir + "/" + aux2 + '.gds')
shutil.copyfile(aLib + '/' + aux3 + '/latest/'  + aux3 + '.gds',   flowPtExportDir + "/" + aux3 + '.gds')

time.sleep(1)

print('#----------------------------------------------------------------------')
print('# Synthesis...')
print('#----------------------------------------------------------------------')
time.sleep(1)
print("Checking required files....")

# Run the Synthesis flow
p = sp.Popen(['make','synth'], cwd=flowDir)
p.wait()

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
#coreDim = 100
coreDim = math.ceil(math.sqrt(coreCellArea*2.3)/5)*5
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

time.sleep(2)

print()
if args.mode == 'macro':
  print("Exiting tool....")
  sys.exit(1)

time.sleep(2)






















#if args.mode == 'verilog':
#  print("Exiting tool....")
#  #sys.exit(1)
#  exit()
#
#
#if args.mode != 'verilog':
#  print("Only verilog mode is supported [other modes are in-progress]....")
#  sys.exit(1)
