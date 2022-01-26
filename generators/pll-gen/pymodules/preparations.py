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

	if platform=='tsmc65lp':
		mFile = platformConfig['model_lib'] + '/pll_model.json'
	elif platform=='gf12lp':
		mFile = platformConfig['model_lib'] + '/pll_pex_model_gf12lp_FCv2.json'


	return aLib,mFile,calibreRulesDir,hspiceModel



def command_parse(parseList):
	[specFile,platForm,outDir,pexVerify,runVsim,mode,synth_tool,track]=parseList
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
	if synth_tool==1:
		parser.add_argument('--synth_tool', required=False, default=False,
		                    help='supported synth tool: dc or genus')
	if track==1:
		parser.add_argument('--track', required=False, default=False,
		                    help='gf12lp: 9 or 10.5, tsmc65lp: 9')
	args = parser.parse_args()


	specfile=0
	platform=0
	outputDir=0
	pex_verify=0
	run_vsim=0
	outMode=0
	synthTool='dc'
	Track=0
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
	if synth_tool==1:
		synthTool=args.synth_tool
	if track==1:
		Track=float(args.track)

	return specfile,platform,outputDir,pex_verify,run_vsim,outMode,synthTool,Track


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
				print('unable to create '+Dir)
				sys.exit(1)

def dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform, vsimDir):
	# verilog sim
	vsimDirs_list = [vsimDir, vsimDir+'/verilog',vsimDir+'/aprVerilog']
	gen_subDirs(vsimDirs_list)

	if outMode=="macro" or outMode=="full":
		gen_subDirs([absPvtDir_plat])

		hspiceDirs_split = hspiceDir.split("/")

		hspiceDirs_pol = hspiceDirs_split[1:len(hspiceDirs_split)-1]

		hspiceDirs_pol2 = []
		Dir_accum = hspiceDirs_pol[0] 
		for cnt in range(len(hspiceDirs_pol)):
			if cnt==0:
				Dir_accum = '/'+hspiceDirs_pol[0] 
			else:	
				Dir_accum = Dir_accum + "/" + hspiceDirs_pol[cnt] 
			hspiceDirs_pol2.append(Dir_accum) 

		print(hspiceDirs_pol2)
		gen_subDirs(hspiceDirs_pol2)

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
	
		dco_flowDirs=[dco_flowDir,dco_flowDir+'/src',dco_flowDir+'/scripts',dco_flowDir+'/scripts/innovus',dco_flowDir+'/scripts/dc',dco_flowDir+'/scripts/genus']
		gen_subDirs(dco_flowDirs)
	
		outbuff_div_flowDirs=[outbuff_div_flowDir]
		gen_subDirs(outbuff_div_flowDirs)

		pll_flowDirs=[pll_flowDir,pll_flowDir+'/src',pll_flowDir+'/scripts',pll_flowDir+'/scripts/innovus',pll_flowDir+'/scripts/dc',pll_flowDir+'/scripts/genus']
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

