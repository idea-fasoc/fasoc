import os
import glob
import shutil
import subprocess as sp

def gen_post_pex_netlist(platform, designName, formatDir, flowDir, extDir, calibreRulesDir, wellpin, spectre):
	# v2lvs netlist: 1. wellpin in cadre => copy from cadre 2. no wellpin in cadre => run v2lvs again with modified verilog
	if wellpin==1:
		for file in glob.glob(flowDir+'/results/calibre/lvs/_'+designName+'*.sp'):
			shutil.copy(file, extDir+'/sch/'+designName+'.spi')
	else:
		p = sp.Popen(['cp', flowDir+'/results/innovus/'+designName+'_lvs.v', flowDir+'/results/innovus/'+designName+'_lvs_well.v']) 
		p.wait()
		
		p = sp.Popen(['vi', flowDir+'/results/innovus/'+designName+'_lvs_well.v', \
			      '-c', '%s/.VDD(VDD)/.VDD(VDD), .VNW(VDD), .VPW(VSS)/g | wq'])
		p.wait()
		
		cdlInclude = ''
		cdlParse   = ''
		with open(flowDir + '/scripts/innovus/generated/' + designName + \
			  '.cdlList', 'r') as file:
		   filedata = file.readlines()
		
		for line in filedata:
		   cdlInclude = cdlInclude + ' -s ' + line.rstrip()
		   cdlParse   = cdlParse + ' -lsr ' + line.rstrip()

		p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl',
			      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-v',
		              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
		              '-o',extDir+'/sch/'+designName+'.spi','-i','-c','/_'])
		p.wait()
	
	# Copy the merged gds file to extraction directory
	p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
					extDir+'/layout/'+designName+'.gds.gz'])
	p.wait()
	# Copy runsets 
	shutil.copy(formatDir+'pex.runset.'+platform, extDir+'/runsets/pex.runset.'+platform)
	
	# Clean the space for PEX
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.dv'):
		os.remove(extDir + '/run/svdb/' + designName + '.dv')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.extf'):
		os.remove(extDir + '/run/svdb/' + designName + '.extf')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.lvsf'):
		os.remove(extDir + '/run/svdb/' + designName + '.lvsf')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.pdsp'):
		os.remove(extDir + '/run/svdb/' + designName + '.pdsp')
	if os.path.isfile(extDir + '/run/svdb/' + designName + '.sp'):
		os.remove(extDir + '/run/svdb/' + designName + '.sp')
	
	if os.path.isdir(extDir + '/run/svdb/' + designName + '.phdb'):
		shutil.rmtree(extDir + '/run/svdb/' + designName + '.phdb',
						  ignore_errors=True)
	if os.path.isdir(extDir + '/run/svdb/' + designName + '.xdb'):
		shutil.rmtree(extDir + '/run/svdb/' + designName + '.xdb',
						  ignore_errors=True)
	if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdb'):
		shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdb',
						  ignore_errors=True)
	if os.path.isdir(extDir + '/run/svdb/' + 'template'):
		shutil.rmtree(extDir + '/run/svdb/' + 'template',
						  ignore_errors=True)
	
	# Set the environment variables
	if platform == 'gf12lp':
		with open(flowDir + '/scripts/innovus/generated/' + designName + \
			  '.beolStack', 'r') as file:
			filedata = file.read()
		os.environ['BEOL_STACK'] = filedata.rstrip()
		with open(flowDir + '/scripts/innovus/generated/' + designName + \
			  '.techLvsDir', 'r') as file:
			filedata = file.read()
		os.environ['TECHDIR_LVS'] = filedata.rstrip()
		with open(flowDir + '/scripts/innovus/generated/' + designName + \
			  '.techPexDir', 'r') as file:
			filedata = file.read()
		os.environ['TECHDIR_XACT'] = filedata.rstrip()
		os.environ['PEX_RUN'] = 'TRUE'
	
	# Configure the PEX rule files
	for file in os.listdir(calibreRulesDir + '/'):
		if not os.path.isdir(calibreRulesDir + '/' + file):
			shutil.copy2(calibreRulesDir+'/'+file, extDir+'/run/')
	
	with open(extDir+'/runsets/pex.runset.'+platform, 'r') as file:
		filedata = file.read()
	filedata = filedata.replace('design', designName)
	if spectre==0:
		extRunDir=extDir+'/run/'
		filedata = filedata.replace('netlistform', 'HSPICE')
	elif spectre==1:
		extRunDir=extDir+'/run_scs/'
		filedata = filedata.replace('netlistform', 'SPECTRE')

	with open(extRunDir+'pex.runset', 'w') as file:
		file.write(filedata)
	
	# Run Calibre RCX
	if platform == 'gf12lp':
		p = sp.Popen(['calibre','-gui','-xact','-batch','-runset',
						 'pex.runset'],cwd=extRunDir)
		p.wait()
	else:
		p = sp.Popen(['calibre','-gui','-pex','-batch','-runset',
						 'pex.runset'],cwd=extRunDir)
		p.wait()

	# tsmc65lp
