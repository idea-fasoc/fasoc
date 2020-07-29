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
import subprocess  # process
from subprocess import call

soc_dir = os.path.dirname(__file__)
fasoc_dir  = os.path.relpath(os.path.join(soc_dir,"../.."))

parser = argparse.ArgumentParser(description='Hierarchy Checker Tool')
parser.add_argument('--list', required=True,
                    help='The file that include list of the files that shouldbe check')
args = parser.parse_args()

print("Check list: ", args.list)
try:
  with open(args.list,'r') as text_hierarchy_file:
    text_hierarchy_line = text_hierarchy_file.readlines()
except ValueError as e:
  print("Error occurred opening or loading the check list file: ", args.list)
  print("Exception: ", str(e))
  sys.exit(1)

for i in range(0,len(text_hierarchy_line)//2):
	subprocess.call(['diff', (text_hierarchy_line[2*i].split('\n'))[0], (text_hierarchy_line[2*i+1].split('\n'))[0]])