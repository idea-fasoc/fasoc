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

import argparse	# arguement parsing
import sys	# exit function
import os	# filesystem manipulation
import json
import shutil
import re
import subprocess	# process
from subprocess import call

# Parse and validate arguments
# ==============================================================================
soc_dir = os.path.dirname(__file__)
fasoc_dir	= os.path.relpath(os.path.join(soc_dir,"../.."))

parser = argparse.ArgumentParser(description='Cleaning FASoC Integration Tool')
parser.add_argument('--design', required=True,
					help='Resolved design description json file path')
parser.add_argument('--platform', default="tsmc65lp",
					help='PDK/process kit for cadre flow (.e.g tsmc65lp)')
parser.add_argument('--platform_config', default=os.path.join(fasoc_dir, "config/platform_config.json"),
					help='Platform configuration json file path')
parser.add_argument('--connection', default="remove",
					help='Whether removal connection in design file')
parser.add_argument('--database', default="remove",
					help='Whether removal the module from the database')
parser.add_argument('--synthesis', default="remove",
					help='Whether removal the synthesis files')
args = parser.parse_args()

print("Loading design: ", args.design)
try:
	with open(args.design) as f:
		designJson = json.load(f)
except ValueError as e:
	print("Error occurred opening or loading design json file: ", args.design)
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

designDir = os.path.dirname(args.design)
databaseDir = platformJson["platforms"][args.platform]["database"]
rubiDir = os.path.join(soc_dir,'..','rubi')
designName = designJson['design_name']

if args.platform == "tsmc65lp":
	synthDir = os.path.join(designDir,"fasoc_test")
elif args.platform == "gf12lp":
	synthDir = os.path.join(designDir,"fasoc_test_12")

# Removing the unnecessary files at the design directory
print("Cleaning design directory ...")
for file in os.listdir(designDir):
	file_name = (file.split('.'))[0]
	if file_name != '':
		postfix = (file.split(file_name))[-1]
	else:
		shutil.rmtree(os.path.join(designDir,file))
		postfix = 'N/A'

	if file == 'updated_desin.json':
		os.remove(os.path.join(designDir,file))
	if not (postfix == '.json' or file == 'Makefile' or 'postfix' == 'N/A' or file == 'fasoc_test' or file == 'fasoc_test_12' or postfix == '.tcl'):
		if os.path.isfile(os.path.join(designDir,file)):
			os.remove(os.path.join(designDir,file))
		elif	os.path.isdir(os.path.join(designDir,file)):
			shutil.rmtree(os.path.join(designDir,file))

# Removing the database
if args.database == "remove":
	if	os.path.isdir(databaseDir):
		print("Cleaning database directory ...")
		shutil.rmtree(databaseDir)

# Removing connection in the design json file
if args.connection == "remove":
	if "connections" in designJson:
		print("Cleaning design connection ...")
		del designJson["connections"]
		with open(args.design, "w") as f:
			json.dump(designJson, f, indent=True)

# Removing the generated ruby files
rubi_clean_tag = False
for file in os.listdir(rubiDir):
	if file == 'connect.rb' or file == 'create_Hier.rb':
		os.remove(os.path.join(rubiDir,file))
		rubi_clean_tag = True
	if rubi_clean_tag:
		print("Cleaning rubi directory ...")

# Removing the generated copied verilog files on synthesis directory
if args.synthesis == "remove":
	print("Cleaning synthesis directory ...")
	for module in designJson["modules"]:
		if module["generator"] == "memory-gen":
			dst_module_verilogDir = os.path.join(synthDir,"src","mem",module["module_name"] + ".v")
		elif module["generator"] == "m0mcu_rtl":
			dst_module_verilogDir = os.path.join(synthDir,"m0sdk","systems","cortex_m0_mcu","verilog",module["module_name"] + ".v")
		elif module["generator"] != "cmsdk_apb_slave_mux_rtl":
			dst_module_verilogDir = os.path.join(synthDir,"src",module["module_name"] + ".v")
		try:
			os.remove(dst_module_verilogDir) 
		except FileNotFoundError:
			pass
		if module["generator"] == "cmsdk_apb_slave_mux_rtl":
			dst_module_verilogDir = os.path.join(synthDir,"m0sdk","logical",module["module_name"])
		try:
			shutil.rmtree(dst_module_verilogDir) 
		except FileNotFoundError:
			pass

	# Removing create_clock in constraints.tcl
	constraintsDir = os.path.join(synthDir,"scripts","dc","constraints.tcl")
	temp_constraintsDir = os.path.join(synthDir,"scripts","dc","temp_constraints.tcl")
	with open(constraintsDir, 'r') as constraints_file, open(temp_constraintsDir, 'w') as temp_constraints_file:
		for line in constraints_file:
			remove_line_tag = False
			if re.match(r'create_clock \[get_pins ',line) or re.match(r'             -name CLK_OUT \\',line) or re.match(r'             -period \$VCO_PERIOD',line):
				remove_line_tag = True
				create_clock_pat = r'create_clock \[get_pins (\S+)/synth_pll/'
				pll_instance_name = re.findall(create_clock_pat,line)
				if pll_instance_name != []:
					initial_first_create_clock_line = rf'create_clock \[get_pins {pll_instance_name[0]}/synth_pll/CLK_OUT\] \\'
					line = re.sub(initial_first_create_clock_line,"",line)
					initial_second_create_clock_line = rf'create_clock \[get_pins {pll_instance_name[0]}/synth_pll/CLKREF_RETIMED_1\] \\'
					line = re.sub(initial_second_create_clock_line,"",line)
				line = re.sub(r"             -name CLK_OUT \\","",line)
				line = re.sub("             -period \$VCO_PERIOD","",line)
			if remove_line_tag:
				if not line.strip():
					continue
			temp_constraints_file.write(line)
	os.rename(temp_constraintsDir,constraintsDir)

	try:
		os.remove(os.path.join(synthDir,"m0sdk","systems","cortex_m0_mcu","verilog",designName + ".v")) 
	except FileNotFoundError:
		pass

	subprocess.check_call(["make","bleach_synth"],cwd=synthDir)