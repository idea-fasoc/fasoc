#!/usr/bin/env python3

#------------------------------------------------------------------------------
# LDO MODEL WRAPPER
# IDEA & POSH
# Date: 12/21/2018
#------------------------------------------------------------------------------
import sys
import getopt
import math
import subprocess as sp
import fileinput
import re
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import glob

#------------------------------------------------------------------------------
# Get the folder/file paths
#------------------------------------------------------------------------------
genDir           = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")
head_tail_0      = os.path.split(os.path.abspath(genDir))
head_tail_1      = os.path.split(head_tail_0[0])
pvtGenDir        = os.path.relpath(os.path.join(genDir, '../../', 'private', head_tail_1[1], head_tail_0[1]))
flowDir          = os.path.join(pvtGenDir, './flow')
extDir           = os.path.join(pvtGenDir, './extraction')
simDir           = os.path.join(pvtGenDir, './simulation')
pyModulesDir     = os.path.join(pvtGenDir, './pymodules')

#------------------------------------------------------------------------------
# Parse the command line arguments
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Parsing command line arguments...')
print('#---------------------------------------------------------------------')
print(sys.argv)

parser = argparse.ArgumentParser(description='Digital LDO model generator')
parser.add_argument('--platform', required=True,
                    help='PDK/process kit for cadre flow (.e.g tsmc16)')
parser.add_argument('--clean', action='store_true',
                    help='To clean the workspace.')
args = parser.parse_args()

if args.platform != 'tsmc65lp' and args.platform != 'gfbicmos8hp':
   print('Error: Only supports TSMC65lp and GFBiCmos8hp kits as of now.')
   sys.exit(1)

if not os.path.isdir(pvtGenDir):   
   print('Error: Private directory does not exist. \n       ' + \
         'Model generation is only supported in \'macro\' and \'full\' modes.')
   sys.exit(1)
else:
   sys.path.append(pyModulesDir)
   import clean_up          as clc
   import cfg_digital_flow  as cfg
   import run_digital_flow  as rdf
   import run_pex_flow      as pex
   import run_sim_flow      as sim

# Load json config file
print('Loading platform_config file...')
try:
   with open(genDir + '../../config/platform_config.json') as file:
      jsonConfig = json.load(file)
except ValueError as e:
   print('Error: platform_config.json file has an invalid format. %s' % str(e))
   sys.exit(1)

# Define the config & design variables
mFile = ''
simTool = ''
extTool = ''
netlistTool = ''
calibreRulesDir = ''

# Define the internal variables used
ptCell = 'PT_UNIT_CELL'

# Get the config variable from platfom config file
simTool = jsonConfig['simTool']
if simTool != 'hspice' and simTool != 'finesim':
   print('Error: Supported simulators are \'hspice\' or \'finesim\' as of now')
   sys.exit(1)

extTool = jsonConfig['extractionTool']
if extTool != 'calibre':
   print('Error: Only support calibre extraction now')
   sys.exit(1)

netlistTool = jsonConfig['netlistTool']
if netlistTool != 'calibredrv':
   print('Error: Only support calibredrv netlist tool now')
   sys.exit(1)

try:
   platformConfig = jsonConfig['platforms'][args.platform]
except KeyError as e:
   print('Error: \"' + args.platform + '\" config not available')
   sys.exit(1)

mFile = platformConfig['model_lib'] + '/ldo.model'

calibreRulesDir = platformConfig['calibreRules']

print('Run Config:')
print('Aux Lib - \"' + platformConfig['aux_lib'] + '\"')
print('PT Cell Used - \"' + ptCell + '\"')
print('Model File - \"' + mFile + '\"')
print('Netlisting Tool - \"' + netlistTool + '\"')
print('Extraction Tool - \"' + extTool + '\"')
print('Simulation Tool - \"' + simTool + '\"')
print('Calibre Rules Directory - \"' + calibreRulesDir + '\"')
print('Digital Flow Directory - \"' + flowDir + '\"')
print('Extraction Directory - \"' + extDir  + '\"')
print('Simulation Directory - \"' + simDir  + '\"')

#------------------------------------------------------------------------------
# Clean the workspace
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Cleaning the workspace...')
print('#---------------------------------------------------------------------')
clc.wrkspace_clean(flowDir, extDir, simDir)
if (args.clean):
   print('Workspace clean done. Exiting the flow.')
   sys.exit(0)

try:
   os.mkdir(flowDir + '/src')
except OSError:
   print('Unable to create the "src" directory in "flow" folder')

try:
   os.mkdir(extDir + '/layout')
except OSError:
   print('Unable to create the "layout" directory in "extraction" folder')

try:
   os.mkdir(extDir + '/run')
except OSError:
   print('Unable to create the "run" directory in "extraction" folder')

try:
   os.mkdir(extDir + '/sch')
except OSError:
   print('Unable to create the "sch" directory in "extraction" folder')

try:
   os.mkdir(simDir + '/run')
except OSError:
   print('Unable to create the "run" directory in "simulation" folder')

