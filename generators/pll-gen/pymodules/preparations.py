#=========================================================
# preparing for the flows
#	1. parse command line
#	2. parse configurations  
#	3. directory tree generation
#	4. parse aux cells
#=========================================================
import os
import sys
import argparse
import json
import shutil
import subprocess as sp
import txt_mds
import glob

def config_parse(outMode,configFile,platform):
	print ('#----------------------------------------------------------------------')
	print ('#Loading platform_config file...')
	print ('#----------------------------------------------------------------------')
	try:
	  with open(configFile) as file:
	    jsonConfig = json.load(file)
	except ValueError as e:
	  print ('Error occurred opening or loading json file.')
	  sys.exit(1)

	# Define the config & design variables
	aLib=''

	# Get the config variable from platfom config file
	simTool = jsonConfig['simTool']
	if simTool != 'hspice':
	   print ('Error: Only support hspice simulator now')
	   sys.exit(1)

	extTool = jsonConfig['extractionTool']
	if extTool != 'calibre':
	   print ('Error: Only support calibre extraction now')
	   sys.exit(1)

	netlistTool = jsonConfig['netlistTool']
	if netlistTool != 'calibredrv':
	   print ('Error: Only support calibredrv netlist tool now')
	   sys.exit(1)

	try:
	   platformConfig = jsonConfig['platforms'][platform]
	except ValueError as e:
	   print ('Error: \"' + platform + '\" config not available')
	   sys.exit(1)

	aLib = 'placeHolder' 
	hspiceModel = 'placeHolder'
	calibreRulesDir = 'placeHolder'
	if outMode=='full' or outMode=='macro':
		aLib = platformConfig['aux_lib']
		if platform=='tsmc65lp':
			hspiceModel = platformConfig['hspiceModels'] + '/toplevel.l'
		if platform=='gf12lp':
			hspiceModel = platformConfig['hspiceModels'] + '/12LP_Hspice.lib'
		calibreRulesDir = platformConfig['calibreRules']
		if aLib=='placeHolder':
			print('Error: aux-cell lib is not properly read')
			sys.exit(1)	
		if hspiceModel=='placeHolder':
			print('Error: hspiceModel is not properly read')
			sys.exit(1)	
		if calibreRulesDir=='placeHolder':
			print('Error: calibre rules directory is not properly read')
			sys.exit(1)	

	mFile = platformConfig['model_lib'] + '/pll_model.json'


	return aLib,mFile,calibreRulesDir,hspiceModel



def command_parse(parseList):
	[specFile,platForm,outDir,pexVerify,runVsim,mode]=parseList
	print ('#----------------------------------------------------------------------')
	print ('# Parsing command line arguments...')
	print ('#----------------------------------------------------------------------')
	print (sys.argv)

	parser = argparse.ArgumentParser(description='All Digital PLL design generator')
	if specFile==1:
		parser.add_argument('--specfile', required=True,
		                    help='File containing the specification for the generator')
	if outDir==1:
		parser.add_argument('--outputDir', required=True,
		                    help='Output directory for generator results')
	if platForm==1:
		parser.add_argument('--platform', required=True,
		                    help='PDK/process kit for cadre flow (.e.g tsmc16)')
	if pexVerify==1:
		parser.add_argument('--pex_verify', required=False, default=False,
		                    help='whether or not to run pex sim for verification(takes more than a day with 4 cores)')
	if runVsim==1:
		parser.add_argument('--run_vsim', required=False, default=False,
		                    help='whether or not to run verilog sim for controller function verification(takes about 5mins)')
	#---determine the output level: verilog/macro/full---
	if mode==1:
		parser.add_argument('--mode', required=False, default=False,
		                    help='output level: verilog/macro/full')
	args = parser.parse_args()


	specfile=0
	platform=0
	outputDir=0
	pex_verify=0
	run_vsim=0
	outMode=0
	if specFile==1:
		if not os.path.isfile(args.specfile):
			print ('Error: specfile does not exist')
			print ('File Path: ' + args.specfile)
			sys.exit(1)
		specfile=args.specfile
	if platForm==1:
		if args.platform != 'tsmc65lp' and args.platform != 'gf12lp' :
			print ('Error: tsmc65lp and gf12lp are the only supported platforms, received platform: '+args.platform)
			sys.exit(1)
		platform=args.platform
	if outDir==1:
		outputDir=args.outputDir
	if pexVerify==1:
		pex_verify=int(args.pex_verify)
	if runVsim==1:
		run_vsim=int(args.run_vsim)
	#---determine the output level: verilog/macro/full---
	if mode==1:
		outMode=args.mode

	return specfile,platform,outputDir,pex_verify,run_vsim,outMode


