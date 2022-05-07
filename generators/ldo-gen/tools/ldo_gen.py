#!/usr/bin/env python3

#------------------------------------------------------------------------------
# LDO GEN WRAPPER
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
supportedInputs  = os.path.join(genDir, './tools/supported_inputs.json')

#------------------------------------------------------------------------------
# Parse the command line arguments
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Parsing command line arguments...')
print('#---------------------------------------------------------------------')
print(sys.argv)

parser = argparse.ArgumentParser(description='Digital LDO design generator')
parser.add_argument('--specfile', required=True,
                    help='File containing the specification for the generator')
parser.add_argument('--outputDir', required=True,
                    help='Output directory for generator results')
parser.add_argument('--platform', required=True,
                    help='PDK/process kit for cadre flow (.e.g tsmc16)')
parser.add_argument('--mode', default='verilog',
                    choices=['verilog', 'macro', 'full'],
                    help='LDO Gen operation mode. Default mode: \'verilog\'.')
parser.add_argument('--gf12lpTrack', default='10P5T',
                    choices=['10P5T', '9T'],
                    help='Standard cell height for 12LP. Default: \'10P5T\'.')
parser.add_argument('--clean', action='store_true',
                    help='Clean the workspace.')
parser.add_argument('--useDefaultModel', action='store_true',
                    help='Uses the model from ldo-gen/models directory.')
args = parser.parse_args()

if not os.path.isfile(args.specfile):
   print('Error: specfile does not exist')
   print('File Path: ' + args.specfile)
   sys.exit(1)

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
   import run_sim_flow      as sim

# Load json supported inputs file
print('Loading supportedInputsFile...')
try:
   with open(supportedInputs) as file:
      jsonSupportedInputs = json.load(file)
except ValueError as e:
   print('Error: Supported Inputs json file has an invalid format. %s' % str(e))
   sys.exit(1)

try:
   supportedSpecs = jsonSupportedInputs['platforms'][args.platform]
except KeyError as e: 
   print('Error: \'' + args.platform + '\' tech is missing from supported platforms.')
   sys.exit(1)

try:
   vin_max = float(supportedSpecs['vin']['max'])
except KeyError as e:
   print('Error: Bad Supported Inputs file. \'vin[max]\' value is missing.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'vin[max]\'.')
   sys.exit(1)

try:
   vin_min = float(supportedSpecs['vin']['min'])
except KeyError as e:
   print('Error: Bad Supported Inputs file. \'vin[min]\' value is missing.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'vin[min]\'.')
   sys.exit(1)

try:
   dropout_max = float(supportedSpecs['dropout']['max'])
except KeyError as e:
   print('Error: Bad Supported Inputs file. \'dropout[max]\' value is missing.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'dropout[max]\'.')
   sys.exit(1)

try:
   dropout_min = float(supportedSpecs['dropout']['min'])
except KeyError as e:
   print('Error: Bad Supported Inputs file. \'dropout[min]\' value is missing.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'dropout[min]\'.')
   sys.exit(1)

try:
   maxLoad_max = float(supportedSpecs['maxLoad']['max'])
except KeyError as e:
   print('Error: Bad Supported Inputs file. \'maxLoad[max]\' value is missing.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'maxLoad[max]\'.')
   sys.exit(1)

try:
   maxLoad_min = float(supportedSpecs['maxLoad']['min'])
except KeyError as e:
   print('Error: Bad Supported Inputs file. \'maxLoad[min]\' value is missing.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'maxLoad[min]\'.')
   sys.exit(1)

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
if jsonSpec['generator'] != 'ldo-gen':
   print('Error: Generator specification must be \"ldo-gen\".')
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
imax = ''
vin = ''

# Get the config variable from platfom config file
if args.mode != 'verilog':
   synthTool = jsonConfig['synthTool']
   if synthTool != 'dc' and synthTool != 'genus':
      print('Error: Supported synthesis tools are \'dc\' or \'genus\' ' + \
            'as of now')
      sys.exit(1)

   simTool = jsonConfig['simTool']
   if simTool != 'hspice' and simTool != 'finesim':
      print('Error: Supported simulators are \'hspice\' or \'finesim\' ' + \
            'as of now')
      sys.exit(1)

   if args.mode == 'full':
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

mFile = platformConfig['model_lib'] + '/ldoModel.json'
if args.platform == 'gf12lp' and args.gf12lpTrack == '9T':
   mFilePublic = genDir + '/models/' + args.platform + '_9T_model.json'
else:
   mFilePublic = genDir + '/models/' + args.platform + '_model.json'

if (args.useDefaultModel):
   mFile = mFilePublic
   print('\"useDefaultModel\" is enabled. ' + \
         'Using the model file provided in the repo.')
   
if args.mode == 'full':
   calibreRulesDir = platformConfig['calibreRules']

# Get the design spec & parameters from spec file
try:
   designName = jsonSpec['module_name']
