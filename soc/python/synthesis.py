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

import shutil	# filesystem manipulation
import os	# filesystem manipulation
import json	# json parsing
import subprocess	# process
import re

def synthesis (designJson,designName,socVerilogDir,m0_module_name,m0_instance_name,synthDir,filelistDir):

# Adding socrates output verilog file parameters
# ==============================================================================
	if "parameters" in designJson:
		param_line = ""
		if "`include" in designJson["parameters"]:
			for parameter_name in designJson["parameters"]:
				if parameter_name == "`include":
					param_line = param_line + parameter_name + " \"" + designJson["parameters"][parameter_name] + "\"\n"
		param_line = param_line + "module " + designName + " #(\n"

		for counter, parameter_name in enumerate(designJson["parameters"]):
			if parameter_name != "`include":
				if counter != len(designJson["parameters"]) - 1:
					if not isinstance(designJson["parameters"][parameter_name],list):
						param_line = param_line + "parameter " + parameter_name + " = " + str(designJson["parameters"][parameter_name]) + ",\n"
					else:
						for parameter_dict in designJson["parameters"][parameter_name]:
							for parameter_dict_item in parameter_dict:
								if parameter_dict_item == "value":
									param_line = param_line + "parameter " + parameter_name + " = " + str(parameter_dict[parameter_dict_item]) + ",\n"
								elif parameter_dict_item == "`ifdef":
									param_line = param_line + parameter_dict_item + " " + str(parameter_dict[parameter_dict_item]) + "\n"
								elif (parameter_dict_item == "`endif" or parameter_dict_item == "`else"):
									param_line = param_line + parameter_dict_item + "\n"
				else:
					param_line = param_line + "parameter " + parameter_name + " = " + str(designJson["parameters"][parameter_name]) + "\n"
		param_line = param_line + ")"
			
		with open(socVerilogDir, "r") as socrates_verilog:
			soc_ver = socrates_verilog.read()
		soc_ver = soc_ver.replace("module " + designName, param_line)
		with open(socVerilogDir, 'w') as socrates_verilog:
			socrates_verilog.write(soc_ver)

# Copying the associated verilog files and rename them and change their module name, and adding/changing create_clock for plls to constraints.tcl
# ================================================================================================================================================
	src_module_verilogDir = os.path.join("/afs","eecs.umich.edu","cadre","projects","fasoc","share","integration_tool","verilog")
	constraintsDir = os.path.join(synthDir,"scripts","dc","constraints.tcl")
	vco_period_pat = r'set VCO_PERIOD'
	previous_create_clock_added = 0

	for module in designJson["modules"]:

# constraints.tcl modifications
		if module["generator"] == "pll-gen":
			with open(constraintsDir, 'r') as constraints_file:
				constraints_lines = constraints_file.readlines()
			for line_no, line in enumerate(constraints_lines):

				set_dont_touch_pat = r'set_dont_touch \[get_cells (\S+)/u_pin_mux/IO_\*\]'
				m0_initial_instance_names = re.findall(set_dont_touch_pat,line)
				if len(m0_initial_instance_names) != 0:
					m0_initial_instance_name = m0_initial_instance_names[0]
				if re.match(vco_period_pat,line):
					create_clock_line_no = line_no + previous_create_clock_added
			new_constraints_line = [None] * (len(constraints_lines) + 6)
			new_constraints_line[0 : create_clock_line_no + 1] =  constraints_lines[0 : create_clock_line_no + 1]
			new_constraints_line[create_clock_line_no + 1] = "create_clock [get_pins " + module["instance_name"] + "/synth_pll/CLK_OUT] \\\n"
			new_constraints_line[create_clock_line_no + 2] = "             -name CLK_OUT \\\n"
			new_constraints_line[create_clock_line_no + 3] = "             -period $VCO_PERIOD\n"
			new_constraints_line[create_clock_line_no + 4] = "create_clock [get_pins " + module["instance_name"] + "/synth_pll/CLKREF_RETIMED_1] \\\n"
			new_constraints_line[create_clock_line_no + 5] = "             -name CLK_OUT \\\n"
			new_constraints_line[create_clock_line_no + 6] = "             -period $VCO_PERIOD\n"
			new_constraints_line[create_clock_line_no + 7 : len(constraints_lines) + 6] =  constraints_lines[create_clock_line_no + 1 : len(constraints_lines)]
			previous_create_clock_added = previous_create_clock_added + 6
			with open(constraintsDir,'w') as constraints_file:
				constraints_file.writelines(new_constraints_line)

