#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse  # arguement parsing
import sys  # exit function
import shutil  # filesystem manipulation
import os  # filesystem manipulation
import re  # regular expressiosn
import json  # json parsing
import subprocess  # process
import zipfile
import numpy as np
from subprocess import call
from collections import OrderedDict
import webbrowser as wb

from jsonXmlGenerator import jsonXmlGenerator
from rtlXmlGenerator import rtlXmlGenerator
from analogGen import analogGen
from closedLoop import closedLoop

# Parse and validate arguments
# ==============================================================================

soc_dir = os.path.dirname(__file__)
fasoc_dir  = os.path.relpath(os.path.join(soc_dir,"../.."))

parser = argparse.ArgumentParser(description='FASoC Integration Tool')
parser.add_argument('--design', required=True,
                    help='Resolved design description json file path')
parser.add_argument('--platform', default="tsmc65lp",
                    help='PDK/process kit for cadre flow (.e.g tsmc65lp)')
parser.add_argument('--fasoc_config', default=os.path.join(fasoc_dir, "config/fasoc_config.json"),
                    help='SoC tool configuration json file path')
parser.add_argument('--platform_config', default=os.path.join(fasoc_dir, "config/platform_config.json"),
                    help='Platform configuration json file path')
parser.add_argument('--mode', default="verilog",
                    help='Run Mode')
parser.add_argument('--database', default="add",
                    help='Add to database')
args = parser.parse_args()


if args.platform != "tsmc65lp":
  print("Error: tsmc65lp is the only platform supported")
  sys.exit(1)


# STEP 1: Load all user intent and all config files
# ==============================================================================

print("Loading design: ", args.design)
try:
  with open(args.design) as f:
    designJson = json.load(f)
except ValueError as e:
  print("Error occurred opening or loading design json file: ", args.design)
  print("Exception: ", str(e))
  sys.exit(1)

print("Loading FASoC Config: ", args.fasoc_config)
try:
  with open(args.fasoc_config) as f:
    configJson = json.load(f)
except ValueError as e:
  print("Error occurred opening or loading fasoc_config json file: ", args.fasoc_config)
  print("Exception: ", str(e))
  sys.exit(1)

print("Loading platform Config: ", args.platform_config)
try:
  with open(args.platform_config) as f:
    platformJson = json.load(f)
except ValueError as e:
  print("Error occurred opening or loading platform_config json file: ",
        args.platform_config)
  print("Exception: ", str(e))
  sys.exit(1)

design_dir = os.path.dirname(args.design)
databaseDir = platformJson["platforms"]["tsmc65lp"]["database"]
designName = designJson['design_name']
socrates_installDir = platformJson["socratesInstall"]
ipXactDir = os.path.join(design_dir,'ipxact')
rubiDir = os.path.join(soc_dir,'..','rubi')
jsnDir = os.path.join(design_dir,'json')

try:
  os.mkdir(ipXactDir)
  print("Directory " , ipXactDir ,  " Created ") 
except FileExistsError:
  print("Directory " , ipXactDir ,  " already exists")
  print("Cleaning ipxact directory ...")
  if len(os.listdir(ipXactDir)) != 0:
    for file in os.listdir(ipXactDir):
      os.remove(os.path.join(ipXactDir,file))

try:
  os.mkdir(jsnDir)
  print("Directory " , jsnDir ,  " Created ") 
except FileExistsError:
  print("Directory " , jsnDir ,  " already exists")
  print("Cleaning ipxact directory ...")
  if len(os.listdir(jsnDir)) != 0:
    for file in os.listdir(jsnDir):
      os.remove(os.path.join(jsnDir,file))

try:
  units = designJson["units"]
except KeyError:
  print("units is not mentioned in the design file")
  units = {}
# STEP 2: Run the design solver
# ==============================================================================

# TODO: Solver is not yet implemented. Assuming the input design json is
# completely solved


# STEP 3-5: For each module, generate if not cached (or in DB)
# ==============================================================================
module_list = []
module_number = 0
connection_done_flag = False

for module in designJson["modules"]:
# ----------------------------------------------------------------------------------------
# Environment preparing
  print("Processing module " + module['module_name'] + " instace " + module['instance_name'])

  if module['module_name'] not in module_list:
    module_list.append(module['module_name'])
    outputDir = os.path.join(design_dir, module["module_name"], "export")
    try:
      os.makedirs(outputDir)
      print("Directory " + outputDir + " Created ") 
    except FileExistsError:
      print("Directory " + outputDir + " already exists")
      if len(os.listdir(outputDir)) != 0:
        print("Cleaning output directory:" + outputDir + " ...")
        for output_file in os.listdir(outputDir):
          os.remove(os.path.join(outputDir,output_file))

    inputDir = os.path.join(design_dir, module["module_name"], "import")
    try:
      os.makedirs(inputDir)
      print("Directory " + inputDir + " Created ") 
    except FileExistsError:
      print("Directory " + inputDir + " already exists")
      print("Cleaning input directory:" + inputDir + " ...")
      if len(os.listdir(inputDir)) != 0:
        for file in os.listdir(inputDir):
          os.remove(os.path.join(inputDir,file))

    moduleIsGenerator = analogGen(module,configJson,databaseDir,outputDir,inputDir,ipXactDir,fasoc_dir,jsnDir,args.platform,args.mode,args.database,units,module_number,designJson,args.design,connection_done_flag)

    module_number += 1
