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

import os
import json
import sys
import argparse  # arguement parsing

from ml_regression_merged import ml_regression_merged
from algebric_model_evaluator import algebric_model_evaluator

wrapper_dir = os.path.dirname(__file__)
soc_dir  = os.path.relpath(os.path.join(wrapper_dir,"../.."))

parser = argparse.ArgumentParser(description='FASoC Integration Tool')
parser.add_argument('--platform', default="tsmc65lp",
                    help='PDK/process kit for cadre flow (.e.g tsmc65lp)')
parser.add_argument('--soc_model_config', default=os.path.join(soc_dir, "config/soc_model_config.json"),
                    help='soc model config configuration json file path')
parser.add_argument('--mode', default="ml_regression",
                    help='ml_regression_merged should be run or algebric_model_evaluator')
parser.add_argument('--generator', default="memory-gen",
                    help='which generator should be used')
parser.add_argument('--constraint', default="area",
                    help='power or area')
args = parser.parse_args()

print("Loading platform Config: ", args.soc_model_config)
try:
  with open(args.soc_model_config) as f:
    socModelJson = json.load(f)
except ValueError as e:
  print("Error occurred opening or loading soc_model_config json file: ",
        args.soc_model_config)
  print("Exception: ", str(e))
  sys.exit(1)

sheetDir = socModelJson["platforms"]["tsmc65lp"]["socModel"]

for gen in socModelJson["platforms"]["tsmc65lp"]["generators"]:
	if gen["name"] == args.generator:
		if args.mode == 'ml_regression':
			ml_regression_merged(os.path.join(sheetDir,gen["train_test_input"]),os.path.join(sheetDir,gen["train_test_output"]),args.constraint,gen["inputs"]) 
		elif args.mode == 'model_evaluator':
			algebric_model_evaluator(os.path.join(sheetDir,gen["whole"]),args.constraint,(args.generator.split('-'))[0],gen["inputs"])
		else:
			print("This mode is not acceptable")
			sys.exit(0)