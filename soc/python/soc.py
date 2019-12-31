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

from jsonXmlGenerator import jsonXmlGenerator
from rtlXmlGenerator import rtlXmlGenerator
from analogGen import analogGen
from ML_model import ML_model

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
    else:
      print("WARNING: Unsupported generator type", module["generator"])
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# The other instance of a module
  else:
    shutil.copy(os.path.join(ipXactDir,moduleJson['module_name'] + '.xml'),os.path.join(ipXactDir,moduleJson['instance_name'] + '.xml'))
#---------------------------------------------------------------------------------------

# STEP 6: Check constraints and close the loop
# ==============================================================================
target_power_constraint = designJson["constraints"]["power"]
target_area_constraint = designJson["constraints"]["area"]
#previous_inputs = []
previous_inputs = {'ldo-gen':[],'pll-gen':[],'mem-gen':[]}

total_power_constraint = target_power_constraint + 1
total_area_constraint = target_area_constraint + 1
iterate_count = 0
number_iteration = 20
connection_done_flag = True
updated_designJsn = ['None'] * (number_iteration + 1)
abs_output_diff = ['None'] * (number_iteration + 1)
updated_designJsn[0] = designJson

while (target_power_constraint < total_power_constraint or target_area_constraint < total_area_constraint) and iterate_count < number_iteration:
  iterate_count += 1
  updated_designJsn[iterate_count] = updated_designJsn[iterate_count -1]

  total_power_constraint = 0
  total_area_constraint = 0
  # max_power_constraint = ['init',-1]
  # max_area_constraint = ['init',-1]
  modules_power_list = []
  modules_area_list = []

  for jsonFile_constraint in os.listdir(jsnDir):
    with open(os.path.join(jsnDir,jsonFile_constraint)) as f_constraint:
      generator_element_constraint = json.load(f_constraint)
    if "Power" in generator_element_constraint["results"]:
      generator_element_constraint["results"]["power"] = generator_element_constraint["results"]["Power"]
      del generator_element_constraint["results"]["Power"]
    if "area" not in generator_element_constraint["results"]:
      generator_element_constraint["results"]["area"] = 100000
    if "power" not in generator_element_constraint["results"]:
      generator_element_constraint["results"]["power"] = 0
    if "area" in generator_element_constraint["results"] and isinstance(generator_element_constraint["results"]["area"],str):
      generator_element_constraint["results"]["area"] = 100000
    with open(os.path.join(jsnDir,jsonFile_constraint), "w") as new_json_constraint:
      json.dump(generator_element_constraint, new_json_constraint, indent=True)

  for jsonFile_constraint in os.listdir(jsnDir):
    with open(os.path.join(jsnDir,jsonFile_constraint)) as f_constraint:
      generator_element_constraint = json.load(f_constraint)
    power_constraint = generator_element_constraint["results"]["power"]
    area_constraint = generator_element_constraint["results"]["area"]

    # if power_constraint > max_power_constraint[1]:
    #   max_power_constraint[0] = generator_element_constraint['module_name']
    #   max_power_constraint[1] = power_constraint
    # if area_constraint > max_area_constraint[1]:
    #   max_area_constraint[0] = generator_element_constraint['module_name']
    #   max_area_constraint[1] = area_constraint

    modules_power_list.append([generator_element_constraint['module_name'],power_constraint])
    modules_area_list.append([generator_element_constraint['module_name'],area_constraint])

    total_power_constraint = total_power_constraint + power_constraint
    total_area_constraint = total_area_constraint + area_constraint

  def sortRegSecond(elem):
    return elem[1]
  modules_power_list.sort(key=sortRegSecond,reverse=True)
  modules_area_list.sort(key=sortRegSecond,reverse=True)

  abs_output_diff[iterate_count -1] = (abs(total_area_constraint-target_area_constraint)/target_area_constraint)**2 + (abs(total_power_constraint-target_power_constraint)/target_power_constraint)**2
  print('total_power_constraint = ' + str(total_power_constraint))
  print('total_area_constraint = ' + str(total_area_constraint))

  if target_area_constraint < total_area_constraint and target_power_constraint < total_power_constraint:
    print("both area and power are not satisfied")
    if (target_area_constraint - total_area_constraint)/target_area_constraint > (target_power_constraint - total_power_constraint)/target_power_constraint:
      #max_constraint = max_area_constraint
      modules_constraint_list = modules_area_list
      target_constraont = 'area'
      print('area has more priority')
      #print('target_modification for area: ' + max_constraint[0])
    else:
      #max_constraint = max_power_constraint
      modules_constraint_list = modules_power_list
      target_constraont = 'power'
      print('power has more priority')
      #print('target_modification for power: ' + max_power_constraint[0])  

  elif target_area_constraint < total_area_constraint:
    #max_constraint = max_area_constraint
    modules_constraint_list = modules_area_list
    target_constraont = 'area'
    print("area is not satisfied")
    #print('target_modification for area: ' + max_area_constraint[0])

  elif target_power_constraint < total_power_constraint:
    #max_constraint = max_power_constraint
    modules_constraint_list = modules_power_list
    target_constraont = 'power'
    print("power is not satisfied")
    #print('target_modification for power: ' + max_power_constraint[0])

  else:
    print("Both power and area are satisfied")
    break

  feasibility_counter = 0
  while feasibility_counter < len(modules_constraint_list):
    for diff_module in designJson["modules"]:
      module_constraint = modules_constraint_list[feasibility_counter]
      #if diff_module["module_name"] == max_constraint[0]:
      if diff_module["module_name"] == module_constraint[0]:
        print(diff_module["module_name"] + " is going to be regenerate")
        outputDir = os.path.join(design_dir, diff_module["module_name"], "export")
        module,previous_input,feasible = ML_model(diff_module,platformJson["platforms"]["tsmc65lp"]["socModel"],outputDir,target_area_constraint-total_area_constraint,target_power_constraint-total_power_constraint,previous_inputs)
        
        if feasible:
          print("Cleaning output directory:" + outputDir + " ...")
          for output_file in os.listdir(outputDir):
            os.remove(os.path.join(outputDir,output_file))
          inputDir = os.path.join(design_dir, module["module_name"], "import")
          print("Cleaning input directory:" + inputDir + " ...")
          for file in os.listdir(inputDir):
            os.remove(os.path.join(inputDir,file))
          moduleIsGenerator = analogGen(module,configJson,databaseDir,outputDir,inputDir,ipXactDir,fasoc_dir,jsnDir,args.platform,args.mode,args.database,units,module_number,designJson,args.design,connection_done_flag)

          for updated_module_counter,updated_module in enumerate(updated_designJsn[iterate_count]["modules"]):
            #if updated_module["module_name"] == max_constraint[0]:
            if updated_module["module_name"] == module_constraint[0]:
              updated_designJsn[iterate_count]["modules"][updated_module_counter] = module
              with open(os.path.join(design_dir,'updated_desin.json'), "w") as updatedJsnFile:
                json.dump(updated_designJsn[iterate_count], updatedJsnFile, indent=True)

          feasibility_counter = len(modules_constraint_list)
          break

        else:
          feasibility_counter += 1
          break