#------------------------------------------------------------------------------
# Configure Synth and APR scripts
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Configuring Synth and APR scripts...')
print('#---------------------------------------------------------------------')
cfg.ldo_model_dg_flow_cfg(args.platform, platformConfig['aux_lib'], flowDir)

#------------------------------------------------------------------------------
# Initialize the local variables
#------------------------------------------------------------------------------
results = []
numIter = 0
for arrSize in [2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, \
                100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]:
   print('#---------------------------------------------------------------' + \
         '------')
   print('# Running the sim loop for array size = %s...' % arrSize)
   print('#---------------------------------------------------------------' + \
         '------')
   #---------------------------------------------------------------------------
   # Change the design name & Generate the Behavioral Verilog
   #---------------------------------------------------------------------------
   # Get the design name
   designName = 'LDO_' + str(arrSize)

   # Generate behavioral verilog of the testbench
   print('# Array Size %s - Generating the Behavioral Verilog...' % arrSize)
   p = sp.Popen(['python',genDir+'./tools/ldo_model_verilog_gen.py','-a', \
                 ptCell,str(arrSize)])
   p.wait()
   print('# Array Size %s - Behavioral Verilog Generated' % arrSize)

   #---------------------------------------------------------------------------
   # Update design name & source file list in the digital flow directory
   #---------------------------------------------------------------------------
   # Update the design name
   with open(flowDir + '/include.mk', 'r') as file:
      filedata = file.read()
   filedata = re.sub(r'export DESIGN_NAME :=.*', r'export DESIGN_NAME := ' + \
                     designName, filedata)
   with open(flowDir + '/include.mk', 'w') as file:
      file.write(filedata)

   # Update the verilog file list for Synthesis
   with open(flowDir + '/scripts/dc/dc.filelist.tcl', 'r') as file:
      filedata = file.read()
   filedata = re.sub(r'append MAIN_SOURCE_FILE.*', r'append ' + \
                     'MAIN_SOURCE_FILE \"' + designName + '.v\"', filedata)
   with open(flowDir + '/scripts/dc/dc.filelist.tcl', 'w') as file:
      file.write(filedata)

   #---------------------------------------------------------------------------
   # Run Synthesis and APR
   #---------------------------------------------------------------------------
   print('# Array Size %s - Running Synthesis and APR...' % arrSize)
   designArea = rdf.run_synth_n_apr(args.platform, designName, flowDir)
   print('# Array Size %s - Synthesis and APR finished' % arrSize)

   #---------------------------------------------------------------------------
   # Generate post PEX netlist
   #---------------------------------------------------------------------------
   print('# Array Size %s - Generating post PEX netist...' % arrSize)
   pex.gen_post_pex_netlist(args.platform, designName, flowDir, extDir, \
                            calibreRulesDir)
   print('# Array Size %s - Post PEX netlist Generated' % arrSize)

   #---------------------------------------------------------------------------
   # Run Hspice Sims
   #---------------------------------------------------------------------------
   print('# Array Size %s - Running Hspice Sims...' % arrSize)
   sim.run_post_pex_model_imax_worst(args.platform, \
                                     platformConfig['hspiceModels'], \
                                     designName, extDir, simDir, \
                                     simTool, arrSize)
   print('# Array Size %s - Hspice Sim Completed' % arrSize)

   #---------------------------------------------------------------------------
   # Parse the Sim Results
   #---------------------------------------------------------------------------
   print('# Array Size %s - Parsing the Sim Results...' % arrSize)
   simResult = open(simDir+'/run/'+designName+'.mt0', 'r')
   numSkipLines = 3
   numLine = 1
   numDataLine = 0
   for line in simResult.readlines():
      if (numLine > numSkipLines):
         if ((numLine % 2) == 1) or (simTool == 'finesim'):
            words = line.split()
            if numIter == 0:
               results.append([float(words[1])])
            results[numDataLine].append([int(arrSize), float(words[2])])
            numDataLine = numDataLine + 1
      numLine = numLine + 1
   simResult.close()
   numIter = numIter + 1
   results.sort(key=lambda x: x[0])
   print('# Array Size %s - Sim Results Parsed' % arrSize)

#------------------------------------------------------------------------------
# Generate the Model File
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Generating the Model File...')
print('#---------------------------------------------------------------------')
model = []
labels = []
f = open(mFile, 'w')
for i in range(len(results)):
   model.append([results[i][0]])
   f.write('%s: ' % str(results[i][0]))
   x = [item[1] for item in results[i][1:]]
   y = [item[0] for item in results[i][1:]]
   xt = [float(1000000)*item for item in x]
   plt.semilogx(y, xt)
   labels.append('Vin = %s' % results[i][0])
   z = np.polyfit(x,y,8)
   model[i].extend(z)
   for item in z:
      f.write('\t%s' % item)
   f.write('\n')
f.close()

plt.xlim(results[0][1][0], results[0][numIter][0])
plt.legend(labels, loc='upper left')
plt.xlabel('No. of unit cells in parallel')
plt.ylabel('Id (uA)')
plt.title('Id vs Array size')
#plt.show()

#------------------------------------------------------------------------------
# Print the Finish message
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('Script Finished - Model File saved as \"' + mFile +'\"')
print('#---------------------------------------------------------------------')
