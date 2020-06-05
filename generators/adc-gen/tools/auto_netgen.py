import sys
import os
import shutil
import string

##### Directory name for result files
genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

head_tail_0 = os.path.split(os.path.abspath(genDir))
head_tail_1 = os.path.split(head_tail_0[0])
privateGenDir = os.path.relpath(os.path.join(genDir, '../../', 'private', head_tail_1[1], head_tail_0[1]))
#ptCell = 'PT_UNIT_CELL'

flowDir = os.path.join(privateGenDir , './flow')
simDir = genDir + '../../private/generators/adc-gen/hspice/spice'
srcDir = flowDir + '/src'

tempDir = './temp'
##### number of stages
NBIT = int(sys.argv[1])

##### number of switch
nisw = int(sys.argv[2])
ncsw = int(sys.argv[3])
ncv = int(sys.argv[4])

value = []
result_out = []

value_reverse = []
result_out_reverse = []

value_reverse_v = []
result_out_reverse_v = []


## value
for i in range(0, NBIT):
	value.append("value<%s>"%i)

value = ' '.join(value)

## result_out
for i in range(0, NBIT):
	result_out.append("result_out<%s>"%i)

result_out = ' '.join(result_out)


## value reverse
for i in range(0, NBIT):
	irev = 7-(NBIT-1)+i
	value_reverse.append("value<%s>"%irev)

value_reverse = ' '.join(value_reverse)

## value reverse verilog
for i in range(0, NBIT):
	irev = 7-(NBIT-1)+i
	value_reverse_v.append("value[%s], "%irev)

value_reverse_v = ' '.join(value_reverse_v)


## result_out reverse
for i in range(0, NBIT):
	irev = 7-(NBIT-1)+i
	result_out_reverse.append("result_out<%s>"%irev)

result_out_reverse = ' '.join(result_out_reverse)


## result_out reverse verilog
for i in range(0, NBIT):
	irev = 7-(NBIT-1)+i
	result_out_reverse_v.append("result_out[%s], "%irev)

result_out_reverse_v = ' '.join(result_out_reverse_v)



## sar
inFile0 = open(genDir + "./0_spice_template/sar").read()

inFile0 = inFile0.replace('@value', value)
inFile0 = inFile0.replace('@result_out', result_out)

outFile0 = open(simDir + "/sar.cdl", "w")
outFile0.write(inFile0)
outFile0.close()



## sar verilog
inFile0_v = open(genDir + "./0_spice_template/sar.v").read()

inFile0_v = inFile0_v.replace('@NBIT', str(NBIT))

inFile0_v = inFile0_v.replace('@value_reverse_v', value_reverse_v)
inFile0_v = inFile0_v.replace('@result_out_reverse_v', result_out_reverse_v)

print(genDir)
outFile0_v = open(srcDir + "/sar.v", "w")
outFile0_v.write(inFile0_v)
outFile0_v.close()




## cdac
inFile1 = open(genDir + "./0_spice_template/cdac").read()

inFile1 = inFile1.replace('@value', value)

for i in range(0, NBIT):
	inFile1 = inFile1.replace('*bit%s '%i, '')

outFile1 = open(tempDir + "/cdac_autogen_temp", 'w')
outFile1.write(inFile1)
outFile1.close()

r_file = open(tempDir + "/cdac_autogen_temp", "r")
lines = r_file.readlines()


w_file0 = open(simDir + "/cdac.cdl", "w")

for line in lines:
	if line[0:3] == '@in':
		nline = line[4:len(line)]
		clist = list(nline)
		for i in range(0,nisw):
			for ci in range(0, len(clist)):
				if clist[ci] == '@':
					w_file0.write('_%d'%i)
				else:
					w_file0.write(clist[ci])


	elif line[0:3] == '@cv':
		nline = line[4:len(line)]
		clist = list(nline)
		for i in range(0,ncv):
			for ci in range(0, len(clist)):
				if clist[ci] == '@':
					w_file0.write('_%d'%i)
				else:
					w_file0.write(clist[ci])


	elif line[0:3] == '@cm':
		nline = line[4:len(line)]
		clist = list(nline)
		for i in range(0,ncsw):
			for ci in range(0, len(clist)):
				if clist[ci] == '@':
					w_file0.write('_%d'%i)
				else:
					w_file0.write(clist[ci])




	else:
		w_file0.write(line)

w_file0.close()

## cdac verilog
inFile1_v = open(genDir + "./0_spice_template/cdac.v").read()

inFile1_v = inFile1_v.replace('@value', value)

inFile1_v = inFile1_v.replace('@NBIT', str(NBIT))

for i in range(0, NBIT):
	inFile1_v = inFile1_v.replace('//bit%s '%i, '')

outFile1_v = open(tempDir + "/cdac_autogen_temp_v", 'w')
outFile1_v.write(inFile1_v)
outFile1_v.close()

r_file_v = open(tempDir + "/cdac_autogen_temp_v", "r")
lines = r_file_v.readlines()


w_file0_v = open(srcDir + "/cdac.v", "w")

for line in lines:
	if line[0:3] == '@in':
		nline = line[4:len(line)]
		clist = list(nline)
		for i in range(0,nisw):
			for ci in range(0, len(clist)):
				if clist[ci] == '@':
					w_file0_v.write('_%d'%i)
				else:
					w_file0_v.write(clist[ci])


	elif line[0:3] == '@cv':
		nline = line[4:len(line)]
		clist = list(nline)
		for i in range(0,ncv):
			for ci in range(0, len(clist)):
				if clist[ci] == '@':
					w_file0_v.write('_%d'%i)
				else:
					w_file0_v.write(clist[ci])


	elif line[0:3] == '@cm':
		nline = line[4:len(line)]
		clist = list(nline)
		for i in range(0,ncsw):
			for ci in range(0, len(clist)):
				if clist[ci] == '@':
					w_file0_v.write('_%d'%i)
				else:
					w_file0_v.write(clist[ci])




	else:
		w_file0_v.write(line)

w_file0_v.close()










## sar logic
inFile2 = open(genDir + "./0_spice_template/sar_logic").read()

inFile2 = inFile2.replace('@value_reverse', value_reverse)
inFile2 = inFile2.replace('@result_out_reverse', result_out_reverse)

outFile2 = open(simDir + "/sar_logic.cdl", "w")
outFile2.write(inFile2)
outFile2.close()




## dac
inFile3 = open(genDir + "./0_spice_template/dac").read()

inFile3 = inFile3.replace('@NBIT',str(NBIT))

outFile3 = open(simDir + "/dac.va", "w")
outFile3.write(inFile3)
outFile3.close()


## copy netlist
shutil.copy2(genDir + "./0_spice_template/comp_nand.cdl", simDir)
shutil.copy2(genDir + "./0_spice_template/meas_card", simDir + "/../run")
shutil.copy2(genDir + "./0_spice_template/comp_nand.v", srcDir)
shutil.copy2(genDir + "./0_spice_template/sar_logic.v", srcDir)
