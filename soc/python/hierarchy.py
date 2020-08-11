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

import sys
import os
from optparse import OptionParser
from io import StringIO
import re
from collections import defaultdict
import numpy as np

import pyverilog
from pyverilog.vparser.parser import parse
from pyverilog.vparser.preprocessor import preprocess
from pyverilog.vparser.lexer import dump_tokens

def verilog_writer(start_to_line,from_line_arr,lex_to_dict,end_to_keyword,previous_line,to_file,from_file,task,task_line,in_end_to_line):
	if task == 'Input/Output':
		for line_no in range(start_to_line,len(lex_to_dict)):
			if set(end_to_keyword).issubset(set(lex_to_dict[line_no])):
				if previous_line:
					end_to_line = line_no - 1
				else:
					end_to_line = line_no
				break
	else:
		end_to_line = in_end_to_line

	with open(from_file,'r') as veri_from_file, open(to_file,'r') as veri_to_file:
		veri_from_line = veri_from_file.readlines()
		veri_to_line = veri_to_file.readlines()

# Add ',' to the end of the previous last input/output
	if task == 'Parameter':
		if '//' in veri_to_line[task_line - 1]:
			veri_to_line[task_line - 1] = ''.join([(veri_to_line[task_line - 1].split('//'))[0],',//',(veri_to_line[task_line-1].split('//'))[-1]])
		else:
			veri_to_line[task_line - 1] = ''.join([(veri_to_line[task_line - 1].split('\n'))[0],',\n'])

	new_to_line = [None] * (len(veri_to_line) +  len(from_line_arr))
	new_to_line[0 : end_to_line] =  veri_to_line[0 : end_to_line]
	for counter, line_no in enumerate(from_line_arr):
		new_to_line[end_to_line + counter] = veri_from_line[line_no - 1]
	new_to_line[end_to_line + len(from_line_arr) : len(veri_to_line) + end_to_line + len(from_line_arr)] = veri_to_line[end_to_line : len(veri_to_line)]

	init_output_gen_name = os.path.basename(to_file)
	if '_gen.v' in init_output_gen_name:
		output_gen_file = init_output_gen_name
	else:
		output_gen_file = (init_output_gen_name.split('.v'))[0]+'_gen.v'

	with open(output_gen_file,'w') as veri_to_file:
		veri_to_file.writelines(new_to_line)
	return output_gen_file, veri_from_line, end_to_line + len(from_line_arr)

def verilog_reader(verilog_file,include_line_number,start_keywords):
	lex_dict = defaultdict(list)
	parse_dict = defaultdict(list)
	veri_parse_line_no_arr = []
	nospace_line_arr = []
	line_array_dict = defaultdict(list)
	start_line_dict = dict.fromkeys(list(start_keywords.keys()),0)# Initializing

# Parsing Verilog
# ==============================================================================
	output_buf = 'preprocess.out'
	output_buf = StringIO()
	ast, directives = parse(verilog_file,
                        preprocess_include=options.include,
                        preprocess_define=options.define)
	ast.show(buf=output_buf)
	parser_result = output_buf.getvalue()

	lex = preprocess(verilog_file,
                  include=options.include,
                  define=options.define)
	lex_result = dump_tokens(lex)