def read_ble_params(dp_json):
	print ('#----------------------------------------------------------------------')
	print ('# Loading ' +dp_json+ ' design parameter file...')
	print ('#----------------------------------------------------------------------')
	try:
	  with open(dp_json) as file:
	    jsonParam = json.load(file)
	except ValueError as e:
	  print ('Error occurred opening or loading json file.')
	  sys.exit(1)

	# Get the config variable from platfom config file
	buf8x_name    = jsonParam["std_cell_names"]["buf8x_name"]
	buf2x_name    = jsonParam["std_cell_names"]["buf2x_name"]
	buf4x_name    = jsonParam["std_cell_names"]["buf4x_name"]
	buf10x_name   = jsonParam["std_cell_names"]["buf10x_name"]
	dff_name      = jsonParam["std_cell_names"]["dff_name"]
	inv0p6x_name  = jsonParam["std_cell_names"]["inv0p6x_name"]
	buf16x_name   = jsonParam["std_cell_names"]["buf16x_name"]
	buf14x_name   = jsonParam["std_cell_names"]["buf14x_name"]
	embtdc_dff_name=jsonParam["std_cell_names"]["embtdc_dff_name"]
	xnor2_0p6_name =jsonParam["std_cell_names"]["xnor2_0p6_name"]
	dffrpq_3x_name =jsonParam["std_cell_names"]["dffrpq_3x_name"]

	nstg    =jsonParam["dco_design_params"]["nstg"]
	ndrv    =jsonParam["dco_design_params"]["ndrv"]
	ncc     =jsonParam["dco_design_params"]["ncc"]
	nfc     =jsonParam["dco_design_params"]["nfc"]
	ncc_dead=jsonParam["dco_design_params"]["ncc_dead"]

	pre_ls_ref_nstg_cc_tune =jsonParam["tstdc_counter_design_params"]["pre_ls_ref_nstg_cc_tune"]
	pre_ls_ref_ncc_tune     =jsonParam["tstdc_counter_design_params"]["pre_ls_ref_ncc_tune"]
	pre_ls_ref_nfc          =jsonParam["tstdc_counter_design_params"]["pre_ls_ref_nfc"]
	dltdc_num_ph            =jsonParam["tstdc_counter_design_params"]["dltdc_num_ph"]
	dltdc_nfc               =jsonParam["tstdc_counter_design_params"]["dltdc_nfc"]
	dltdc_ndrv              =jsonParam["tstdc_counter_design_params"]["dltdc_ndrv"]
	dltdc_ncc               =jsonParam["tstdc_counter_design_params"]["dltdc_ncc"]
	pre_nstg_ref_ls         =jsonParam["tstdc_counter_design_params"]["pre_nstg_ref_ls"]
	pre_nstg_ref            =jsonParam["tstdc_counter_design_params"]["pre_nstg_ref"]
	pre_nstg_fb             =jsonParam["tstdc_counter_design_params"]["pre_nstg_fb"]
	ppath_nstg              =jsonParam["tstdc_counter_design_params"]["ppath_nstg"]
	pre_ls_ref_nstg         =jsonParam["tstdc_counter_design_params"]["pre_ls_ref_nstg"]
	post_ls_ref_nstg        =jsonParam["tstdc_counter_design_params"]["post_ls_ref_nstg"]
	post_ls_ref_nstg_cc_tune=jsonParam["tstdc_counter_design_params"]["post_ls_ref_nstg_cc_tune"]
	post_ls_ref_ncc_tune    =jsonParam["tstdc_counter_design_params"]["post_ls_ref_ncc_tune"]
	pre_es_fb_nstg          =jsonParam["tstdc_counter_design_params"]["pre_es_fb_nstg"]
	pre_es_fb_nstg_cc_tune  =jsonParam["tstdc_counter_design_params"]["pre_es_fb_nstg_cc_tune"]
	pre_es_fb_ncc_tune      =jsonParam["tstdc_counter_design_params"]["pre_es_fb_ncc_tune"]
	post_es_fb_nstg         =jsonParam["tstdc_counter_design_params"]["post_es_fb_nstg"]
	post_es_fb_nstg_cc_tune =jsonParam["tstdc_counter_design_params"]["post_es_fb_nstg_cc_tune"]
	post_es_fb_ncc_tune     =jsonParam["tstdc_counter_design_params"]["post_es_fb_ncc_tune"]


	std_cell_names=[buf8x_name,buf2x_name,buf4x_name,buf10x_name,dff_name,inv0p6x_name,buf16x_name,buf14x_name,embtdc_dff_name,xnor2_0p6_name,dffrpq_3x_name]
	dco_design_params = [nstg,ndrv,ncc,nfc,ncc_dead]
	tstdc_counter_design_params=[pre_ls_ref_nstg_cc_tune,pre_ls_ref_ncc_tune,pre_ls_ref_nfc,dltdc_num_ph,dltdc_nfc,dltdc_ndrv,dltdc_ncc,pre_nstg_ref_ls,pre_nstg_ref,pre_nstg_fb,ppath_nstg,pre_ls_ref_nstg,post_ls_ref_nstg,post_ls_ref_nstg_cc_tune,post_ls_ref_ncc_tune,pre_es_fb_nstg,pre_es_fb_nstg_cc_tune,pre_ds_fb_ncc_tune,post_es_fb_nstg,post_es_fb_nstg_cc_tune,post_es_fb_ncc_tune] 

def ble_dir_tree(outMode,absPvtDir_plat,outputDir,extDir,calibreRulesDir,hspiceDir,finesimDir,dco_flowDir,outbuff_div_flowDir,pll_flowDir,platform, vsimDir,tdc_flowDir):
	# verilog sim
	vsimDirs_list = [vsimDir, vsimDir+'/verilog',vsimDir+'/aprVerilog']
	gen_subDirs(vsimDirs_list)

	if outMode=="macro" or outMode=="full":
		gen_subDirs([absPvtDir_plat])

		hspiceDirs_split = hspiceDir.split("/")

		hspiceDirs_pol = hspiceDirs_split[1:len(hspiceDirs_split)-1]

		hspiceDirs_pol2 = []
		Dir_accum = hspiceDirs_pol[0] 
		for cnt in range(len(hspiceDirs_pol)):
			if cnt==0:
				Dir_accum = '/'+hspiceDirs_pol[0] 
			else:	
				Dir_accum = Dir_accum + "/" + hspiceDirs_pol[cnt] 
			hspiceDirs_pol2.append(Dir_accum) 

		print(hspiceDirs_pol2)
		gen_subDirs(hspiceDirs_pol2)

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
	
		dco_flowDirs=[dco_flowDir,dco_flowDir+'/src',dco_flowDir+'/scripts',dco_flowDir+'/scripts/innovus',dco_flowDir+'/scripts/dc',dco_flowDir+'/scripts/genus']
		gen_subDirs(dco_flowDirs)
	
		outbuff_div_flowDirs=[outbuff_div_flowDir]
		gen_subDirs(outbuff_div_flowDirs)

		pll_flowDirs=[pll_flowDir,pll_flowDir+'/src',pll_flowDir+'/scripts',pll_flowDir+'/scripts/innovus',pll_flowDir+'/scripts/dc',pll_flowDir+'/scripts/genus']
		gen_subDirs(pll_flowDirs)

		tdc_flowDirs=[tdc_flowDir,tdc_flowDir+'/src',tdc_flowDir+'/scripts',tdc_flowDir+'/scripts/innovus',tdc_flowDir+'/scripts/dc',tdc_flowDir+'/scripts/genus']
		gen_subDirs(tdc_flowDirs)

	if outputDir!=0:
		gen_subDirs([outputDir])

