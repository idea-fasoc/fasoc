#------------------------------------------------------------------------------
# generates PLL model with pex simulation for pll level only (ff_dco as a hard macro) 
#------------------------------------------------------------------------------
import sys
import getopt
import math
import subprocess as sp
import fileinput
import re
import os
import shutil
import numpy as np
import argparse
import json

import HSPICE_mds
import HSPICEpex_netlist

#flowDir='./flow'
#extDir = './extraction'
#simDir = './HSPICE'
#designName='dco_8stg'



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