#		p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.rcx_',extDir+'/run/'])
#		p.wait()
#		p = sp.Popen(['cp',calibreRulesDir+'/calibre.rcx',extDir+'/run/'])
#		p.wait()
#		p = sp.Popen(['cp',calibreRulesDir+'/rules',extDir+'/run/'])
#		p.wait()
#		with open(extDir+'/run/_calibre.rcx_', 'r') as file:
#		   filedata = file.read()
#		filedata = filedata.replace('design', designName)
#		with open(extDir+'/run/_calibre.rcx_', 'w') as file:
#		   file.write(filedata)
#		p = sp.Popen(['calibre','-xrc','-phdb','-nowait','-turbo','1',
#		             '_calibre.rcx_'],cwd=extDir+'/run')
#		p.wait()
#		p = sp.Popen(['calibre','-xrc','-pdb','-rcc','-turbo','1','-nowait',
#		             '_calibre.rcx_'],cwd=extDir+'/run')
#		p.wait()
#		p = sp.Popen(['calibre','-xrc','-fmt','-all','-nowait','_calibre.rcx_'],
#		             cwd=extDir+'/run')
#		p.wait()

#------------------------------------------------------------------------------
# LVS and PEX flow for 65nm (extra steps for welltaps issues) 
# flowDir should be absolute path
#------------------------------------------------------------------------------
def lvs_pex_65nm(calibreRulesDir,flowDir,extDir,simDir,designName,lvs,pex):
	#with open('./tempFiles/platform_config.json') as file:
	#    jsonConfig = json.load(file)
	#
	#calibreRulesDir = jsonConfig['calibreRules']
	
	if lvs==1 or pex==1:		
		# Generate pre PEX netlist and gds files
		p = sp.Popen(['cp', flowDir+'/results/innovus/'+designName+'_lvs.v', flowDir+'/results/innovus/'+designName+'_lvs_well.v']) 
		p.wait()
		
		p = sp.Popen(['vi', flowDir+'/results/innovus/'+designName+'_lvs_well.v', \
			      '-c', '%s/.VDD(VDD)/.VDD(VDD), .VNW(VDD), .VPW(VSS)/g | wq'])
		p.wait()
		
		cdlInclude = ''
		cdlParse   = ''
		with open(flowDir + '/scripts/innovus/generated/' + designName + \
			  '.cdlList', 'r') as file:
		   filedata = file.readlines()
		
		for line in filedata:
		   cdlInclude = cdlInclude + ' -s ' + line.rstrip()
		   cdlParse   = cdlParse + ' -lsr ' + line.rstrip()

		p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl',
			      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-v',
		              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
		              '-o',extDir+'/sch/'+designName+'.spi','-i','-c','/_'])
		p.wait()
	
		# NOTE: The exported version of the gds is not merged (i.e. doesn't include standard cells)
		p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
			      extDir+'/layout/'+designName+'.gds.gz'])
		p.wait()
	
		# Clean the space
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.dv'):
		   os.remove(extDir + '/run/svdb/' + designName + '.dv')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.extf'):
		   os.remove(extDir + '/run/svdb/' + designName + '.extf')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.lvsf'):
		   os.remove(extDir + '/run/svdb/' + designName + '.lvsf')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.pdsp'):
		   os.remove(extDir + '/run/svdb/' + designName + '.pdsp')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.sp'):
		   os.remove(extDir + '/run/svdb/' + designName + '.sp')

	# Calibre LVS
	if lvs==1: 
		p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.lvs_',extDir+'/run/'])
		p.wait()
		with open(extDir+'/run/_calibre.lvs_', 'r') as file:
		   filedata = file.read()
		filedata = filedata.replace('design', designName)
		with open(extDir+'/run/_calibre.lvs_', 'w') as file:
		   file.write(filedata)
		
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdhB'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdhB', 
		                 ignore_errors=True)
		p = sp.Popen(['calibre','-spice',designName+'.sp','-lvs','-hier','-nowait',
		              '_calibre.lvs_'],cwd=extDir+'/run')
		p.wait()
		print ('# PLL - LVS completed. check '+extDir+'/run/'+designName+'.lvs.report')

	# Calibre RCX
	if pex==1:
		p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.rcx_',extDir+'/run/'])
		p.wait()
		p = sp.Popen(['cp',calibreRulesDir+'/calibre.rcx',extDir+'/run/'])
		p.wait()
		p = sp.Popen(['cp',calibreRulesDir+'/rules',extDir+'/run/'])
		p.wait()
		with open(extDir+'/run/_calibre.rcx_', 'r') as file:
		   filedata = file.read()
		filedata = filedata.replace('design', designName)
		with open(extDir+'/run/_calibre.rcx_', 'w') as file:
		   file.write(filedata)
	
		# Clean
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.phdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.phdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.xdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.xdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + 'template'):
		   shutil.rmtree(extDir + '/run/svdb/' + 'template',
		                 ignore_errors=True)
		
		p = sp.Popen(['calibre','-xrc','-phdb','-nowait','-turbo','1',
		             '_calibre.rcx_'],cwd=extDir+'/run')
		p.wait()
		p = sp.Popen(['calibre','-xrc','-pdb','-rcc','-turbo','1','-nowait',
		             '_calibre.rcx_'],cwd=extDir+'/run')
		p.wait()
		p = sp.Popen(['calibre','-xrc','-fmt','-all','-nowait','_calibre.rcx_'],
		             cwd=extDir+'/run')
		p.wait()
		print (designName+' post PEX netlist Generated')