# verilog files modifications
		if module["generator"] == "memory-gen":
			dst_module_verilogDir = os.path.join(synthDir,"src","mem",module["module_name"] + ".v")
		elif module["generator"] == "cmsdk_apb_slave_mux_rtl":
			try:
				os.makedirs(os.path.join(synthDir,"m0sdk","logical",module["module_name"],"verilog")) 
			except FileExistsError:
				if len(os.listdir(os.path.join(synthDir,"m0sdk","logical",module["module_name"],"verilog"))) != 0:
					for file in os.listdir(os.path.join(synthDir,"m0sdk","logical",module["module_name"],"verilog")):
						os.remove(os.path.join(os.path.join(synthDir,"m0sdk","logical",module["module_name"],"verilog"),file))
			dst_module_verilogDir = os.path.join(synthDir,"m0sdk","logical",module["module_name"],"verilog",module["module_name"] + ".v")
		elif module["generator"] == "m0mcu_rtl":
			dst_module_verilogDir = os.path.join(synthDir,"m0sdk","systems","cortex_m0_mcu","verilog",module["module_name"] + ".v")
		else:
			dst_module_verilogDir = os.path.join(synthDir,"src",module["module_name"] + ".v")
		shutil.copy(os.path.join(src_module_verilogDir,module["generator"] + ".v"),dst_module_verilogDir)
		
		with open(dst_module_verilogDir, "r") as dst_module_verilog:
			dst_module_ver = dst_module_verilog.read()
		if "rtl" in module["generator"]:
			if module["generator"] != "ldo_mux_rtl":
				dst_module_ver = dst_module_ver.replace("module " + module["generator"] + " #(", "module " + module["module_name"] + " #(")
			else:
				dst_module_ver = dst_module_ver.replace("module " + module["generator"] + " (", "module " + module["module_name"] + " (")
		else:
			if module["generator"] != "temp-sense-gen":
				initial_module_name = (module["generator"].split("-gen"))[0] + "_gen"
			else:
				initial_module_name = "temp_sense_gen"
			dst_module_ver = dst_module_ver.replace("module " + initial_module_name + " #(", "module " + module["module_name"] + " #(")
		with open(dst_module_verilogDir, 'w') as dst_module_verilog:
				dst_module_verilog.write(dst_module_ver)

# Adding generators parameters to socrates output verilog file
# =================================================================================
		if "parameters" in module:
			param_line = module["module_name"] + " #(\n"
			for counter, parameter_name in enumerate(module["parameters"]):
				if counter != len(module["parameters"]) - 1:
					if not isinstance(module["parameters"][parameter_name],list):
						param_line = param_line + "." + parameter_name + " (" + str(module["parameters"][parameter_name]) + "),\n"
					else:
						for parameter_dict in module["parameters"][parameter_name]:
							for parameter_dict_item in parameter_dict:
								if parameter_dict_item == "value":
									param_line = param_line + "." + parameter_name + " (" + str(parameter_dict[parameter_dict_item]) + "),\n"
								elif parameter_dict_item == "`ifdef":
									param_line = param_line + parameter_dict_item + " " + str(parameter_dict[parameter_dict_item]) + "\n"
								elif (parameter_dict_item == "`endif" or parameter_dict_item == "`else"):
									param_line = param_line + parameter_dict_item + "\n"
				else:
					param_line = param_line + "." + parameter_name + " (" + str(module["parameters"][parameter_name]) + ")\n"
			param_line = param_line + ")" + module["instance_name"]
			
			with open(socVerilogDir, "r") as socrates_verilog:
				soc_ver = socrates_verilog.read()
			soc_ver = soc_ver.replace(module['module_name'] + " " + module['instance_name'], param_line)
			with open(socVerilogDir, 'w') as socrates_verilog:
				socrates_verilog.write(soc_ver)

