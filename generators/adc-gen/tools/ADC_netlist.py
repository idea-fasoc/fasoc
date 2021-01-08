import sys
import os
import shutil
import string
import time

def gen_adc_netlist(resolution_in, nisw_in, ncsw_in,simDir,genDir, platform):
	##### Directory name for result files
	dir_name = simDir + '/run'
	#dir_name2 = './hspice/run'
	
	##### Result directory generation
	#try:
	#	os.mkdir(dir_name)
	#except file_exist_error:
	#	print("Directory ", dir_name , "already exists")
	
	#try:
	#	os.mkdir(dir_name2)
	#except file_exist_error:
	#	print("Directory ", dir_name2 , "already exists")
	
	
	
	##### CDAC unit cap value
	capVal = [3.2e-15]
	for i in range(0,len(capVal)):
		capVal[i] = str(capVal[i])
	
	##### Input switch unit width
	widthi = [2]
	for i in range(0,len(widthi)):
		widthi[i] = str(widthi[i])
	
	##### VCM switch unit width
	widthc = [2]
	for i in range(0,len(widthc)):
		widthc[i] = str(widthc[i])
	
	##### Sampling speed
	fsmpl = [1.0e6]
	for i in range(0,len(fsmpl)):
		fsmpl[i] = str(fsmpl[i])
	
	##### number of bits - maximum 8bits
	#NBIT = [5]
	#for i in range(0,len(NBIT)):
	#	NBIT[i] = str(NBIT[i])
	NBIT = str(resolution_in)	

	##### number of input switch
	#nisw = [2]
	#for i in range(0,len(nisw)):
	#	nisw[i] = str(nisw[i])
	nisw = str(nisw_in)

	##### number in VCM switch
	#ncsw = [2]
	#for i in range(0,len(ncsw)):
	#	ncsw[i] = str(ncsw[i])
	ncsw = str(ncsw_in)	

	##### number of CDAC unit cap
	ncv = [1]
	for i in range(0,len(ncv)):
		ncv[i] = str(ncv[i])
	
	
	
	##### run file generation #####
	run_file = open("run_sim", "w")
	netgen_file = open("netlist_gen", "w")
	result_file = open("result_gen", "w")
	
	result_data="echo cap_val,widthi,widthc,fsmpl,nbit,nisw,ncsw,ncv,pwr,area,enob >> result_sorted\n"
	result_file.write(result_data)
	
	
	for i in range(0,len(capVal)):
		for j in range(0,len(widthi)):
			for k in range(0,len(widthc)):
				for l in range(0,len(fsmpl)):
					for ii in range(0,len(NBIT)):
						for jj in range(0,len(nisw)):
							for kk in range(0,len(ncsw)):
								for ll in range(0,len(ncv)):
									#####
									config="%s_%s_%s_%s"%(NBIT[ii],nisw[jj],ncsw[kk],ncv[ll])
									s = open("./tools/tbSar.sp").read()
									s = s.replace('@capVal', capVal[i])
									s = s.replace('@widthi', widthi[j])
									s = s.replace('@widthc', widthc[k])
									s = s.replace('@fsmpl', fsmpl[l])
									#s = s.replace('@config', config)
									
									f = open("%s/tbSar_capVal_%s_widthi_%s_widthc_%s_fsmpl_%s_config_%s.sp"%(dir_name, capVal[i], widthi[j], widthc[k], fsmpl[l], config), 'w')
									f.write(s)
									f.close()
									run_data="finesim -spice -np 4 %s/tbSar_capVal_%s_widthi_%s_widthc_%s_fsmpl_%s_config_%s.sp -o %s/tbSar_capVal_%s_widthi_%s_widthc_%s_fsmpl_%s_config_%s\n"%(dir_name, capVal[i], widthi[j], widthc[k], fsmpl[l], config, dir_name, capVal[i], widthi[j], widthc[k], fsmpl[l], config)
									run_file.write(run_data)
	
									result_data="python ./tools/result.py %s/tbSar_capVal_%s_widthi_%s_widthc_%s_fsmpl_%s_config_%s.mt0 >> result_sorted\n"%(dir_name, capVal[i], widthi[j], widthc[k], fsmpl[l], config)
									result_file.write(result_data)
	
									netgen_data="python" +" %stools/auto_netgen.py %s %s %s %s %s\n"%(genDir,NBIT[ii],nisw[jj],ncsw[kk],ncv[ll], platform)
									netgen_file.write(netgen_data)
	
									#####
	run_file.close()
	netgen_file.close()
	result_file.close()
	
	os.chmod("run_sim",0o777)
	os.chmod("netlist_gen",0o777)
	os.chmod("result_gen",0o777)
	
	time.sleep(2)
	
	os.system("./netlist_gen")