def ble_aux_copy_export(flowDir,DCDC_CAP_UNIT_lib,BUFH_X14N_pwr_lib):
	print ('#----------------------------------------------------------------------')
	print ('# Parsing decap cells')
	print ('#----------------------------------------------------------------------')
	if os.path.isdir(flowDir+'blocks/'):
		print('INFO: '+flowDir+'blocks/ already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/')

	if os.path.isdir(flowDir+'/blocks/DCDC_CAP_UNIT/export/'):
		print('INFO: '+flowDir+'/blocks/DCDC_CAP_UNIT/export already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks/DCDC_CAP_UNIT')
			os.mkdir(flowDir+'/blocks/DCDC_CAP_UNIT/export/')
			print(flowDir+'/blocks/DCDC_CAP_UNIT/export/ generated')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/DCDC_CAP_UNIT/export/')
	if os.path.isdir(flowDir+'/blocks/BUFH_X14N_pwr/export/'):
		print('INFO: '+flowDir+'/blocks/BUFH_X14N_pwr/export already exists')
	else:
		try:
			os.mkdir(flowDir+'/blocks/BUFH_X14N_pwr')
			os.mkdir(flowDir+'/blocks/BUFH_X14N_pwr/export/')
			print(flowDir+'/blocks/BUFH_X14N_pwr/export/ generated')
		except OSError:
			print('Error: unable to create '+flowDir+'/blocks/BUFH_X14N_pwr/export/')


	print(DCDC_CAP_UNIT_lib)

	try:
		for CAP_file in os.listdir(DCDC_CAP_UNIT_lib):
			print("INFO: copying aux-cell file:"+DCDC_CAP_UNIT_lib+CAP_file)
			shutil.copy(DCDC_CAP_UNIT_lib+CAP_file,flowDir+'blocks/DCDC_CAP_UNIT/export/')
		for BUF_file in os.listdir(BUFH_X14N_pwr_lib):
			print("INFO: copying aux-cell file:"+BUFH_X14N_pwr_lib+BUF_file)
			shutil.copy(BUFH_X14N_pwr_lib+BUF_file,flowDir+'blocks/BUFH_X14N_pwr/export/')

	except OSError:
		print('Error: unable to copy aux-cell files in '+flowDir+'/blocks/')
		sys.exit(1)

def read_std_cell_names(platform,track,std_cell_json):
	print ('#----------------------------------------------------------------------')
	print ('# Loading ' +std_cell_json+ ' for standard cell names...')
	print ('#----------------------------------------------------------------------')
	try:
		with open(std_cell_json) as file:
			jsonFile = json.load(file)
	except ValueError as e:
		print ('Error occurred opening or loading json file.')
		sys.exit(1)
	if track==9:
		track_s="9"
	elif track==10.5:
		track_s="10.5"

	if platform=="tsmc65lp":
		buf_small	=jsonFile[platform]["buf_small"]
		buf_big		=jsonFile[platform]["buf_big"]
		bufz		=jsonFile[platform]["bufz"]
		tdc_dff		=jsonFile[platform]["tdc_dff"]
		buf1_name	=jsonFile[platform]["buf1_name"]
		buf2_name	=jsonFile[platform]["buf2_name"]
		buf3_name	=jsonFile[platform]["buf3_name"]
		Height		=jsonFile[platform]["Height"]
	elif platform=="gf12lp":
		buf_small	=jsonFile[platform][track_s]["buf_small"]
		buf_big		=jsonFile[platform][track_s]["buf_big"]
		bufz		=jsonFile[platform][track_s]["bufz"]
		tdc_dff		=jsonFile[platform][track_s]["tdc_dff"]
		buf1_name	=jsonFile[platform][track_s]["buf1_name"]
		buf2_name	=jsonFile[platform][track_s]["buf2_name"]
		buf3_name	=jsonFile[platform][track_s]["buf3_name"]
		Height		=jsonFile[platform][track_s]["Height"]
	return buf_small,buf_big,buf1_name,buf2_name,buf3_name,tdc_dff,Height
