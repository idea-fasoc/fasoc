
import math
import numpy
import os


##### generate list with result data [[code_var0], [code_var1], [code_var2], ...]
##### data0 is code for capacitance
data0 = list()
r_file = open("./code_result")
mt0_data = r_file.readlines()
data_col = 1
new_list = list()
multi = 2

for line in mt0_data:
	stripped = line.strip()
	split_line=stripped.split()
	data0.append(split_line[2])
#### data1: code difference based on last code
data1 = list()
data2 = list()
i=0
last_code= data0[len(data0)-1]
for val in data0:
	i=i+1
	if val == 'failed':
		val_cal = 'failed'
	else:
		val_cal = float(val)-(float(last_code)*pow(1/float(multi),len(data0)-i))
		error =  100*(val_cal/float(val))
	data1.append(val_cal)
	data2.append(error)

r_result_list = open("./code_result", "r")
result_lines= r_result_list.readlines()
result_list = list()
i=0
print(os.getcwd())
print('ConversionTime Power CODE CODEdifference Error ')
for line in result_lines:
	result_list = result_lines[i].split()
	print('%s %s %s %s %s %s'%(result_list[0], result_list[1], result_list[2], data0[i], data1[i], data2[i]))
	i=i+1
	