# Adding ifdef to input/output ports (in overal input/output, m0 instantiation, and assignment) to socrates output verilog file
# ==============================================================================================================================
	ifdef_port_dict = {"nTRST":["in", "ARM_CMSDK_INCLUDE_JTAG"],"TDI":["in", "ARM_CMSDK_INCLUDE_JTAG"],"TDO":["out","ARM_CMSDK_INCLUDE_JTAG"]}
	m0_start_pat = rf'{m0_module_name} #\('
	m0_end_pat = r'\s*\);'
	end_module_list = []
	new_soc_ver_lines = []
	m0_corres_port_dict = {}
	assign_corres_port_dict = {}

	with open(socVerilogDir, 'r') as socrates_verilog:
		outVer_lines = socrates_verilog.readlines()

	for line_no, line in enumerate(outVer_lines):
		if re.match(m0_start_pat,line):
			m0_start_line_no = line_no
		if re.search(m0_end_pat,line) != None:
			end_module_list.append(line_no)
	m0_end_line_no = end_module_list[list(map(lambda i: i > m0_start_line_no, end_module_list)).index(True)]
	
	for line_no, line in enumerate(outVer_lines):
		for ifdef_port in ifdef_port_dict:
			if (m0_start_line_no < line_no and m0_end_line_no > line_no):
				m0_pat = rf'.{ifdef_port} \((\S+)\)'
				m0_corres_port = re.findall(m0_pat,line)
				if m0_corres_port != []:
					m0_corres_port_dict[ifdef_port] = m0_corres_port[0]
					initial_m0_line = rf'\s*.{ifdef_port} \({m0_corres_port_dict[ifdef_port]}\)\s*,'
					final_m0_line = "    `ifdef " + ifdef_port_dict[ifdef_port][1] + "\n" + "    ." + ifdef_port + " (" + m0_corres_port_dict[ifdef_port] + "),\n" + "    `endif"
					line = re.sub(initial_m0_line,final_m0_line,line)

			if ifdef_port_dict[ifdef_port][0] == "in":
				initial_input_line = rf'\s*input\s+{ifdef_port}\s*,'
				final_input_line = "`ifdef " + ifdef_port_dict[ifdef_port][1] + "\n" + "  input          " + ifdef_port + ",\n" + "`endif"
				line = re.sub(initial_input_line,final_input_line,line)

				if m0_end_line_no < line_no:
					initial_assign_line = rf'\s*assign {m0_corres_port_dict[ifdef_port]} = {ifdef_port};'
					final_assign_line = "`ifdef " + ifdef_port_dict[ifdef_port][1] + "\n" + "assign " + m0_corres_port_dict[ifdef_port] + " = " + ifdef_port + ";\n" + "`endif"
					line = re.sub(initial_assign_line,final_assign_line,line)

			elif ifdef_port_dict[ifdef_port][0] == "out":
				initial_input_line = rf'\s*output\s+{ifdef_port}\s*,'
				final_input_line = "`ifdef " + ifdef_port_dict[ifdef_port][1] + "\n" + "  output          " + ifdef_port + ",\n" + "`endif"
				line = re.sub(initial_input_line,final_input_line,line)

				assign_pat = rf'\s*assign {ifdef_port} = (\S+);'
				assign_corres_port = re.findall(assign_pat,line)
				if assign_corres_port != []:
					assign_corres_port_dict[ifdef_port] = assign_corres_port[0]
					initial_assign_line = rf'\s*assign {ifdef_port} = {assign_corres_port_dict[ifdef_port]};'
					final_assign_line = "`ifdef " + ifdef_port_dict[ifdef_port][1] + "\n" + "assign " + ifdef_port + " = " + assign_corres_port_dict[ifdef_port] + ";\n" + "`endif"
					line = re.sub(initial_assign_line,final_assign_line,line)
		new_soc_ver_lines.append(line)
	
	with open(socVerilogDir, 'w') as socrates_verilog:
		socrates_verilog.writelines(new_soc_ver_lines)

