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

#ptCell = 'PT_UNIT_CELL'

flowDir = os.path.join(privateGenDir , './flow')
extDir = genDir + '../../private/generators/adc-gen/extraction'
simDir = genDir + '../../private/generators/adc-gen//hspice'
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

ADC_netlist.gen_adc_netlist(resolution, nisw, ncsw,srcDir,genDir)

print('#----------------------------------------------------------------------')
print('# Verilog Generated')
print('#----------------------------------------------------------------------')

time.sleep(2)
if args.mode == 'verilog':
  print("Exiting tool....")
  #sys.exit(1)
  exit()


if args.mode != 'verilog':
  print("Only verilog mode is supported [other modes are in-progress]....")
  sys.exit(1)