#------------------------------------------------------------------------------
# generates dco.gds, .pex.netlist 
#------------------------------------------------------------------------------
def dco_flow_pex(calibreRulesDir,netlistDir,formatDir,flowDir,rawPexDir,extDir,simDir,ndrv,ncc,nfc,nstg,ninterp,W_CC,H_CC,W_FC,H_FC,bleach,design,pex):
	designName='dco_%ddrv_%dcc_%dfc_%dstg'%(ndrv,ncc,nfc,nstg)
	print('starting flow for '+designName)
	#-------------------------------------------
	# flow setup 
	#-------------------------------------------
	if bleach==1:
		p = sp.Popen(['make','bleach_all'], cwd=flowDir)
		p.wait()

	Flow_setup.dco_flow_setup(formatDir,flowDir,ndrv,ncc,nfc,nstg)

	NCtotal=nstg*(ncc+ndrv)
	NFtotal=nstg*(nfc)
	Atotal=NCtotal*W_CC*H_CC+NFtotal*W_FC*H_FC	
	W_core=math.ceil(math.sqrt(Atotal)*1.2)
	H_core=W_core
	
	with open(flowDir + '/scripts/innovus/always_source.tcl', 'r') as file:
	   filedata = file.read()
	filedata = re.sub(r'set core_width.*', r'set core_width    ' + \
			  str(W_core) + ' ;# Core Area Width', filedata)
	filedata = re.sub(r'set core_height.*', r'set core_height   ' + \
			  str(H_core) + ' ;# Core Area Height', filedata)
	with open(flowDir + '/scripts/innovus/always_source.tcl', 'w') as file:
	   file.write(filedata)
		
	#-------------------------------------------
	# run CADRE flow 
	#-------------------------------------------
	if design==1:
		
		p = sp.Popen(['make','design'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','lvs'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','drc'], cwd=flowDir)
		p.wait()
		
		p = sp.Popen(['make','export'], cwd=flowDir)
		p.wait()
		
	#-------------------------------------------
	# check if pex.netlist already exists 
	#-------------------------------------------
	if pex==1:
		try:
			exist=open(netlistDir+designName+'.pex.netlist','r')
			print(designName+'.pex.netlist already exists')
		except:
			#-------------------------------------------
			# generate pex view
			#-------------------------------------------
			lvs=1  # do lvs for default
			lvs_pex_65nm(calibreRulesDir,flowDir,extDir,simDir,designName,lvs,pex)
			
			#-------------------------------------------
			# modify the pex netlist
			#-------------------------------------------
			HSPICEpex_netlist.gen_pex_netlist(rawPexDir,netlistDir,formatDir,ncc,ndrv,nfc,nstg,ninterp,designName)
			
			#-------------------------------------------
			# copy .pxi, .pex
			#-------------------------------------------
			p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.'+designName+'.pxi',netlistDir+'/'+designName+'.pex.netlist.'+designName+'.pxi'])
			p.wait()
			p = sp.Popen(['cp',extDir+'/run/'+designName+'.pex.netlist.pex',netlistDir+'/'+designName+'.pex.netlist.pex'])
			p.wait()