print('Total number of iteration is: ' + str(iterate_count))

total_power_constraint = 0
total_area_constraint = 0
for jsonFile_constraint in os.listdir(jsnDir):
  with open(os.path.join(jsnDir,jsonFile_constraint)) as f_constraint:
    generator_element_constraint = json.load(f_constraint)
  power_constraint = generator_element_constraint["results"]["power"]
  area_constraint = generator_element_constraint["results"]["area"]
  total_power_constraint = total_power_constraint + power_constraint
  total_area_constraint = total_area_constraint + area_constraint

abs_output_diff[iterate_count] = (abs(total_area_constraint-target_area_constraint)/target_area_constraint)**2 + (abs(total_power_constraint-target_power_constraint)/target_power_constraint)**2
del abs_output_diff[iterate_count +1:number_iteration + 1]

if target_power_constraint < total_power_constraint or target_area_constraint < total_area_constraint:
  print("We could not satisfy both power and area")

  optimized_func_list = np.where(abs_output_diff == np.amin(abs_output_diff))
  optimized_func_index = optimized_func_list[0][0]
  with open(os.path.join(design_dir,'updated_desin.json'), "w") as updatedJsnFile:
    json.dump(updated_designJsn[optimized_func_index], updatedJsnFile, indent=True)
  
else:
  print("Both power and area are satisfied")

# STEP 7: Call Socrates for stitching
# ==============================================================================



# workplaceDir = design_dir
# projectName = designName + '_socrates_proj'
# projectDir = os.path.join(workplaceDir,projectName)

# subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,
# '--project', projectName,'--flow', 'AddNewProject'])

# for file in os.listdir(ipXactDir):
#   shutil.copy(os.path.join(ipXactDir,file), projectDir)
# shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4.xml'), projectDir)
# shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4_rtl.xml'), projectDir)
# shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite.xml'), projectDir)
# shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite_rtl.xml'), projectDir)
# for file in os.listdir(platformJson["socrates_DRC_config"]):
#   shutil.copy(os.path.join(platformJson["socrates_DRC_config"],file), workplaceDir)
# #shutil.copy(platformJson["socrates_DRC_config"], workplaceDir)

# subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,'--project', projectName,
# '--flow', 'RunScript', 'ScriptFile='+rubiDir+'/clean.rb?arg1='+designName,
# '--flow', 'RunScript', 'ScriptFile='+rubiDir+'/convert_json.rb?arg1='+args.design+'&arg2='+designName+'&arg3='+rubiDir+'&arg4='+rubiDir+'/create_Hier.rb&arg5='+rubiDir+'/connect.rb',
# '--flow', 'RunScript', 'ScriptFile='+rubiDir+'/create_Hier.rb',
# '--flow', 'RunScript', 'ScriptFile='+rubiDir+'/connect.rb',
# '--check',
# '--result', projectDir+'/DRC.log',
# '--flow', 'RunScript', 'ScriptFile='+rubiDir+'/report.rb?arg1='+rubiDir+'&arg2='+designName+'&arg3='+projectDir+'/Design_Report.txt',
# '--flow', 'RunScript', 'ScriptFile='+rubiDir+'/generate.rb?arg1='+designName+'&arg2='+os.path.join(projectDir,'logical')])

# with open (os.path.join(projectDir,'logical',designName,'verilog', designName+'.v'),'r') as socrates_verilog:
#   soc_ver=socrates_verilog.read()
# with open(args.design) as fdesign:
#   designJson = json.load(fdesign)
# for module in designJson["modules"]:
#   soc_ver = soc_ver.replace(module['generator'] + ' ' + module['instance_name'], module['module_name'] + ' ' + module['instance_name'])
# with open(os.path.join(projectDir,'logical',designName,'verilog', designName+'.v'),'w') as socrates_verilog:
#   socrates_verilog.write(soc_ver)


# STEP 7: Assemble SoC run chip level Cadre Flow
# ==============================================================================


# STEP 8: Run chip level Cadre Flow
# ==============================================================================