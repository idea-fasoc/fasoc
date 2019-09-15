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
from subprocess import call
from collections import OrderedDict

from checkDB import checkDB
from rtlcheckDB import rtlcheckDB
from jsonXmlGenerator import jsonXmlGenerator
from rtlXmlGenerator import rtlXmlGenerator

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

    if module["generator"] in configJson["generators"] and "rtl" not in module["generator"]:
      foundDB = checkDB(module,databaseDir,outputDir,ipXactDir)
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# Generate analog block      
      if not foundDB:
        print(module["module_name"] + " is going to be generate")
        specFilePath = os.path.join(inputDir, module["module_name"] + ".spec")
        outputSpec = module
        del outputSpec["instance_name"]
        with open(specFilePath, "w") as specfile:
          json.dump(outputSpec, specfile, indent=True)

        try:
          cmd1 = os.path.join(fasoc_dir,configJson["generators"][module["generator"]]["path"])
        except KeyError:
          print("Please specify path for module: " + module["module_name"] + "instance: " + module["instance_name"])
        cmd = cmd1 + " --specfile " + specFilePath + " --output " + outputDir + " --platform " + args.platform
        print("Launching: ", cmd)
        
        if module["generator"] == 'pll-gen':
          try:
            #ret = subprocess.check_call(["python",cmd1,"--specfile",specFilePath,"--output",outputDir,"--platform",args.platform], shell=True)
            ret = subprocess.check_call([cmd1,"--specfile",specFilePath,"--output",outputDir,"--platform",args.platform,"--pex_verify",'0','--run_vsim','0'])
            if ret:
              print("Error: Command returned error " + error)
              sys.exit(1)
          except:
            print ("Error/Exception occurred while running command:", sys.exc_info()[0])
        else:
          try:
            #ret = subprocess.check_call(["python",cmd1,"--specfile",specFilePath,"--output",outputDir,"--platform",args.platform], shell=True)
            ret = subprocess.check_call([cmd1,"--specfile",specFilePath,"--output",outputDir,"--platform",args.platform])
            if ret:
              print("Error: Command returned error " + error)
              sys.exit(1)
          except:
            print ("Error/Exception occurred while running command:", sys.exc_info()[0])

        #os.chdir(cwd)

        for output_file in os.listdir(outputDir):
          output_file_name = (output_file.split('.'))[0]
          postfix = (output_file.split(output_file_name))[-1]
          os.rename(os.path.join(outputDir,output_file),os.path.join(outputDir,module['module_name'] + postfix))
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# Add to database/cache
        try:
          os.makedirs(os.path.join(databaseDir,'ZIP'))
          print("Directory " + os.path.join(databaseDir,'ZIP') +  " Created in the database") 
        except FileExistsError:
          print("Directory " + os.path.join(databaseDir,'ZIP') + " already exists in the database")
        
        if not os.path.exists(os.path.join(databaseDir,"DB_mem.txt")):
          with open(os.path.join(databaseDir,"DB_mem.txt"), 'w') as DBetxt:
            DBetxt.write('0')

        with open(os.path.join(databaseDir,"DB_mem.txt"),'r') as DBetxt:
          DBNumber=DBetxt.readlines()
        intDBNumber=int((DBNumber[0].split('\n'))[0])
        with zipfile.ZipFile(os.path.join(databaseDir,'ZIP',module["module_name"] + str(intDBNumber) + '.zip'), 'w') as myzip:
          for file in os.listdir(outputDir):
            if not '.xml' in file:   
              myzip.write(os.path.join(outputDir,file),file)

        try:
          os.makedirs(os.path.join(databaseDir,'JSN',module["generator"]))
          print("Directory " + os.path.join(databaseDir,'JSN',module["generator"]) +  " Created in the database") 
        except FileExistsError:
          print("Directory " + os.path.join(databaseDir,'JSN',module["generator"]) + " already exists in the database")

        shutil.copy(os.path.join(outputDir,module['module_name'] + '.json'),os.path.join(databaseDir,'JSN',module["generator"],module["module_name"] + str(intDBNumber) + '.json'))

        intDBNumber += 1
        with open(os.path.join(databaseDir,"DB_mem.txt"), 'w') as DBetxt:
            DBetxt.write(str(intDBNumber))
#---------------------------------------------------------------------------------------

      
#---------------------------------------------------------------------------------------       
# Check if generator and database are done and make ipxact
      jsonXmlGenerator(configJson["generators"][module["generator"]],module,units,outputDir,ipXactDir)
      postfixes = ['.db','.gds.gz','.json','.lef','.lib','.spi','.v','.cdl','.xml']
      for postfix in postfixes:
        if not os.path.exists(os.path.join(outputDir,module["module_name"] + postfix)):
          print(module["module_name"] + postfix + " does not exist")
#---------------------------------------------------------------------------------------      

#---------------------------------------------------------------------------------------     
# If generator is rtl
    elif "rtl" in module["generator"]:
      shutil.copy(module['src'],outputDir)
      rtlXmlGenerator(configJson["generators"][module["generator"]],module,outputDir,ipXactDir)
      foundDB = rtlcheckDB(module,databaseDir,outputDir,ipXactDir)

      if not foundDB:
        pass
#--------------------------------------------------------------------------------------- 

#--------------------------------------------------------------------------------------- 
# If moduel generator is not rtl nor in our generators
    else:
      print("WARNING: Unsupported generator type", module["generator"])
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# The other instance of a module
  else:
    shutil.copy(os.path.join(ipXactDir,moduleJson['module_name'] + '.xml'),os.path.join(ipXactDir,moduleJson['instance_name'] + '.xml'))
#---------------------------------------------------------------------------------------

# STEP 6: Call Socrates for stitching
# ==============================================================================
workplaceDir = design_dir
projectName = designName + '_socrates_proj'
projectDir = os.path.join(workplaceDir,projectName)

subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,
'--project', projectName,'--flow', 'AddNewProject'])

for file in os.listdir(ipXactDir):
  shutil.copy(os.path.join(ipXactDir,file), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4_rtl.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite_rtl.xml'), projectDir)
shutil.copy(platformJson["socrates_DRC_config"], workplaceDir)

subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,'--project', projectName,
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_00_convert_json.rb?arg1='+args.design+'&arg2='+designName+'&arg3='+rubiDir+'/CLI_01_Create_Hier.rb&arg4='+rubiDir+'/CLI_02_Connect.rb',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_01_Create_Hier.rb',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_02_Connect.rb',
'--check',
'--result', projectDir+'/DRC.log',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_03_Report.rb?arg1='+designName+'&arg2='+projectDir+'/Design_Report.txt',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_04_Generate.rb?arg1='+designName+'&arg2='+os.path.join(projectDir,'logical',designName)])

# STEP 7: Assemble SoC run chip level Cadre Flow
# ==============================================================================


# STEP 8: Run chip level Cadre Flow
# ==============================================================================


