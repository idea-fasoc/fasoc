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

import csv
import pandas as pd
import os
import numpy as np
import json
from scipy.optimize import fsolve

def ML_model(original_module,csv_path,outputDir,margin_area,margin_power,previous_inputs):

	multiplier_list = [1,1.05,0.95,1.1,0.9,1.15,0.85,1.2,0.8,1.25,0.75]

	if original_module['generator'] == 'ldo-gen':
		df = pd.read_csv(os.path.join(csv_path,'ldo.csv'))
		imax_csv = df['imax']
		vin_csv = df['vin']
		area_csv = df['area']
		power_csv = df['power']

		with open(os.path.join(outputDir,original_module['module_name']+'.json')) as outGenFile:
			outGenJson = json.load(outGenFile)

		current_power = outGenJson['results']['power']
		current_area = outGenJson['results']['area']
		current_vin = outGenJson['specifications']['vin']
		current_imax = outGenJson['specifications']['imax']
		original_vin = original_module['specifications']['vin']
		original_imax = original_module['specifications']['imax']
		target_power = current_power + margin_power
		target_area = current_area + margin_area

		# -------------------------------------------------------------------------------------
		# Regarding Functionality

		acceptable_vin_list = []
		acceptable_imax_list = []
		satisfied_list = []
		results_list = []
		abs_output_diff = []
		abs_satis_input_diff = []

		for additive in [0,0.1,-0.1,0.2,-0.2]:
			if current_vin + additive <= 1.3 and current_vin + additive >= 0.6:
				acceptable_vin_list.append(current_vin + additive)

		for multiplier in multiplier_list:
			if current_imax * multiplier <= 0.019 and current_imax * multiplier >= 0.001:
				acceptable_imax_list.append(current_imax * multiplier)

		
		for vin in acceptable_vin_list:
			for imax in acceptable_imax_list:
				acceptable_inputs_tag = True
				if (vin == 0.6 and imax > 0.004) or (vin == 0.7 and imax > 0.011):
					acceptable_inputs_tag = False

				for previous_input in previous_inputs['ldo-gen']:# say it with in
					if vin == previous_input[0] and imax == previous_input[1]:
						acceptable_inputs_tag = False
						break

				if acceptable_inputs_tag:
					area = 8.057712617e+04 + -1.423940e+05*vin + 4.189547e+06*imax + 1.787496e+04*(vin**2) + -1.412762e+06*vin*imax + 4.790724e+04*(vin**3) + -1.341138e+06*(vin**2)*imax + -4.912363e+07*vin*(imax**2) + 3.292007e+03*(vin**4) + -7.892173e+03*(vin**6) + 1.442646e+05*(vin**5)*imax +  2.869955e+07*(vin**4)*(imax**2) + -5.204883e+10*(vin**2)*(imax**4) + -7.779279e+11*vin*(imax**5) + 2.295740e+14*(imax**6)
					power = 0.0009

					results_list.append([vin,imax,area,power])
					abs_output_diff.append((abs(power-target_power)/target_power)**2 + (abs(area-target_area)/target_area)**2)
					if 	area <= target_area and power <= target_power:
						satisfied_list.append([vin,imax,area,power])
						abs_satis_input_diff.append((abs(vin-original_vin)/original_vin)**2 + (abs(imax-original_imax)/original_imax)**2)

		if satisfied_list == []:
			print('no satisfication')
			if abs_output_diff == []:
				print(original_module['module_name'] + " cannot be optimized more than this")
				return outGenJson , previous_inputs , False
			else:
				optimized_func_list = np.where(abs_output_diff == np.amin(abs_output_diff))
				optimized_func_index = optimized_func_list[0][0]
				optimized_func_vin = round(results_list[optimized_func_index][0],2)
				optimized_func_imax = results_list[optimized_func_index][1]
				optimized_func_area = results_list[optimized_func_index][2]
				optimized_func_power = results_list[optimized_func_index][3]
		else:
			print('satisfication')
			optimized_func_list = np.where(abs_satis_input_diff == np.amin(abs_satis_input_diff))
			optimized_func_index = optimized_func_list[0][0]
			optimized_func_vin = round(satisfied_list[optimized_func_index][0],2)
			optimized_func_imax = satisfied_list[optimized_func_index][1]
			optimized_func_area = satisfied_list[optimized_func_index][2]
			optimized_func_power = satisfied_list[optimized_func_index][3]

		print("new specifications:")
		print("vin:")
		print(optimized_func_vin)
		print("imax:")
		print(optimized_func_imax)
		print("area:")
		print(optimized_func_area)
		print("power:")
		print(optimized_func_power)
		outGenJson["specifications"]["vin"] = optimized_func_vin
		outGenJson["specifications"]["imax"] = optimized_func_imax
		outGenJson.pop('results', None)

		previous_inputs['ldo-gen'].append([optimized_func_vin,optimized_func_imax])
		return outGenJson , previous_inputs , True

		# -------------------------------------------------------------------------------------------
	elif original_module['generator'] == 'pll-gen':
		df = pd.read_csv(os.path.join(csv_path,'pll.csv'))
		fnom_csv = df['fnom']
		area_csv = df['area']
		power_csv = df['power']

		with open(os.path.join(outputDir,original_module['module_name']+'.json')) as outGenFile:
			outGenJson = json.load(outGenFile)

		current_fnom_min = outGenJson['specifications']['Fnom_min']
		current_fnom_max = outGenJson['specifications']['Fnom_max']
		current_power = outGenJson['results']['power']
		current_area = outGenJson['results']['area']
		current_fnom = outGenJson['results']['nominal frequency']
		current_min_freq = outGenJson['results']['minimum frequency']
		current_max_freq = outGenJson['results']['maximum frequency']
		original_fnom_min = original_module['specifications']['Fnom_min']
		original_fnom_max = original_module['specifications']['Fnom_max']
		target_power = current_power + margin_power
		target_area = current_area + margin_area

		# -------------------------------------------------------------------------------------
		# Regarding Functionality

		satisfied_list = []
		results_list = []
		abs_output_diff = []
		abs_satis_input_diff = []

		multiplier = 0.8
		while(multiplier <= current_area/target_area):
			acceptable_equ_solv_tag = False
			solution_target_area = multiplier * target_area

			def equations(p):
				fnoms = p
				return(3.7442024014121142e04 + -6.846677e-05*fnoms + 2.229949e-14*fnoms**2 + 3.062494e-23*fnoms**3 + -1.706576e-50*(fnoms**6) - solution_target_area)
			fnoms = fsolve(equations, (current_fnom))
			equation_error = equations(fnoms)

			for fnom in fnoms:
				if fnom > 250e6 and fnom < 950e6 and equation_error < 0.1:
					acceptable_equ_solv_tag = True
					break

			if fnom in previous_inputs['pll-gen']:
				acceptable_equ_solv_tag = False

			if acceptable_equ_solv_tag:
				area = 3.7442024014121142e04 + -6.846677e-05*fnom + 2.229949e-14*fnom**2 + 3.062494e-23*fnom**3 + -1.706576e-50*(fnom**6)
				power = 0.032

				results_list.append([fnom,area,power])
				abs_output_diff.append(((power-target_power)/target_power)**2 + ((area-target_area)/target_area)**2)

				if area <= target_area and multiplier < 1:
					satisfied_list.append([fnom,area,power])
					if fnom < 600e6:
						fnom_min = fnom - 5e6
						fnom_max = fnom + 5e6
					else:
						fnom_min = fnom - 10e6
						fnom_max = fnom + 10e6
					abs_satis_input_diff.append(((fnom_min-original_fnom_min)/original_fnom_min)**2 + ((fnom_max-original_fnom_max)/original_fnom_max)**2)

			multiplier += 0.03

		if satisfied_list == []:
			print('no satisfication')
			if abs_output_diff == []:
				print(original_module['module_name'] + " cannot be optimized more than this")
				return outGenJson , previous_inputs , False
			else:
				optimized_func_list = np.where(abs_output_diff == np.amin(abs_output_diff))
				optimized_func_index = optimized_func_list[0][0]
				optimized_func_fnom = results_list[optimized_func_index][0]
				if optimized_func_fnom < 600e6:
					optimized_func_fnom_min = optimized_func_fnom - 5e6
					optimized_func_fnom_max = optimized_func_fnom + 5e6
				else:
					optimized_func_fnom_min = optimized_func_fnom - 10e6
					optimized_func_fnom_max = optimized_func_fnom + 10e6
				optimized_func_area = results_list[optimized_func_index][1]
				optimized_func_power = results_list[optimized_func_index][2]
		else:
			print('satisfication')
			optimized_func_list = np.where(abs_satis_input_diff == np.amin(abs_satis_input_diff))
			optimized_func_index = optimized_func_list[0][0]
			optimized_func_fnom = satisfied_list[optimized_func_index][0]
			if optimized_func_fnom < 600e6:
				optimized_func_fnom_min = optimized_func_fnom - 5e6
				optimized_func_fnom_max = optimized_func_fnom + 5e6
			else:
				optimized_func_fnom_min = optimized_func_fnom - 10e6
				optimized_func_fnom_max = optimized_func_fnom + 10e6
			optimized_func_area = satisfied_list[optimized_func_index][1]
			optimized_func_power = satisfied_list[optimized_func_index][2]

		print("new specifications:")
		print("fnom_min:")
		print(optimized_func_fnom_min)
		print("fnom_max:")
		print(optimized_func_fnom_max)
		print("area:")
		print(optimized_func_area)
		print("power:")
		print(optimized_func_power)
		outGenJson["specifications"]["Fnom_min"] = optimized_func_fnom_min
		outGenJson["specifications"]["Fnom_max"] = optimized_func_fnom_max
		outGenJson.pop('results', None)

		previous_inputs['pll-gen'].append(optimized_func_fnom)
		return outGenJson , previous_inputs , True
