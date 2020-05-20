#=========================================================
# functions that makes set ups for pll-gen
#	1. directory tree generation
#	2. aux cell parser
#=========================================================
import os
import sys
import argparse
import json
import shutil
import subprocess as sp

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
		hspiceModel = platformConfig['hspiceModels'] + '/toplevel.l'
		calibreRulesDir = platformConfig['calibreRules']

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
		if args.platform != 'tsmc65lp':
			print ('Error: tsmc65lp is the only platform supported')
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
#	print('run_vsim=%d'%(run_vsim))
	return specfile,platform,outputDir,pex_verify,run_vsim,outMode

#==========================================================
# 1. copies the aux files to flow/blocks/
# 2. returns the width/length of aux-cell from .lef
#==========================================================
def dco_aux_parse(flowDir,dco_CC_lib,dco_FC_lib):
	if os.path.isdir(flowDir+'blocks/'):
		print('*** '+flowDir+'blocks/ already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/')
	if os.path.isdir(flowDir+'/blocks/dco_CC/export/'):
		print('*** '+flowDir+'/blocks/dco_CC/export already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks/dco_CC')
			os.mkdir(flowDir+'/blocks/dco_CC/export/')
			print(flowDir+'/blocks/dco_CC/export/'+' generated')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/dco_CC/export/')
	if os.path.isdir(flowDir+'/blocks/dco_FC/export/'):
		print('*** '+flowDir+'/blocks/dco_FC/export already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks/dco_FC')
			os.mkdir(flowDir+'/blocks/dco_FC/export/')
			print(flowDir+'/blocks/dco_FC/export/'+' generated')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/dco_FC/export/')

	shutil.copyfile(dco_CC_lib + '/dco_CC.cdl',  flowDir + '/blocks/dco_CC/export/dco_CC.cdl')
	shutil.copyfile(dco_CC_lib + '/dco_CC.gds', flowDir + '/blocks/dco_CC/export/dco_CC.gds')
	shutil.copyfile(dco_CC_lib + '/dco_CC.lef',  flowDir + '/blocks/dco_CC/export/dco_CC.lef')
	shutil.copyfile(dco_CC_lib + '/dco_CC.lib',  flowDir + '/blocks/dco_CC/export/dco_CC.lib')

	shutil.copyfile(dco_FC_lib + '/dco_FC.cdl',  flowDir + '/blocks/dco_FC/export/dco_FC.cdl')
	shutil.copyfile(dco_FC_lib + '/dco_FC.gds', flowDir + '/blocks/dco_FC/export/dco_FC.gds')
	shutil.copyfile(dco_FC_lib + '/dco_FC.lef',  flowDir + '/blocks/dco_FC/export/dco_FC.lef')
	shutil.copyfile(dco_FC_lib + '/dco_FC.lib',  flowDir + '/blocks/dco_FC/export/dco_FC.lib')

	dco_CC_lef=open(dco_CC_lib+'dco_CC.lef','r')
	lines_CC=list(dco_CC_lef.readlines())
	inCC=0
	for line in lines_CC:
		words=line.split()
		for word in words:
			if word=='dco_CC':
				inCC=1
			if inCC==1 and word=='SIZE':
				sizes=line.split()
				W_CC=float(sizes[1])
				H_CC=float(sizes[3])

	dco_FC_lef=open(dco_FC_lib+'dco_FC.lef','r')
	lines_FC=list(dco_FC_lef.readlines())
	inFC=0
	for line in lines_FC:
		words=line.split()
		for word in words:
			if word=='dco_FC':
				inFC=1
			if inFC==1 and word=='SIZE':
				sizes=line.split()
				W_FC=float(sizes[1])
				H_FC=float(sizes[3])

	return W_CC,H_CC,W_FC,H_FC

def dir_tree(outMode,pvtGenDir,hspice,finesim,outputDir,extDir,calibreRulesDir):
	if outMode=="macro" or outMode=="full":
		hspiceDirs=['HSPICE','HSPICE/NETLIST','HSPICE/TB','HSPICE/DUMP_result','HSPICE/TBrf','HSPICE/DUMPrf_result','HSPICE/pex_NETLIST','HSPICE/pex_TB','HSPICE/pex_DUMP_result']
		if hspice==1:
			for subDir in hspiceDirs:
				Dir = os.path.join(pvtGenDir , './tsmc65lp/'+subDir)
				if os.path.isdir(Dir):
					print('*** '+Dir+' already exists')
				else:
					try:
						os.mkdir(Dir)
						print(Dir+' generated')
					except OSError:
						print('unable to create'+Dir)
		finesimDirs=['FINESIM','FINESIM/NETLIST','FINESIM/TB','FINESIM/DUMP_result','FINESIM/TBrf','FINESIM/DUMPrf_result','FINESIM/pex_NETLIST','FINESIM/pex_TB','FINESIM/pex_DUMP_result']
		if finesim==1:
			for subDir in finesimDirs:
				Dir = os.path.join(pvtGenDir , './tsmc65lp/'+subDir)
				if os.path.isdir(Dir):
					print('*** '+Dir+' already exists')
				else:
					try:
						os.mkdir(Dir)
						print(Dir+' generated')
					except OSError:
						print('unable to create'+Dir)
		extDirs=[extDir,extDir+'/run',extDir+'/sch',extDir+'/layout']
		for subDir in extDirs:
			Dir = os.path.join(pvtGenDir , './tsmc65lp/'+subDir)
			if os.path.isdir(Dir):
				print('*** '+Dir+' already exists')
			else:
				try:
					os.mkdir(Dir)
					print(Dir+' generated')
				except OSError:
					print('unable to create'+Dir)

		p=sp.Popen(['cp',calibreRulesDir+'/calibre.lvs',extDir+'/run/'])
		p.wait()
		p=sp.Popen(['cp',calibreRulesDir+'/calibre.rcx',extDir+'/run/'])
		p.wait()
	
	if outputDir!=0:
		if os.path.isdir(outputDir):
			print('*** '+outputDir+' already exists')
		else:
			try:
				os.mkdir(outputDir)
				print(outputDir+' generated')
			except OSError:
				print('unable to create'+outputDir)