#------------------------------------------------------------------------------
# Run LVS and generate post PEX netlist
# flowDir should be absolute path
# This funciton is especially for design using ff_dco as a Hard Macro 
#------------------------------------------------------------------------------
def post_apr_HM(VDDnames,buf,bufName,dcoName,calibreRulesDir,flowDir,extDir,designName,lvs,pex):
	#with open('./tempFiles/platform_config.json') as file:
	#    jsonConfig = json.load(file)
	#
	#calibreRulesDir = jsonConfig['calibreRules']
	
	if lvs==1 or pex==1:		
		# Generate pre PEX netlist and gds files
		p = sp.Popen(['cp', flowDir+'/results/innovus/'+designName+'_lvs.v', flowDir+'/results/innovus/'+designName+'_lvs_well.v']) 
		p.wait()
	
		for VDDname in VDDnames:	
			p = sp.Popen(['vi', flowDir+'/results/innovus/'+designName+'_lvs_well.v', \
				      '-c', '%s/.VDD('+VDDname+')/.VDD('+VDDname+'), .VNW('+VDDname+'), .VPW(VSS)/g | wq'])
			p.wait()
		
		cdlInclude = ''
		cdlParse   = ''
		with open(flowDir + '/scripts/innovus/generated/' + designName + \
			  '.cdlList', 'r') as file:
		   filedata = file.readlines()
		
		for line in filedata:
		   cdlInclude = cdlInclude + ' -s ' + line.rstrip()
		   cdlParse   = cdlParse + ' -lsr ' + line.rstrip()

		#p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl', flowDir+'/blocks/ff_dco4/export/ff_dco4.cdl',
		#	      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-s',flowDir+'/blocks/ff_dco4/export/ff_dco4.cdl', '-v',
		#              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
		#              #flowDir+'/results/innovus/'+designName+'_lvs_well.v', '-v',flowDir+'/blocks/ff_dco/export/ff_dco.v',
		#              '-o',extDir+'/sch/'+designName+'.spi','-c','/_'])
		#              #'-o',extDir+'/sch/'+designName+'.spi','-i','-c','/_'])


		if buf==0:
			p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl', flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl',
				      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-s',flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl', '-v',
			              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
			              '-o',extDir+'/sch/'+designName+'.spi','-c','/_'])
			p.wait()
		elif buf==1:
			p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl',flowDir+'/blocks/'+bufName+'/export/'+bufName+'.cdl', flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl',
				      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-s',flowDir+'/blocks/'+dcoName+'/export/'+dcoName+'.cdl','-s',flowDir+'/blocks/'+bufName+'/export/'+bufName+'.cdl', '-v',
			              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
			              '-o',extDir+'/sch/'+designName+'.spi','-c','/_'])
			p.wait()
	
		# NOTE: The exported version of the gds is not merged (i.e. doesn't include standard cells)
		p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
			      extDir+'/layout/'+designName+'.gds.gz'])
		p.wait()
	
		# Clean the space
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.dv'):
		   os.remove(extDir + '/run/svdb/' + designName + '.dv')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.extf'):
		   os.remove(extDir + '/run/svdb/' + designName + '.extf')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.lvsf'):
		   os.remove(extDir + '/run/svdb/' + designName + '.lvsf')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.pdsp'):
		   os.remove(extDir + '/run/svdb/' + designName + '.pdsp')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.sp'):
		   os.remove(extDir + '/run/svdb/' + designName + '.sp')

	# Calibre LVS
	if lvs==1: 
		p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.lvs_',extDir+'/run/'])
		p.wait()
		with open(extDir+'/run/_calibre.lvs_', 'r') as file:
		   filedata = file.read()
		filedata = filedata.replace('design', designName)
		with open(extDir+'/run/_calibre.lvs_', 'w') as file:
		   file.write(filedata)
		
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdhB'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdhB', 
		                 ignore_errors=True)
		p = sp.Popen(['calibre','-spice',designName+'.sp','-lvs','-hier','-nowait',
		              '_calibre.lvs_'],cwd=extDir+'/run')
		p.wait()
		print ('# PLL - LVS completed. check '+extDir+'/run/'+designName+'.lvs.report')

	# Calibre RCX
	if pex==1:
		p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.rcx_',extDir+'/run/'])
		p.wait()
		p = sp.Popen(['cp',calibreRulesDir+'/calibre.rcx',extDir+'/run/'])
		p.wait()
		p = sp.Popen(['cp',calibreRulesDir+'/rules',extDir+'/run/'])
		p.wait()
		with open(extDir+'/run/_calibre.rcx_', 'r') as file:
		   filedata = file.read()
		filedata = filedata.replace('design', designName)
		with open(extDir+'/run/_calibre.rcx_', 'w') as file:
		   file.write(filedata)
	
		# Clean
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.phdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.phdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.xdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.xdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + 'template'):
		   shutil.rmtree(extDir + '/run/svdb/' + 'template',
		                 ignore_errors=True)
		
		p = sp.Popen(['calibre','-xrc','-phdb','-nowait','-turbo','1',
		             '_calibre.rcx_'],cwd=extDir+'/run')
		p.wait()
		p = sp.Popen(['calibre','-xrc','-pdb','-rcc','-turbo','1','-nowait',
		             '_calibre.rcx_'],cwd=extDir+'/run')
		p.wait()
		p = sp.Popen(['calibre','-xrc','-fmt','-all','-nowait','_calibre.rcx_'],
		             cwd=extDir+'/run')
		p.wait()
		print ('# PLL - Post PEX netlist Generated')



