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
#from rtlcheckDB import rtlcheckDB
from jsonXmlGenerator import jsonXmlGenerator
from rtlXmlGenerator import rtlXmlGenerator
from fastAnalogGen import fastAnalogGen

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
count = 0

# ----------------------------------------------------------------------------------------

for i in range(0,18): # PLL

  designJson["modules"][0]["module_name"] = "pll" + str(count)
  count += 1
  designJson["modules"][0]["instance_name"] = "i_pll" + str(count)
  designJson["modules"][0]["specifications"]["Fnom_min"] = 600e6 + 20e6 * i
  designJson["modules"][0]["specifications"]["Fnom_max"] = 620e6 + 20e6 * i

  with open(args.design,"w") as change_f:
    json.dump(designJson, change_f, indent=True)
  with open(args.design) as f:
    designJson = json.load(f)
  for module in designJson["modules"]:
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

      moduleIsGenerator = fastAnalogGen(module,configJson,databaseDir,outputDir,inputDir,ipXactDir,fasoc_dir,jsnDir,args.platform,args.mode,args.database,units)