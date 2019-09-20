
import re
import sys

#with open(sys.argv[1],'r') as r_mt0

file_name = sys.argv[1]
r_mt0 = open(file_name)


mt0_lines=r_mt0.readlines()


####################################################
str_list0=list()

i=0

for line in mt0_lines:
	result_pre=list()
	if i>2:
		result_pre=line.split()
		str_list0.append(result_pre)
	i=i+1


####################################################

str_list1=list()

for line in str_list0:
	result_pre2=list()
	i=0
	for val in line:
		if i<(len(line)-2):
			if float(val)>0.5:
				result_pre2.append(1.0)
			else:
				result_pre2.append(0.0)
		i=i+1	
	
	str_list1=result_pre2


code_f=0
code_r=0
code_t=0

i=0
for val in str_list1:
	if i<24:
		code_f = code_f+float(val*(2**i))
	if i>23 and i<48:
		code_r = code_r+float(val*(2**(i-24)))
	if i>47 and  i<72:
		code_t = code_t+float(val*(2**(i-48)))
	i=i+1

code_final = code_t*2-code_f-code_r

print("%s     %s      %s" %(result_pre[len(result_pre)-6], result_pre[len(result_pre)-3], code_final))


