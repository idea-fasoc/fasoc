#!/usr/bin/env python3

#------------------------------------------------------------------------------
# SCPA GEN WRAPPER
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
verilogDir       = os.path.join(genDir, './verilog')
#supportedInputs  = os.path.join(genDir, './tools/supported_inputs.json')

#------------------------------------------------------------------------------
# Parse the command line arguments
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Parsing command line arguments...')
print('#---------------------------------------------------------------------')
print(sys.argv)

parser = argparse.ArgumentParser(description='Digital SCPA design generator')
parser.add_argument('--specfile', required=True,
                    help='File containing the specification for the generator')
parser.add_argument('--outputDir', required=True,
                    help='Output directory for generator results')
parser.add_argument('--platform', required=True,
                    help='PDK/process kit for cadre flow (.e.g tsmc16)')
parser.add_argument('--mode', default='verilog',
                    choices=['verilog', 'macro', 'full', 'pex'],
                    help='LDO Gen operation mode. Default mode: \'verilog\'.')
parser.add_argument('--clean', action='store_true',
                    help='Clean the workspace.')
args = parser.parse_args()

#if not os.path.isfile(args.specfile):
#   print('Error: specfile does not exist')
#   print('File Path: ' + args.specfile)
#   sys.exit(1)

# Should change this condition to use supportedInputs file
if args.platform != 'tsmc65lp' and args.platform != 'gfbicmos8hp' and \
   args.platform != 'gf12lp':
   print('Error: Only supports TSMC65lp, GFBiCmos8hp and GF12LP kits ' + \
         'as of now.')
   sys.exit(1)

if args.mode != 'verilog':
   if not os.path.isdir(pvtGenDir):   
      print('Error. Private directory does not exist. ' + \
            'Please use only \'verilog\' mode.')
      sys.exit(1)

if os.path.isdir(pvtGenDir):   
   sys.path.append(pyModulesDir)
   import clean_up          as clc
   import cfg_digital_flow  as cfg
   import run_digital_flow  as rdf
   import run_pex_flow      as pex
#   import run_sim_flow      as sim

# Load json supported inputs file
# DELETE
# Load json input spec file
print('Loading specfile...')
try:
   with open(args.specfile) as file:
      jsonSpec = json.load(file)
except ValueError as e:
   print('Error: Input Spec json file has an invalid format. %s' % str(e))
   sys.exit(1)

try:
   generator = jsonSpec['generator']
except KeyError as e: 
   print('Error: Bad Input Specfile. \'generator\' variable is missing.')
   sys.exit(1)
if jsonSpec['generator'] != 'scpa-gen':
   print('Error: Generator specification must be \"scpa-gen\".')
   sys.exit(1)

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
mFilePublic = ''
simTool = ''
extTool = ''
netlistTool = ''
calibreRulesDir = ''
designName = ''
#imax = ''
#vin = ''


if args.mode == 'pex':
   #---------------------------------------------------------------------------
   # Generate post PEX netlist
   #---------------------------------------------------------------------------
   pex.gen_post_pex_netlist(args.platform, designName, flowDir, extDir, \
                            calibreRulesDir)
   print('# SCPA - Post PEX netlist Generated')
   
   #---------------------------------------------------------------------------
   # Run Hspice Sims
   #---------------------------------------------------------------------------
#   iMaxOut = sim.run_post_pex_ldo_imax_worst(args.platform, \
#                                             platformConfig['hspiceModels'], \
#                                             designName, extDir, simDir, \
#                                             simTool, vin, imax)
#   print('# LDO - Hspice Sim Completed')

#------------------------------------------------------------------------------
# Write the Outputs
#------------------------------------------------------------------------------
print('Writing the outputs')

if args.mode != 'verilog':
   if os.path.isdir(args.outputDir):
      for file in os.listdir(args.outputDir):
         os.remove(args.outputDir + '/' + file)

   p = sp.Popen(['cp', flowDir+'/export/'+designName+'.gds.gz', \
                 args.outputDir+'/'+designName+'.gds.gz'])
   p.wait()
   p = sp.Popen(['cp', flowDir+'/export/'+designName+'.lef', \
                 args.outputDir+'/'+designName+'.lef'])
   p.wait()
   for file in glob.glob(flowDir+'/export/'+designName+'_*.lib'):
      shutil.copy(file, args.outputDir+'/'+designName+'.lib')
   for file in glob.glob(flowDir+'/export/'+designName+'_*.db'):
      shutil.copy(file, args.outputDir+'/'+designName+'.db')
   p = sp.Popen(['cp', flowDir+'/export/'+designName+'.lvs.v', \
   	         args.outputDir+'/'+designName+'.v'])
   p.wait()
   for file in glob.glob(flowDir+'/results/calibre/lvs/_'+designName+'*.sp'):
      shutil.copy(file, args.outputDir+'/'+designName+'.spi')

#jsonSpec['results'] = {'platform': args.platform}
#jsonSpec['results'].update({'area': designArea})
#jsonSpec['results'].update({'aspect_ratio': "1:1"})
#jsonSpec['results'].update({'power': 0.0009})
#jsonSpec['results'].update({'vin': vin})
#jsonSpec['results'].update({'imax': iMaxOut})

#with open(args.outputDir + '/' + designName + '.json', 'w') as resultSpecfile:
#   json.dump(jsonSpec, resultSpecfile, indent=True)

print('Generator pex successfully ! \n')