def aux_copy_spice (dco_CC_lib, dco_FC_lib, targetDir):
	try:
		for CC_sp in glob.glob(dco_CC_lib+'*.sp'):
			shutil.copy(CC_sp,  targetDir + '/')
	except:
		print("failed to copy "+ dco_CC_lib + '/DCO_CC.sp to ' +  targetDir + '/DCO_CC.sp')
		sys.exit(1)
	try:
		for FC_sp in glob.glob(dco_FC_lib+'*.sp'):
			shutil.copy(FC_sp,  targetDir + '/')
	except:
		print("failed to copy "+ dco_FC_lib + '/DCO_FC.sp to ' +  targetDir + '/DCO_FC.sp')
		sys.exit(1)
	
#==========================================================
# 1. copies the aux files to flow/blocks/
#==========================================================
def aux_copy_export(flowDir,dco_CC_lib,dco_FC_lib):
	print ('#----------------------------------------------------------------------')
	print ('# Parsing DCO aux-cells dimensions and generating blocks/ directory in '+flowDir)
	print ('#----------------------------------------------------------------------')
	dco_CC_lib_spt=dco_CC_lib.split("/")
	dco_CC_name=dco_CC_lib_spt[len(dco_CC_lib_spt)-3]
	dco_FC_lib_spt=dco_FC_lib.split("/")
	dco_FC_name=dco_FC_lib_spt[len(dco_FC_lib_spt)-3]
	if os.path.isdir(flowDir+'blocks/'):
		print('INFO: '+flowDir+'blocks/ already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/')
	if os.path.isdir(flowDir+'/blocks/'+dco_CC_name+'/export/'):
		print('INFO: '+flowDir+'/blocks/'+dco_CC_name+'/export already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks/'+dco_CC_name)
			os.mkdir(flowDir+'/blocks/'+dco_CC_name+'/export/')
			print(flowDir+'/blocks/'+dco_CC_name+'/export/'+' generated')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/'+dco_CC_name+'/export/')
	if os.path.isdir(flowDir+'/blocks/'+dco_FC_name+'/export/'):
		print('INFO: '+flowDir+'/blocks/'+dco_FC_name+'/export already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks/'+dco_FC_name)
			os.mkdir(flowDir+'/blocks/'+dco_FC_name+'/export/')
			print(flowDir+'/blocks/'+dco_FC_name+'/export/'+' generated')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/'+dco_FC_name+'/export/')

	try:
		for CC_file in os.listdir(dco_CC_lib):
			print("INFO: copying aux-cell file:"+dco_CC_lib+CC_file)
			shutil.copy(dco_CC_lib+CC_file,flowDir+'blocks/'+dco_CC_name+'/export/')
#		shutil.copyfile(dco_CC_lib + '/dco_CC.cdl',  flowDir + '/blocks/dco_CC/export/dco_CC.cdl')
#		shutil.copyfile(dco_CC_lib + '/dco_CC.gds', flowDir + '/blocks/dco_CC/export/dco_CC.gds')
#		shutil.copyfile(dco_CC_lib + '/dco_CC.lef',  flowDir + '/blocks/dco_CC/export/dco_CC.lef')
#		shutil.copyfile(dco_CC_lib + '/dco_CC.lib',  flowDir + '/blocks/dco_CC/export/dco_CC.lib')
		for FC_file in os.listdir(dco_FC_lib):
			shutil.copy(dco_FC_lib+FC_file,flowDir+'blocks/'+dco_FC_name+'/export/')

		#shutil.copyfile(dco_FC_lib + '/dco_FC.cdl',  flowDir + '/blocks/dco_FC/export/dco_FC.cdl')
		#shutil.copyfile(dco_FC_lib + '/dco_FC.gds', flowDir + '/blocks/dco_FC/export/dco_FC.gds')
		#shutil.copyfile(dco_FC_lib + '/dco_FC.lef',  flowDir + '/blocks/dco_FC/export/dco_FC.lef')
		#shutil.copyfile(dco_FC_lib + '/dco_FC.lib',  flowDir + '/blocks/dco_FC/export/dco_FC.lib')
	except OSError:
		print('Error: unable to copy aux-cell files in '+flowDir+'/blocks/')
		sys.exit(1)
	return dco_CC_name, dco_FC_name

