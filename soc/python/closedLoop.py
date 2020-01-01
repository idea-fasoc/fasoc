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
import os  # filesystem manipulation
import json  # json parsing
import numpy as np

from ML_model import ML_model
from analogGen import analogGen

def closedLoop(designJson,jsnDir,design_dir,platformJson,configJson,databaseDir,ipXactDir,fasoc_dir,args_platform,args_mode,args_database,units,module_orig_number,args_design):
  
  target_power_constraint = designJson["constraints"]["power"]
  target_area_constraint = designJson["constraints"]["area"]
  previous_inputs = {'ldo-gen':[],'pll-gen':[],'memory-gen':[]}

  total_power_constraint = target_power_constraint + 1
  total_area_constraint = target_area_constraint + 1
  iterate_count = 0
  number_iteration = 100
  connection_done_flag = True
  updated_designJsn = ['None'] * (number_iteration + 1)
  abs_output_diff = ['None'] * (number_iteration + 1)
  updated_designJsn[0] = designJson

  while (target_power_constraint < total_power_constraint or target_area_constraint < total_area_constraint) and iterate_count < number_iteration:
    iterate_count += 1
    module_number = module_orig_number + iterate_count
    updated_designJsn[iterate_count] = updated_designJsn[iterate_count -1]

    total_power_constraint = 0
    total_area_constraint = 0
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
        modules_constraint_list = modules_area_list
        target_constraont = 'area'
        print('area has more priority')
      else:
        modules_constraint_list = modules_power_list
        target_constraont = 'power'
        print('power has more priority') 

    elif target_area_constraint < total_area_constraint:
      modules_constraint_list = modules_area_list
      target_constraont = 'area'
      print("area is not satisfied")

    elif target_power_constraint < total_power_constraint:
      modules_constraint_list = modules_power_list
      target_constraont = 'power'
      print("power is not satisfied")

    else:
      print("Both power and area are satisfied")
      break

    feasibility_counter = 0
    while feasibility_counter < len(modules_constraint_list):
      for diff_module in designJson["modules"]:
        module_constraint = modules_constraint_list[feasibility_counter]
        if diff_module["module_name"] == module_constraint[0]:
          print(diff_module["module_name"] + " is going to be regenerate")
          outputDir = os.path.join(design_dir, diff_module["module_name"], "export")
          module,previous_inputs,feasible = ML_model(diff_module,platformJson["platforms"]["tsmc65lp"]["socModel"],outputDir,target_area_constraint-total_area_constraint,target_power_constraint-total_power_constraint,previous_inputs)
          
          if feasible:
            print("Cleaning output directory:" + outputDir + " ...")
            for output_file in os.listdir(outputDir):
              os.remove(os.path.join(outputDir,output_file))
            inputDir = os.path.join(design_dir, module["module_name"], "import")
            print("Cleaning input directory:" + inputDir + " ...")
            for file in os.listdir(inputDir):
              os.remove(os.path.join(inputDir,file))
            moduleIsGenerator = analogGen(module,configJson,databaseDir,outputDir,inputDir,ipXactDir,fasoc_dir,jsnDir,args_platform,args_mode,args_database,units,module_number,designJson,args_design,connection_done_flag)

            for updated_module_counter,updated_module in enumerate(updated_designJsn[iterate_count]["modules"]):
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