except KeyError as e:
   print('Error: Bad Input Specfile. \'module_name\' variable is missing.')
   sys.exit(1)

try:
   vin = float(jsonSpec['specifications']['vin'])
except KeyError as e:
   print('Error: Bad Input Specfile. \'vin\' value is missing under ' + \
         '\'specifications\'.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'vin\' '+ \
         'under \'specifications\'.')
   sys.exit(1)
if vin > vin_max or vin < vin_min:
   print('Error: Only support vin from ' + str(vin_min) + ' to ' + \
          str(vin_max) + ' with increments of 0.1V now')
   sys.exit(1)

try:
   dropout = float(jsonSpec['specifications']['dropout'])
except KeyError as e:
   print('Error: Bad Input Specfile. \'dropout\' value is missing under ' + \
         '\'specifications\'.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'dropout\' '+ \
         'under \'specifications\'.')
   sys.exit(1)
if dropout > dropout_max or dropout < dropout_min:
   print('Error: Only support dropout from ' + str(dropout_min) + ' to ' + \
          str(dropout_max) + ' with increments of 50mV now')
   sys.exit(1)

try:
   imax = float(jsonSpec['specifications']['imax'])
except KeyError as e:
   print('Error: Bad Input Specfile. \'imax\' value is missing under ' + \
         '\'specifications\'.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'imax\' '+ \
         'under \'specifications\'.')
maxLoad_max = maxLoad_max*dropout/0.05
maxLoad_min = maxLoad_min*dropout/0.05
if imax > maxLoad_max or imax < maxLoad_min:
   print('Error: Only support imax in the range [' + str(maxLoad_min) + ', ' + \
         str(maxLoad_max)+'] for dropout = '+str(dropout))
   sys.exit(1)

print('Run Config:')
print('Mode - \"' + args.mode + '\"')
print('Model File - \"' + mFile + '\"')
if args.mode != 'verilog':
   print('Aux Lib - \"' + platformConfig['aux_lib'] + '\"')
   print('Digital Flow Directory - \"' + flowDir + '\"')
   print('Simulation Tool - \"' + simTool + '\"')
   print('Simulation Directory - \"' + simDir  + '\"')
   if args.mode == 'full':
      print('Netlisting Tool - \"' + netlistTool + '\"')
      print('Extraction Tool - \"' + extTool + '\"')
      print('Calibre Rules Directory - \"' + calibreRulesDir + '\"')
      print('Extraction Directory - \"' + extDir  + '\"')
print('LDO Instance Name - \"' + designName + '\"')

# Define the output variables
designArea = 0
iMaxOut    = imax 

#------------------------------------------------------------------------------
# Clean the workspace
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Cleaning the workspace...')
print('#---------------------------------------------------------------------')
if os.path.isdir(args.outputDir):
   shutil.rmtree(args.outputDir, ignore_errors=True)

if args.mode != 'verilog':
   clc.wrkspace_clean(flowDir, extDir, simDir)
   if (args.clean):
     print('Workspace clean done. Exiting the flow.')
     sys.exit(0)
   
   try:
      os.mkdir(flowDir + '/src')
   except OSError:
      print('Unable to create the "src" directory in "flow" folder')
      sys.exit(1)
   
   try:
      os.mkdir(simDir + '/run')
   except OSError:
      print('Unable to create the "run" directory in "simulation" folder')
      sys.exit(1)

   if args.mode == 'full':
      try:
         os.mkdir(extDir + '/layout')
      except OSError:
         print('Unable to create the "layout" directory in "extraction" folder')
         sys.exit(1)
      
      try:
         os.mkdir(extDir + '/run')
      except OSError:
         print('Unable to create the "run" directory in "extraction" folder')
         sys.exit(1)
      
      try:
         os.mkdir(extDir + '/sch')
      except OSError:
         print('Unable to create the "sch" directory in "extraction" folder')
         sys.exit(1)
else: 
   if (args.clean):
      print('Workspace clean done. Exiting the flow.')
      sys.exit(0)

try:
   os.mkdir(args.outputDir)
except OSError:
   print('Unable to create the output directory')
   sys.exit(1)

#------------------------------------------------------------------------------
# Get the Power Transistor array size
#------------------------------------------------------------------------------
print('#---------------------------------------------------------------------')
print('# Getting the Power Transistor array Size')
print('#---------------------------------------------------------------------')
if not os.path.isfile(mFile):
   if args.mode == 'verilog':
      print('Model file \'' + mFile + '\' is not valid. ' + \
            'Using the model file provided in the repo.')
      mFile = mFilePublic
   else:
      p = sp.Popen(['python',genDir+'./tools/ldo_model.py','--platform', \
                   args.platform,'--gf12lpTrack',args.gf12lpTrack])
      p.wait()

try:
   f = open(mFile, 'r')
except ValueError as e:
   print('Model file creation failed')
   sys.exit(1)