def post_apr(dcoAux,calibreRulesDir,flowDir,extDir,designName,lvs,pex):
	#with open('./tempFiles/platform_config.json') as file:
	#    jsonConfig = json.load(file)
	#
	#calibreRulesDir = jsonConfig['calibreRules']
	
	if lvs==1 or pex==1:		
		# Generate pre PEX netlist and gds files
		p = sp.Popen(['cp', flowDir+'/results/innovus/'+designName+'_lvs.v', flowDir+'/results/innovus/'+designName+'_lvs_well.v']) 
		p.wait()
		
		p = sp.Popen(['vi', flowDir+'/results/innovus/'+designName+'_lvs_well.v', \
			      '-c', '%s/.VDD(VDD)/.VDD(VDD), .VNW(VDD), .VPW(VSS)/g | wq'])
		p.wait()
		
		cdlInclude = ''
		cdlParse   = ''
		with open(flowDir + '/scripts/innovus/generated/' + designName + \
			  '.cdlList', 'r') as file:
		   filedata = file.readlines()
		
		for line in filedata:
		   cdlInclude = cdlInclude + ' -s ' + line.rstrip()
		   cdlParse   = cdlParse + ' -lsr ' + line.rstrip()

		if dcoAux==1:
			p = sp.Popen(['v2lvs', cdlParse, '-lsr', flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-lsr', flowDir+'/blocks/dco_FC/export/dco_FC.cdl',
				      cdlInclude, '-s',flowDir+'/blocks/dco_CC/export/dco_CC.cdl','-s',flowDir+'/blocks/dco_FC/export/dco_FC.cdl','-v',
			              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
			              '-o',extDir+'/sch/'+designName+'.spi','-i','-c','/_'])
			p.wait()
		else:
			p = sp.Popen(['v2lvs', cdlParse,
				      cdlInclude,'-v',
			              flowDir+'/results/innovus/'+designName+'_lvs_well.v',
			              '-o',extDir+'/sch/'+designName+'.spi','-i','-c','/_'])
			p.wait()
	
		# NOTE: The exported version of the gds is not merged (i.e. doesn't include standard cells)
		p = sp.Popen(['cp', flowDir+'/results/calibre/'+designName+'.merged.gds.gz', \
			      extDir+'/layout/'+designName+'.gds.gz'])
		p.wait()
	
		# Clean the space
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.dv'):
		   os.remove(extDir + '/run/svdb/' + designName + '.dv')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.extf'):
		   os.remove(extDir + '/run/svdb/' + designName + '.extf')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.lvsf'):
		   os.remove(extDir + '/run/svdb/' + designName + '.lvsf')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.pdsp'):
		   os.remove(extDir + '/run/svdb/' + designName + '.pdsp')
		if os.path.isfile(extDir + '/run/svdb/' + designName + '.sp'):
		   os.remove(extDir + '/run/svdb/' + designName + '.sp')

	# Calibre LVS
	if lvs==1: 
		p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.lvs_',extDir+'/run/'])
		p.wait()
		with open(extDir+'/run/_calibre.lvs_', 'r') as file:
		   filedata = file.read()
		filedata = filedata.replace('design', designName)
		with open(extDir+'/run/_calibre.lvs_', 'w') as file:
		   file.write(filedata)
		
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdhB'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdhB', 
		                 ignore_errors=True)
		p = sp.Popen(['calibre','-spice',designName+'.sp','-lvs','-hier','-nowait',
		              '_calibre.lvs_'],cwd=extDir+'/run')
		p.wait()
		print ('# PLL - LVS completed. check '+extDir+'/run/'+designName+'.lvs.report')

	# Calibre RCX
	if pex==1:
		p = sp.Popen(['cp',extDir+'/ruleFiles/_calibre.rcx_',extDir+'/run/'])
		p.wait()
		p = sp.Popen(['cp',calibreRulesDir+'/calibre.rcx',extDir+'/run/'])
		p.wait()
		p = sp.Popen(['cp',calibreRulesDir+'/rules',extDir+'/run/'])
		p.wait()
		with open(extDir+'/run/_calibre.rcx_', 'r') as file:
		   filedata = file.read()
		filedata = filedata.replace('design', designName)
		with open(extDir+'/run/_calibre.rcx_', 'w') as file:
		   file.write(filedata)
	
		# Clean
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.phdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.phdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.xdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.xdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + designName + '.pdb'):
		   shutil.rmtree(extDir + '/run/svdb/' + designName + '.pdb',
		                 ignore_errors=True)
		if os.path.isdir(extDir + '/run/svdb/' + 'template'):
		   shutil.rmtree(extDir + '/run/svdb/' + 'template',
		                 ignore_errors=True)
		
		p = sp.Popen(['calibre','-xrc','-phdb','-nowait','-turbo','1',
		             '_calibre.rcx_'],cwd=extDir+'/run')
		p.wait()
		p = sp.Popen(['calibre','-xrc','-pdb','-rcc','-turbo','1','-nowait',
		             '_calibre.rcx_'],cwd=extDir+'/run')
		p.wait()
		p = sp.Popen(['calibre','-xrc','-fmt','-all','-nowait','_calibre.rcx_'],
		             cwd=extDir+'/run')
		p.wait()
		print ('# PLL - Post PEX netlist Generated')