# Parsing Verilog Lines
# ==============================================================================
	for line in parser_result.splitlines():
		nospace_line = re.sub(r'\s','',line)
		veri_parse_line_no = int((re.findall(r'\(at(\d+)\)',nospace_line))[0]) - include_line_number #250 is line numbers of cmsdk_mcu_defs.v and 55 is line numbers of cmsdk_ahb_memory_defs.v for destination

		veri_parse_line_no_arr.append(veri_parse_line_no)
		nospace_line_arr.append(nospace_line)

		veri_parse_left_subject = (nospace_line.split(':'))[0]
		veri_parse_right_subject = (re.findall(r'(\S+)\(at\d+\)',(nospace_line.split(':'))[-1]))
		if veri_parse_right_subject != []:
			veri_parse_right_subject = veri_parse_right_subject[0]

		for task in start_keywords:
			start_left_keyword = start_keywords[task][0]
			start_line_offset = start_keywords[task][1] # start_keywords[task][1] is line offset: is 1 for source with Moduledef keyword
			start_right_flag = start_keywords[task][2] # start_keywords[task][2] determines whether should we consider veri_parse_src_right_subject as we do for source with options.module_name for Instantiation keyword
			start_right_keyword = start_keywords[task][3]
			array_line_keyword = start_keywords[task][4]

			if not start_right_flag:
				if veri_parse_left_subject == start_left_keyword:
					start_line = veri_parse_line_no + start_line_offset
					start_line_dict[task] = start_line
			else:
				if (veri_parse_left_subject == start_left_keyword) and (veri_parse_right_subject == start_right_keyword):
					start_line = veri_parse_line_no + start_line_offset
					start_line_dict[task] = start_line

			if veri_parse_left_subject == array_line_keyword:
				line_array_dict[task].append(veri_parse_line_no)

		parse_dict[veri_parse_line_no].append([veri_parse_left_subject, veri_parse_right_subject])

	for line in lex_result.splitlines():
		veri_lex_line_no = int((re.findall(r'\S+\s\S+\s(\d+)',line))[0]) - include_line_number #250 is line numbers of cmsdk_mcu_defs.v and 55 is line numbers of cmsdk_ahb_memory_defs.v
		veri_lex_subject = (re.findall(r'\S+\s(\S+)\s\d+',line))[0]
		lex_dict[veri_lex_line_no].append(veri_lex_subject)

	# values = np.array(veri_parse_line_no_arr)
	# desired_index = (np.where(values==96))[0]
	# print(np.array(nospace_line_arr)[desired_index])

	return start_line_dict, parse_dict, line_array_dict, lex_dict

# Parse and validate arguments
# ==============================================================================
soc_dir = os.path.dirname(__file__)
fasoc_dir  = os.path.relpath(os.path.join(soc_dir,"../.."))

optparser = OptionParser()
optparser.add_option("-S", "--source_file", dest="source_file", action="append",
                     default=[], help='The verilog source file')
optparser.add_option("-M", "--module_name", dest="module_name", action="append",
                     default=[], help='The module name that is going to be ported')
optparser.add_option("--dest_file", dest="dest_file", action="append",
                     default=[], help='The verilog destination file')
optparser.add_option("--module_file", dest="module_file", action="append",
                     default=[], help='The verilog file of the module that we are moving')
optparser.add_option("--hierarchy_file", dest="hierarchy_file", action="append",
                     default=[], help='The file that describes hierarchy')
optparser.add_option("-I", "--include", dest="include", action="append",
                     default=[], help="Include path")
optparser.add_option("-D", dest="define", action="append",
                     default=[], help="Macro Definition")
(options, args) = optparser.parse_args()

# Source Verilog
# ==============================================================================
start_src_keywords = {'Parameter':['ModuleDef',1,False,'DUMB','DUMB'],'Instantiation':['InstanceList',0,True,(options.module_name)[0],'DUMB'],'Input/Output':['DUMB',0,False,'DUMB','Ioport']}
start_src_line_dict, parse_src_dict, line_src_array_dict, lex_src_dict = verilog_reader(options.source_file,0,start_src_keywords)

inout_src_instant_arr = []
inout_src_real_arr = []
wire_src_line_arr = []
wire_src_width_dict = defaultdict(list)

# Parameter
start_main_module_src_line = start_src_line_dict['Parameter']
start_module_src_instance_line = start_src_line_dict['Instantiation']
inout_src_line_arr = line_src_array_dict['Input/Output']

for line_no in range(start_main_module_src_line,len(lex_src_dict)):
	if 'RPAREN' in lex_src_dict[line_no]:
		end_main_module_param_src_line = line_no
		break