#---------------------------------------------------------------------------------------      

#---------------------------------------------------------------------------------------     
# If generator is rtl
    if not moduleIsGenerator and "rtl" in module["generator"]:
      shutil.copy(module['src'],outputDir)
      rtlXmlGenerator(configJson["generators"][module["generator"]],module,outputDir,ipXactDir)
#--------------------------------------------------------------------------------------- 

#--------------------------------------------------------------------------------------- 
# If moduel generator is not rtl nor in our generators
    if not moduleIsGenerator and "rtl" not in module["generator"]:
      print("WARNING: Unsupported generator type", module["generator"])
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# The other instance of a module
  else:
    shutil.copy(os.path.join(ipXactDir,moduleJson['module_name'] + '.xml'),os.path.join(ipXactDir,moduleJson['instance_name'] + '.xml'))
#---------------------------------------------------------------------------------------

# STEP 6: Check constraints and close the loop
# ==============================================================================
closedLoop(designJson,jsnDir,design_dir,platformJson,configJson,databaseDir,ipXactDir,fasoc_dir,args.platform,args.mode,args.database,units,module_number,args.design)

# STEP 7: Call Socrates for stitching
# ==============================================================================

workplaceDir = design_dir
projectName = designName + '_socrates_proj'
projectDir = os.path.join(workplaceDir,projectName)
design_vendor =  'arm.com'
design_library = projectName
design_version = 'r0p0'
subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,
'--project', projectName,'--flow', 'AddNewProject'])

for file in os.listdir(ipXactDir):
  shutil.copy(os.path.join(ipXactDir,file), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4_rtl.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite_rtl.xml'), projectDir)
for file in os.listdir(platformJson["socrates_DRC_config"]):
  shutil.copy(os.path.join(platformJson["socrates_DRC_config"],file), workplaceDir)

subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,'--project', projectName,
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/clean.rb?arg1='+designName,
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/convert_json.rb?arg1='+args.design+'&arg2='+designName+'&arg3='+rubiDir+'&arg4='+rubiDir+'/create_Hier.rb&arg5='+rubiDir+'/connect.rb',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/create_Hier.rb',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/connect.rb',
'--check',
'--result', projectDir+'/DRC.log',
'--set', "IDEA_Checks",
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/report.rb?arg1='+rubiDir+'&arg2='+designName+'&arg3='+projectDir+'/Design_Report.txt',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/generate.rb?arg1='+designName+'&arg2='+os.path.join(projectDir,'logical'),
'--flow', 'PrintIpxactSchematic', 'Vendor='+design_vendor, 'Library='+design_library, 'Name='+designName, 'Version='+design_version, 'FileType=pdf', 'Filter=Connections', 'OutputDir='+os.path.join(projectDir,'logical','Schematic')])

# Unifying names
with open (os.path.join(projectDir,'logical',designName,'verilog', designName+'.v'),'r') as socrates_verilog:
  soc_ver=socrates_verilog.read()
with open(args.design) as fdesign:
  designJson = json.load(fdesign)
for module in designJson["modules"]:
  soc_ver = soc_ver.replace(module['generator'] + ' ' + module['instance_name'], module['module_name'] + ' ' + module['instance_name'])
with open(os.path.join(projectDir,'logical',designName,'verilog', designName+'.v'),'w') as socrates_verilog:
  socrates_verilog.write(soc_ver)

# Opening Socrates outputs 
wb.open_new(os.path.join(projectDir,'logical','Schematic','schematic_Connections_'+designName+'_'+design_version+'.pdf'))
wb.open_new(os.path.join(projectDir,'logical',designName,'verilog', designName+'.v'))
wb.open_new(os.path.join(projectDir,'arm.com-'+projectName+'-'+designName+'_design-'+design_version+'.xml'))
wb.open_new(os.path.join(projectDir,'arm.com-'+projectName+'-'+designName+'-'+design_version+'.xml'))

# STEP 7: Assemble SoC run chip level Cadre Flow
# ==============================================================================


# STEP 8: Run chip level Cadre Flow
# ==============================================================================