def aux_parse_size(dco_CC_lib,dco_FC_lib):
	dco_CC_lib_spt=dco_CC_lib.split("/")
	dco_CC_name=dco_CC_lib_spt[len(dco_CC_lib_spt)-3]
	dco_FC_lib_spt=dco_FC_lib.split("/")
	dco_FC_name=dco_FC_lib_spt[len(dco_FC_lib_spt)-3]

	print("INFO: dco coarse cell name is:"+dco_CC_name)
	print("INFO: dco fine cell name is:"+dco_FC_name)
	for CC_lef in glob.glob(dco_CC_lib+'*.lef'):
		dco_CC_lef=open(CC_lef,'r')
#	dco_CC_lef=open(dco_CC_lib+'dco_CC.lef','r')
	lines_CC=list(dco_CC_lef.readlines())
	inCC=0
	for line in lines_CC:
		words=line.split()
		for word in words:
			if word==dco_CC_name:
				inCC=1
			if inCC==1 and word=='SIZE':
				sizes=line.split()
				W_CC=float(sizes[1])
				H_CC=float(sizes[3])

	for FC_lef in glob.glob(dco_FC_lib+'*.lef'):
		dco_FC_lef=open(FC_lef,'r')
	#dco_FC_lef=open(dco_FC_lib+'dco_FC.lef','r')
	lines_FC=list(dco_FC_lef.readlines())
	inFC=0
	for line in lines_FC:
		words=line.split()
		for word in words:
			if word==dco_FC_name:
				inFC=1
			if inFC==1 and word=='SIZE':
				sizes=line.split()
				W_FC=float(sizes[1])
				H_FC=float(sizes[3])

	return W_CC,H_CC,W_FC,H_FC

def gen_subDirs (subDirs):
	for subDir in subDirs:
		if os.path.isdir(subDir):
			print('INFO: '+subDir+' already exists')
		else:
			try:
				os.mkdir(subDir)
				print(subDir+' generated')
			except OSError:
				print('unable to create'+Dir)
				sys.exit(1)

def dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform):
	if outMode=="macro" or outMode=="full":
		gen_subDirs([absPvtDir_plat])

		hspiceDirs=[hspiceDir,hspiceDir+'/NETLIST',hspiceDir+'/TB',hspiceDir+'/DUMP_result',hspiceDir+'/TBrf',hspiceDir+'/DUMPrf_result',hspiceDir+'/pex_NETLIST',hspiceDir+'/pex_TB',hspiceDir+'/pex_DUMP_result',hspiceDir+'/pex_NETLIST_scs',hspiceDir+'/pex_TB_scs',hspiceDir+'/pex_DUMP_result_scs']
		gen_subDirs(hspiceDirs)

		finesimDirs=[finesimDir,finesimDir+'/NETLIST',finesimDir+'/TB',finesimDir+'/DUMP_result',finesimDir+'/TBrf',finesimDir+'/DUMPrf_result',finesimDir+'/pex_NETLIST',finesimDir+'/pex_TB',finesimDir+'/pex_DUMP_result']
		gen_subDirs(finesimDirs)

		extDirs=[extDir,extDir+'/run',extDir+'/run_scs',extDir+'/sch',extDir+'/layout',extDir+'/runsets']
		gen_subDirs(extDirs)

		p=sp.Popen(['cp',calibreRulesDir+'/calibre.lvs',extDir+'/run/'])
		p.wait()
		p=sp.Popen(['cp',calibreRulesDir+'/calibre.rcx',extDir+'/run/'])
		p.wait()
		
		dco_flowDirs=[dco_flowDir,dco_flowDir+'/src',dco_flowDir+'/scripts',dco_flowDir+'/scripts/innovus',dco_flowDir+'/scripts/dc']
		gen_subDirs(dco_flowDirs)
	
		outbuff_div_flowDirs=[outbuff_div_flowDir]
		gen_subDirs(outbuff_div_flowDirs)

		pll_flowDirs=[pll_flowDir,pll_flowDir+'/src',pll_flowDir+'/scripts',pll_flowDir+'/scripts/innovus',pll_flowDir+'/scripts/dc']
		gen_subDirs(pll_flowDirs)

	if outputDir!=0:
		gen_subDirs([outputDir])

def dir_tree_genus(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform):
	if outMode=="macro" or outMode=="full":
		gen_subDirs([absPvtDir_plat])

		dco_flowDirs=[dco_flowDir,dco_flowDir+'/src',dco_flowDir+'/scripts',dco_flowDir+'/scripts/innovus',dco_flowDir+'/scripts/genus']
		gen_subDirs(dco_flowDirs)

	if outputDir!=0:
		gen_subDirs([outputDir])