# Instantiation
for line_no in range(start_module_src_instance_line,len(lex_src_dict)):
	if 'RPAREN' in lex_src_dict[line_no] and 'SEMICOLON' in lex_src_dict[line_no]:
		end_module_src_instance_line = line_no + 1
		break
# Input/Output
for line_no in range(start_module_src_instance_line,end_module_src_instance_line):
	if len(parse_src_dict[line_no]) != 0:
		if 'PortArg' in parse_src_dict[line_no][0]:
			for elem in parse_src_dict[line_no]:
				if elem[0] == 'Identifier':
					inout_src_instant_arr.append(elem[1])
				elif elem[0] == 'PortArg':
					inout_src_real_arr.append(elem[1])
for line_no in range(start_main_module_src_line,start_module_src_instance_line):
	for inout in inout_src_instant_arr:
		if ['Wire',''.join([inout,',False'])] in parse_src_dict[line_no]:
			wire_src_line_arr.append(line_no)
			for elem in parse_src_dict[line_no]:
				if 'IntConst' == elem[0]:
					wire_src_width_dict[inout].append(int(elem[1]))
					#print(elem[1])
for line_no in range(start_main_module_src_line,len(lex_src_dict)):
	if 'RPAREN' in lex_src_dict[line_no] and 'SEMICOLON' in lex_src_dict[line_no]:
		end_main_module_src_line = line_no
		break

# Module Verilog
# ==============================================================================
start_mdl_keywords = {'Input/Output':['ModuleDef',1,False,'DUMB','DUMB']}
start_mdl_line_dict, parse_mdl_dict, line_mdl_array_dict, lex_mdl_dict = verilog_reader(options.module_file,0,start_mdl_keywords)

wire_mdl_line_arr = []
start_main_module_mdl_line = start_mdl_line_dict['Input/Output']

# Input/Output
for line_no in range(start_main_module_mdl_line,len(lex_mdl_dict)):
	if 'RPAREN' in lex_mdl_dict[line_no]  and 'SEMICOLON' in lex_mdl_dict[line_no]:
		end_main_module_mdl_line = line_no
		break
#print(line_no)
for line_no in range(start_main_module_mdl_line,end_main_module_mdl_line + 1):
	if ['Ioport',[]] in parse_mdl_dict[line_no]:
		#width_mdl_arr = []
		for elem in parse_mdl_dict[line_no]:
			#if elem[0] == 'IntConst':
			#	width_mdl_arr.append(int(elem[1]))
			if elem[0] == 'Input':
				inout_mdl = 'output'
				inout_instant_name = inout_src_instant_arr[inout_src_real_arr.index((elem[1].split(',False'))[0])]
			if elem[0] == 'Output':
				inout_mdl = 'input'
				inout_instant_name = inout_src_instant_arr[inout_src_real_arr.index((elem[1].split(',False'))[0])]	
		#if width_mdl_arr != []:
		if inout_instant_name in wire_src_width_dict:
			#wire_mdl_line_arr.append('  '+inout_mdl+'  wire  ['+str(max(width_mdl_arr))+':'+str(min(width_mdl_arr))+']  '+inout_instant_name+',\n')
			wire_mdl_line_arr.append('  '+inout_mdl+'  wire  ['+str(max(wire_src_width_dict[inout_instant_name]))+':'+str(min(wire_src_width_dict[inout_instant_name]))+']  '+inout_instant_name+',\n')
		else:
			wire_mdl_line_arr.append('  '+inout_mdl+'  wire         '+inout_instant_name+',\n')

