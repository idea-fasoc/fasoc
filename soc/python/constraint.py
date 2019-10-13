#!/usr/bin/env python3

import os  # filesystem manipulation
import json  # json parsing

total_power_constraint = 0
total_area_constraint = 0
max_power_constraint = ['init',-1]
max_area_constraint = ['init',-1]

for jsonFile_constraint in os.listdir(r'/n/trenton/v/fayazi/IDEA/fasoc/tests/tool_integration/ldo-pll-mem/json'):
	with open(os.path.join(r'/n/trenton/v/fayazi/IDEA/fasoc/tests/tool_integration/ldo-pll-mem/json',jsonFile_constraint)) as f_constraint:
		generator_element_constraint = json.load(f_constraint)
	if "Power" in generator_element_constraint["results"]:
		del generator_element_constraint["results"]["Power"]
	if "area" not in generator_element_constraint["results"]:
		generator_element_constraint["results"]["area"] = 100000
	if "power" not in generator_element_constraint["results"]:
		generator_element_constraint["results"]["power"] = 0
	if "area" in generator_element_constraint["results"] and isinstance(generator_element_constraint["results"]["area"],str):
		generator_element_constraint["results"]["area"] = 100000
	with open(os.path.join(r'/n/trenton/v/fayazi/IDEA/fasoc/tests/tool_integration/ldo-pll-mem/json',jsonFile), "w") as new_json_constraint:
          json.dump(generator_element_constraint, new_json_constraint, indent=True)

for jsonFile_constraint in os.listdir(r'/n/trenton/v/fayazi/IDEA/fasoc/tests/tool_integration/ldo-pll-mem/json'):
	with open(os.path.join(r'/n/trenton/v/fayazi/IDEA/fasoc/tests/tool_integration/ldo-pll-mem/json',jsonFile_constraint)) as f_constraint:
		generator_element_constraint = json.load(f_constraint)
	power_constraint = generator_element_constraint["results"]["power"]
	area_constraint = generator_element_constraint["results"]["area"]

	if power_constraint > max_power_constraint[1]:
		max_power_constraint[0] = generator_element_constraint['module_name']
		max_power_constraint[1] = power_constraint
	if area_constraint > max_area_constraint[1]:
		max_area_constraint[0] = generator_element_constraint['module_name']
		max_area_constraint[1] = area_constraint

	total_power_constraint = total_power_constraint + power_constraint
	total_area_constraint = total_area_constraint + area_constraint

with open(r'/n/trenton/v/fayazi/IDEA/fasoc/tests/tool_integration/ldo-pll-mem/design2.json') as f_constraint:
	design_element_constraint = json.load(f_constraint)
target_power_constraint = design_element_constraint["constraints"]["power"]
target_area_constraint = design_element_constraint["constraints"]["area"]

if target_area_constraint < total_area_constraint:
	print("area is not satisfied")
	print('target_modification for area: ' + max_area[0]_constraint)
else:
	print("area is satisfied")
if target_power_constraint < total_power_constraint:
	print("power is not satisfied")
	print('target_modification for power: ' + max_power_constraint[0])
else:
	print("power is satisfied")