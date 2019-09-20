#------------------------------------------------------------------------------
# TEMP-SENSE GEN WRAPPER
# IDEA & POSH Integration Excercises
# Date: 4/15/2018
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

#------------------------------------------------------------------------------
# Parse the command line arguments
#------------------------------------------------------------------------------
print("#----------------------------------------------------------------------")
print("# Parsing command line arguments...")
print("#----------------------------------------------------------------------")
print( sys.argv)

genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

parser = argparse.ArgumentParser(description='Temperature Sensor design generator')
parser.add_argument('--specfile', required=True,
                    help='File containing the specification for the generator')
parser.add_argument('--outputDir', required=True,
                    help='Output directory for generator results')
parser.add_argument('--platform', required=True,
                    help='PDK/process kit for cadre flow (.e.g tsmc16)')
args = parser.parse_args()

if not os.path.isfile(args.specfile):
  print("Error: specfile does not exist")
  print("File Path: ' + args.specfile")
  sys.exit(1)

if args.platform != 'tsmc65lp':
  print("Error: tsmc65lp is the only platform supported")
  sys.exit(1)

# Load json spec file
print("Loading specfile...")
try:
  with open(args.specfile) as file:
    jsonSpec = json.load(file)
except ValueError as e:
  print("Error occurred opening or loading json file.")
  print >> sys.stderr, 'Exception: %s' % str(e)
  sys.exit(1)

if jsonSpec['generator'] != 'temp-sense-gen':
  print("Error: Generator specification must be \"temp-sense-gen\".")

# Load json config file
print("Loading platform_config file...")
try:
  with open(genDir + '../../config/platform_config.json') as file:
    jsonConfig = json.load(file)
except ValueError as e:
  print("Error occurred opening or loading json file.")
  print >> sys.stderr, 'Exception: %s' % str(e)
  sys.exit(1)

# Define the config & design variables
aLib = ''
mFile = ''
simTool = ''
extTool = ''
netlistTool = ''
calibreRulesDir = ''
designName = ''


# Define the internal variables used
#ptCell = 'PT_UNIT_CELL'
flowDir = genDir + './flow'
extDir = genDir + './extraction'
simDir = genDir + './hspice'


aux1 = 'NAND2X1RVT_ISOVDD'
aux2 = 'INVX1RVT_ISOVDD'
aux3 = 'BUFX4RVT_ISOVDD'
aux4 = 'BUFX4RVT_ISOVDD'
aux5 = 'HEADERX1RVT'


# Get the config variable from platfom config file
simTool = jsonConfig['simTool']
if simTool != 'hspice':
   print("Error: Only support hspice simulator now")
   sys.exit(1)

extTool = jsonConfig['extractionTool']
if extTool != 'calibre':
   print("Error: Only support calibre extraction now")
   sys.exit(1)

netlistTool = jsonConfig['netlistTool']
if netlistTool != 'calibredrv':
   print("Error: Only support calibredrv netlist tool now")
   sys.exit(1)

calibreRulesDir = jsonConfig['calibreRules']

try:
   platformConfig = jsonConfig['platforms'][args.platform]
except ValueError as e:
   print("Error: \"' + args.platform + '\" config not available")
   sys.exit(1)


##change
aLib1 = platformConfig['aux_lib'] + '/' + aux1
aLib2 = platformConfig['aux_lib'] + '/' + aux2
aLib3 = platformConfig['aux_lib'] + '/' + aux3
aLib4 = platformConfig['aux_lib'] + '/' + aux4
aLib5 = platformConfig['aux_lib'] + '/' + aux5





mFile = platformConfig['model_lib'] + '/modelfile.csv'

# Get the design spec & parameters from spec file
designName = jsonSpec['instance_name']

Tmin = float(jsonSpec['specifications']['temperature']['min'])
Tmax = float(jsonSpec['specifications']['temperature']['max'])
if Tmax > 100 or Tmin < -20:
   print("Error: Supported temperature sensing must be inside the following range [-20 to 100] Celcius")
   sys.exit(1)

optimization = str(jsonSpec['specifications']['optimization'])
if optimization == '':
   print("Error: Please enter which optmization is desired [error or power]")
   sys.exit(1)

print("Run Config:")
print("Aux Lib - \"' + aLib + '\"")
print("PT Cell Used - \"' + ptCell + '\"")
print("Model File - \"' + mFile + '\"")
print("Netlisting Tool - \"' + netlistTool + '\"")
print("Extraction Tool - \"' + extTool + '\"")
print("Simulation Tool - \"' + simTool + '\"")
print("Calibre Rules Directory - \"' + calibreRulesDir + '\"")
print("Digital Flow Directory - \"' + flowDir + '\"")
print("Extraction Directory - \"' + extDir  + '\"")
print("Simulation Directory - \"' + simDir  + '\"")
print("LDO Instance Name - \"' + designName + '\"")