# Destination Modificatoion
# ==============================================================================
# Parameter
start_parameter_dst_keywords = {'Parameter':['ModuleDef',0,False,'DUMB','Parameter']}
start_dst_line_dict, parse_dst_dict, line_dst_array_dict, lex_dst_dict = verilog_reader(options.dest_file,250+55,start_parameter_dst_keywords)
start_main_module_dst_line = start_dst_line_dict['Parameter']
parameter_dst_line_arr = line_dst_array_dict['Parameter']
task_line = parameter_dst_line_arr[-1] # Line number of the last parameter
updated_dst_file, veri_source_line, end_dst_line = verilog_writer(start_main_module_dst_line,list(range(start_main_module_src_line,end_main_module_param_src_line)),lex_dst_dict,['RPAREN'],True,(options.dest_file)[0],(options.source_file)[0],'Parameter',task_line,task_line+1)
# Input/Output
start_input_output_dst_keywords = {'Input/Output':['ModuleDef',0,False,'DUMB','DUMB']}
start_dst_line_dict, parse_dst_dict, line_dst_array_dict, lex_dst_dict = verilog_reader([updated_dst_file],250+55,start_input_output_dst_keywords)
start_main_module_dst_line = start_dst_line_dict['Input/Output']
updated_dst_file, veri_source_line, end_dst_line = verilog_writer(start_main_module_dst_line,wire_src_line_arr,lex_dst_dict,['RPAREN','SEMICOLON'],False,updated_dst_file,(options.source_file)[0],'Input/Output',0,end_dst_line)
# Instantiation
start_instantiation_dst_keywords = {'Instantiation':['ModuleDef',0,False,'DUMB','DUMB']}
start_dst_line_dict, parse_dst_dict, line_dst_array_dict, lex_dst_dict = verilog_reader([updated_dst_file],250+55,start_instantiation_dst_keywords)
start_main_module_dst_line = start_dst_line_dict['Instantiation']
updated_dst_file, veri_source_line, end_dst_line = verilog_writer(start_main_module_dst_line,list(range(start_module_src_instance_line,end_module_src_instance_line)),lex_dst_dict,['RPAREN','SEMICOLON'],False,updated_dst_file,(options.source_file)[0],'Instantiation',0,end_dst_line)

# Source Modificatoion
# ==============================================================================
#Investigate why line = ''.join(['//',line]) didn't work
for counter, line in enumerate(veri_source_line[start_module_src_instance_line - 1 : end_module_src_instance_line]):
	veri_source_line[start_module_src_instance_line -1 + counter] = ''.join(['//',line])
for line_no in wire_src_line_arr:
	veri_source_line[line_no - 1] = ''.join(['//',veri_source_line[line_no - 1]])

# Input/Output
# Adding ',' to the end of the previous last input/output
if '//' in veri_source_line[inout_src_line_arr[-1] - 1]:
	veri_source_line[inout_src_line_arr[-1] - 1] = ''.join([(veri_source_line[inout_src_line_arr[-1] - 1].split('//'))[0],',//',(veri_source_line[inout_src_line_arr[-1] - 1].split('//'))[-1]])
else:
	veri_source_line[inout_src_line_arr[-1] - 1] = ''.join([(veri_source_line[inout_src_line_arr[-1] - 1].split('\n'))[0],',\n'])

# Defining input/output of the module that we are going to move as output/input of source file
new_source_line = [None] * (len(veri_source_line) +  len(wire_mdl_line_arr))
new_source_line[0 : end_main_module_src_line - 1] =  veri_source_line[0 : end_main_module_src_line - 1]
for counter, line in enumerate(wire_mdl_line_arr):
	if counter != len(wire_mdl_line_arr) - 1:
		new_source_line[end_main_module_src_line - 1 + counter] = line
	else:# Removing ',' from the end of the last input/output
		new_source_line[end_main_module_src_line - 1 + counter] = ''.join([(line.split(','))[0],'\n'])
new_source_line[end_main_module_src_line - 1 + len(wire_mdl_line_arr) : len(veri_source_line) + end_main_module_src_line - 1 + len(wire_mdl_line_arr)] = veri_source_line[end_main_module_src_line - 1: len(veri_source_line)]