f.close()

try:
   with open(mFile, 'r') as file:
      jsonModel = json.load(file)
except ValueError as e:
   print('Error: ldoModel.json file has an invalid format. %s' % str(e))
   sys.exit(1)

N = 0
imax_t = 1.3*imax
coefLength = len(jsonModel['Iload,max'][str(dropout)][str(vin)])
for i in range(coefLength):
   z = jsonModel['Iload,max'][str(dropout)][str(vin)][i]
   N = N + (float(z)*pow(imax_t, (coefLength-i-1)))
N = int(math.ceil(N))
arrSize = N
print('# LDO - Power Transistor array Size = ' + str(arrSize))

# Get the estimate of the area
coefLength = len(jsonModel['area'])
for i in range(coefLength):
   z = jsonModel['area'][i]
   designArea = designArea + (float(z)*pow(arrSize, (coefLength-i-1)))
print('# LDO - Design Area Estimate = ' + str(designArea))

#------------------------------------------------------------------------------
# Generate the Behavioral Verilog
#------------------------------------------------------------------------------
with open(verilogDir + '/LDO_TEMPLATE.v', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'parameter integer ARRSZ = \d+;', \
		  r'parameter integer ARRSZ = ' + str(arrSize) + ';', filedata)
filedata = re.sub(r'module \S+', r'module ' + designName + '(', filedata)
if args.mode == 'verilog':
  with open(args.outputDir + '/' + designName + '.v', 'w') as file:
     file.write(filedata)
else:
  with open(flowDir + '/src/' + designName + '.v', 'w') as file:
     file.write(filedata)

# Get ctrl word initialization in hex
ctrlWordHexCntF = int(math.floor(arrSize/4.0))
ctrlWordHexCntR = int(arrSize % 4.0)
ctrlWordHex = ['h']
ctrlWordHex.append(str(hex(pow(2,ctrlWordHexCntR)-1)[2:]))
for i in range(ctrlWordHexCntF):
   ctrlWordHex.append('f')
ctrlWdRst = str(arrSize) + '\'' + ''.join(ctrlWordHex)

with open(verilogDir + '/LDO_CONTROLLER_TEMPLATE.v', 'r') as file:
   filedata = file.read()
filedata = re.sub(r'parameter integer ARRSZ = \d+;', \
		  r'parameter integer ARRSZ = ' + str(arrSize) + ';', filedata)
filedata = re.sub(r'wire \[ARRSZ-1:0\] ctrl_rst = \S+', r'wire ' + \
                  '[ARRSZ-1:0] ctrl_rst = ' + ctrlWdRst + ';', filedata)
if args.mode == 'verilog':
   with open(args.outputDir + '/LDO_CONTROLLER.v', 'w') as file:
      file.write(filedata)
else:
   with open(flowDir + '/src/LDO_CONTROLLER.v', 'w') as file:
      file.write(filedata)

print('# LDO - Behavioural Verilog Generated')

if args.mode != 'verilog':
   #---------------------------------------------------------------------------
   # Configure Synth and APR scripts
   #---------------------------------------------------------------------------
   print('#------------------------------------------------------------------')
   print('# Configuring Synth and APR scripts...')
   print('#------------------------------------------------------------------')
   cfg.ldo_gen_dg_flow_cfg(args.platform, vin, platformConfig['aux_lib'], \
                           designName, flowDir, synthTool)

   #---------------------------------------------------------------------------
   # Run Synthesis and APR
   #---------------------------------------------------------------------------
   designArea = rdf.run_synth_n_apr(args.platform, designName, flowDir, \
                                    args.gf12lpTrack, synthTool)
   print('# LDO - Synthesis and APR finished')

if args.mode == 'full':
   #---------------------------------------------------------------------------
   # Generate post PEX netlist
   #---------------------------------------------------------------------------
   pex.gen_post_pex_netlist(args.platform, designName, flowDir, extDir, \
                            calibreRulesDir)
   print('# LDO - Post PEX netlist Generated')
   
   #---------------------------------------------------------------------------
   # Run Hspice Sims
   #---------------------------------------------------------------------------
   iMaxOut = sim.run_post_pex_ldo_imax_worst(args.platform, \
                                             platformConfig['hspiceModels'], \
                                             designName, extDir, simDir, \
                                             simTool, vin, imax, dropout)
   print('# LDO - Hspice Sim Completed')

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

jsonSpec['results'] = {'platform': args.platform}
jsonSpec['results'].update({'area': designArea})
jsonSpec['results'].update({'aspect_ratio': "1:1"})
jsonSpec['results'].update({'power': 0.0009})
jsonSpec['results'].update({'vin': vin})
jsonSpec['results'].update({'imax': iMaxOut})

with open(args.outputDir + '/' + designName + '.json', 'w') as resultSpecfile:
   json.dump(jsonSpec, resultSpecfile, indent=True)

print('Generator completed successfully ! \n')
