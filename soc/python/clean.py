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

soc_dir = os.path.dirname(__file__)
fasoc_dir	= os.path.relpath(os.path.join(soc_dir,"../.."))

parser = argparse.ArgumentParser(description='Cleaning FASoC Integration Tool')
parser.add_argument('--design', required=True,
					help='Resolved design description json file path')
parser.add_argument('--platform_config', default=os.path.join(fasoc_dir, "config/platform_config.json"),
					help='Platform configuration json file path')
parser.add_argument('--connection', default="remove",
					help='whether removal connection in design file')
parser.add_argument('--database', default="remove",
					help='whether removal the module from the database')
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
databaseDir = platformJson["platforms"]["tsmc65lp"]["database"]
rubiDir = os.path.join(soc_dir,'..','rubi')

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
	if not (postfix == '.json' or file == 'Makefile' or 'postfix' == 'N/A' or file == 'fasoc_test' or file == 'fasoc_test_12'):
		if os.path.isfile(os.path.join(designDir,file)):
			os.remove(os.path.join(designDir,file))
		elif	os.path.isdir(os.path.join(designDir,file)):
			shutil.rmtree(os.path.join(designDir,file))

if args.database == "remove":
	if	os.path.isdir(databaseDir):
		print("Cleaning database directory ...")
		shutil.rmtree(databaseDir)

if args.connection == "remove":
	if "connections" in designJson:
		print("Cleaning design connection ...")
		del designJson["connections"]
		with open(args.design, "w") as f:
			json.dump(designJson, f, indent=True)

rubi_clean_tag = False
for file in os.listdir(rubiDir):
	if file == 'connect.rb' or file == 'create_Hier.rb':
		os.remove(os.path.join(rubiDir,file))
		rubi_clean_tag = True
	if rubi_clean_tag:
		print("Cleaning rubi directory ...")