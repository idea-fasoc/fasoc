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

#def renameDB(file,postfix):
def modifyDBFiles(file,postfix,new_module_name,old_module_name):
	if postfix != '.db' and postfix != '.gds.gz':

		if postfix == '.json':
			with open(file, "r") as f:
				fdata = json.load(f)
			fdata["module_name"] = new_module_name
			with open(file, "w") as f:
				json.dump(fdata, f, indent = True)
		else:
			with open (file,'r') as f:
				fdata=f.read()
			if postfix == '.lef':
				fdata = fdata.replace('MACRO ' + old_module_name, 'MACRO ' + new_module_name)
				fdata = fdata.replace('FOREIGN ' + old_module_name, 'FOREIGN ' + new_module_name)
				fdata = fdata.replace('END ' + old_module_name, 'END ' + new_module_name)

			elif postfix == '.lib':
				fdata = fdata.replace('library("' + old_module_name, 'library("' + new_module_name)
				fdata = fdata.replace('cell( ' + old_module_name, 'cell( ' + new_module_name)

			elif postfix == '.spi' or postfix == '.cdl':
				fdata = fdata.replace('.SUBCKT ' + old_module_name + ' ', '.SUBCKT ' + new_module_name + ' ')

			elif postfix == '.v' or postfix == '.lvs.v':
				fdata = fdata.replace('module ' + old_module_name, 'module ' + new_module_name)
				fdata = fdata.replace('#  Design:            ' + old_module_name, '#  Design:            ' + new_module_name)

			with open(file, 'w') as f:
			  f.write(fdata)