with open((((options.source_file)[0]).split('.v'))[0]+'_gen.v','w') as veri_source_file:
	veri_source_file.writelines(new_source_line)

# Hierarchy Modificatoion
# ==============================================================================
with open((options.hierarchy_file)[0],'r') as text_hierarchy_file:
	text_hierarchy_line = text_hierarchy_file.readlines()
for line in text_hierarchy_line:
# Parameter
	start_parameter_hier_keywords = {'Parameter':['ModuleDef',0,False,'DUMB','Parameter'],'Input/Output':['DUMB',0,False,'DUMB','Ioport']}
	start_hier_line_dict, parse_hier_dict, line_hier_array_dict, lex_hier_dict = verilog_reader([line],250+55,start_parameter_hier_keywords)
	start_main_module_hier_line = start_hier_line_dict['Parameter']
	parameter_hier_line_arr = line_hier_array_dict['Parameter']
	task_line = parameter_hier_line_arr[-1] # Line number of the last parameter
	updated_hier_file, veri_source_line, end_hier_line = verilog_writer(start_main_module_hier_line,list(range(start_main_module_src_line,end_main_module_param_src_line)),lex_hier_dict,['RPAREN'],True,line,(options.source_file)[0],'Parameter',task_line,task_line+1)
# Input/Output
# Adding ',' to the end of the previous last input/output
	start_input_output_hier_keywords = {'Input/Output':['ModuleDef',0,False,'DUMB','DUMB'],'Input/Output':['DUMB',0,False,'DUMB','Ioport']}
	start_hier_line_dict, parse_hier_dict, line_hier_array_dict, lex_hier_dict = verilog_reader([updated_hier_file],250+55,start_input_output_hier_keywords)
	inout_hier_line_arr = line_hier_array_dict['Input/Output']
	with open(updated_hier_file,'r') as veri_hier_file:
		veri_hierarchy_line = veri_hier_file.readlines()

	for line_no in range(start_main_module_hier_line,len(lex_hier_dict)):
		if 'RPAREN' in lex_hier_dict[line_no] and 'SEMICOLON' in lex_hier_dict[line_no]:
			end_main_module_hier_line = line_no
			break
	
	if '//' in veri_hierarchy_line[inout_hier_line_arr[-1] - 1]:
		veri_hierarchy_line[inout_hier_line_arr[-1] - 1] = ''.join([(veri_hierarchy_line[inout_hier_line_arr[-1] - 1].split('//'))[0],',//',(veri_hierarchy_line[inout_hier_line_arr[-1] - 1].split('//'))[-1]])
	else:
		veri_hierarchy_line[inout_hier_line_arr[-1] - 1] = ''.join([(veri_hierarchy_line[inout_hier_line_arr[-1] - 1].split('\n'))[0],',\n'])

# Defining input/output of the module that we are going to move as output/input of hierarchy files
	new_hierarchy_line = [None] * (len(veri_hierarchy_line) +  len(wire_mdl_line_arr))
	new_hierarchy_line[0 : end_main_module_hier_line - 1] =  veri_hierarchy_line[0 : end_main_module_hier_line - 1]
	for counter, mdl_line in enumerate(wire_mdl_line_arr):
		if counter != len(wire_mdl_line_arr) - 1:
			new_hierarchy_line[end_main_module_hier_line - 1 + counter] = mdl_line
		else:# Removing ',' from the end of the last input/output
			new_hierarchy_line[end_main_module_hier_line - 1 + counter] = ''.join([(mdl_line.split(','))[0],'\n'])
	new_hierarchy_line[end_main_module_hier_line - 1 + len(wire_mdl_line_arr) : len(veri_hierarchy_line) + end_main_module_hier_line - 1 + len(wire_mdl_line_arr)] = veri_hierarchy_line[end_main_module_hier_line - 1: len(veri_hierarchy_line)]

	with open(updated_hier_file,'w') as veri_hierarchy_file:
		veri_hierarchy_file.writelines(new_hierarchy_line)