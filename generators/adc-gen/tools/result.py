import numpy as np
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from numpy import array
import sys
import os

file_name = sys.argv[1]
r_file = open(file_name, "r")
lines = r_file.readlines()

file_name_parse = file_name[0:-8].split('_')

stripped_index = lines[2].strip()
index_in = stripped_index.split()
arr_index_in = np.array(index_in)

stripped_data = lines[3].strip()
data_in = stripped_data.split()

pwr = data_in[-3]

data_in = data_in[0:256]

for i in range(0,len(data_in)):
	data_in[i] = float(data_in[i])

### input data => np array conversion
fft_data_in = np.array(data_in)

### fft calculation
fft_data_complex = fft(fft_data_in)

### fft complex => real abs magnitude conversion
fft_data_abs = np.abs(fft_data_complex)

### fft abs magnitude => power spectral density conversion
fft_pden = np.square(fft_data_abs)/len(fft_data_abs)/len(fft_data_abs)

### fft plot range set ( 0~128) : 129ea
fft_pden = fft_pden[0:len(fft_pden)//2+1]

### fft => log conversion
fft_pden_log = 10*np.log10(fft_pden)

### max value find for normalization
fft_max_log=np.max(fft_pden_log[2:256])

### fft normalization to 0dB
fft_pden_log = fft_pden_log - fft_max_log

### plot fft
#plt.plot(fft_pden_log)
#plt.show()

fft_pden_sort = np.sort(fft_pden[1:])[::-1]

max_val = fft_pden_sort[0]
max_val_2nd = fft_pden_sort[1]
fft_sum = np.sum(fft_pden[1:])

sndr = 10*np.log10(max_val/(fft_sum-max_val-fft_pden[-1]/2))
enob = (sndr-1.76)/6.02
#sfdr = 10*np.log10(max_val/max_val_2nd)

#print("sndr = %f\n"%sndr)
#print("sfdr = %f\n"%sfdr)

capVal=file_name_parse[2]
widthi=file_name_parse[4]
widthc=file_name_parse[6]
fsmpl=file_name_parse[8]
nbit=file_name_parse[10]
nisw=file_name_parse[11]
ncsw=file_name_parse[12]
ncv=file_name_parse[13]

fxxx=2
fxxx_vcm=1
#remember that widthi and widthc are all number of fins, rather than actual xtor width
cap_area = 9*2*float(capVal)*1e15*float(ncv)*(2**float(nbit))
sw_input_area = float(widthi)*fxxx*float(nisw)*(2**float(nbit))
sw_vcm_area = float(widthc)*fxxx_vcm*float(ncsw)*(2**float(nbit))
logic_area = 2500

area = int(cap_area + sw_input_area + sw_vcm_area + logic_area)

print_data = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%f"%(capVal, widthi, widthc, fsmpl, nbit, nisw, ncsw, ncv, pwr, area, enob)
print(print_data)
