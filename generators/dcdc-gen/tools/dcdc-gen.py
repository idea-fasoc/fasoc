#!/usr/bin/env python2.7
#======== Verilog wrapper ==========
import function
import SC_netlist
import os
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


import readparamgen
import os
import time

from readparamgen import check_search_done, platformConfig, designName, args


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

print(head_tail_0)
print(head_tail_1)
print(privateGenDir)
#while True:
# Define the internal variables used
#ptCell = 'PT_UNIT_CELL'
flowDir = os.path.join(privateGenDir , './flow')
extDir = genDir + '../../private/generators/dcdc-gen/extraction'
simDir = genDir + '../../private/generators/dcdc-gen/hspice'
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
#------------------------------------------------------------------------------
# Initialize the config variables
#------------------------------------------------------------------------------

print('#----------------------------------------------------------------------')
print('# Verilog Generation')
print('#----------------------------------------------------------------------')

CON, PD, ef, il, vo, hist = check_search_done()
print("Configuration:{0}".format(CON))



#print("stage:{0}".format(stage))

aux = 'SCX1RVT_2TO1'

##change
aLib = platformConfig['aux_lib'] + aux + '/latest/'
calibreRulesDir = platformConfig['calibreRules']

SC_netlist.gen_SC_netlist(CON, PD, aux,srcDir)

shutil.copyfile(genDir + '/src/SC_AUTO.nl.v',   genDir + '/src/' + designName + '.v')
with open(genDir + '/src/' + designName  + '.v', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'SC_AUTO*', r' ' + \
                  designName, filedata)
with open(flowDir + '/src/' + designName + '.v', 'w') as file:
   file.write(filedata)

print('#----------------------------------------------------------------------')
print('# Verilog Generated')
print('#----------------------------------------------------------------------')
#------------------------------------------------------------------------------
# Configure Synth and APR scripts
#------------------------------------------------------------------------------


time.sleep(2)
if args.mode == 'verilog':
  print("Exiting tool....")
  sys.exit(1)


if args.mode != 'verilog':
  print("Only verilog mode is supported [other modes are in-progress]....")
  sys.exit(1)

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


#shutil.copyfile(aLib + '/db/'  + aux + '_tt.db',   flowPtExportDir + "/" + aux + '_tt.db')