# Change design name in include.mk and dc.read_design.tcl
# ==============================================================================================================================
	includeDir =  os.path.join(synthDir,"include.mk")
	read_designDir =  os.path.join(synthDir,"scripts","dc","dc.read_design.tcl")
	new_include_lines = []
	new_read_design_lines = []

	with open(includeDir, 'r') as include_file, open(read_designDir, 'r') as read_design_file:
		include_lines = include_file.readlines()
		read_design_lines = read_design_file.readlines()

	for line in include_lines:
		design_name_pat = rf'\s*export DESIGN_NAME := (\S+)'
		initial_design_name = re.findall(design_name_pat,line)
		if initial_design_name != []:
			initial_design_line = rf'\s*export DESIGN_NAME := {initial_design_name[0]}'
			final_design_line = "export DESIGN_NAME := " + designName
			line = re.sub(initial_design_line,final_design_line,line)
		new_include_lines.append(line)

	for line in read_design_lines:
		elaborate_pat = rf'\s*elaborate (\S+)'
		initial_elaborate = re.findall(elaborate_pat,line)
		if initial_elaborate != []:
			initial_elaborate_line = rf'\s*elaborate {initial_elaborate[0]}'
			final_elaborate_line = "elaborate " + designName
			line = re.sub(initial_elaborate_line,final_elaborate_line,line)
		new_read_design_lines.append(line)

	with open(includeDir, 'w') as include_file, open(read_designDir, 'w') as read_design_file:
		include_file.writelines(new_include_lines)
		read_design_file.writelines(new_read_design_lines)

# Change filelist.tcl file's name and contents of constraints.tcl
# ==============================================================================================================================
	shutil.copy(filelistDir,os.path.join(synthDir,"scripts","dc","dc.filelist.tcl"))
	
	with open(constraintsDir, 'r') as constraints_file:
		constraints_f = constraints_file.read()
	constraints_f = constraints_f.replace("set_dont_touch [get_cells " + m0_initial_instance_name + "/u_pin_mux/IO_*]", "set_dont_touch [get_cells " + m0_instance_name + "/u_pin_mux/IO_*]")
	constraints_f = constraints_f.replace("set_dont_touch  [get_pins " + m0_initial_instance_name + "/u_pin_mux/PLL_CLKOUT*]", "set_dont_touch  [get_pins " + m0_instance_name + "/u_pin_mux/PLL_CLKOUT*]")
	constraints_f = constraints_f.replace("set_dont_touch  [get_pins " + m0_initial_instance_name + "/u_pin_mux/PLL_CLKREF*]", "set_dont_touch  [get_pins " + m0_instance_name + "/u_pin_mux/PLL_CLKREF*]")
	constraints_f = constraints_f.replace("set_dont_touch  [get_nets " + m0_initial_instance_name + "/u_pin_mux/pll_clkref*]", "set_dont_touch  [get_nets " + m0_instance_name + "/u_pin_mux/pll_clkref*]")
	constraints_f = constraints_f.replace("set_dont_touch  [get_cells " + m0_initial_instance_name + "/u_pin_mux/pll_clkref*]", "set_dont_touch  [get_cells " + m0_instance_name + "/u_pin_mux/pll_clkref*]")
	constraints_f = constraints_f.replace("set_dont_touch  [get_nets " + m0_initial_instance_name + "/u_pin_mux/LDO_VREF*]", "set_dont_touch  [get_nets " + m0_instance_name + "/u_pin_mux/LDO_VREF*]")
	constraints_f = constraints_f.replace("set_dont_touch  [get_nets " + m0_initial_instance_name+ "/u_pin_mux/VIN_TEMPSENSE*]", "set_dont_touch  [get_nets " + m0_instance_name + "/u_pin_mux/VIN_TEMPSENSE*]")
	with open(constraintsDir, 'w') as constraints_file:
		constraints_file.write(constraints_f)