#====================================================================
# prepare setups for digital flow
# generates 1 verilog file
#====================================================================
import subprocess as sp
import HSPICE_mds
import sys
import os
import shutil
def pll_flow_setup(outMode,designName,genDir,outDir,formatDir,flowDir,ndrv,ncc,nfc,nstg,verilogSrcDir):

	if outMode=='macro' or outMode=='full':
		shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',flowDir+'/src/FUNCTIONS.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER_TDC_COUNTER.v',flowDir+'/src/PLL_CONTROLLER_TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER.v',flowDir+'/src/PLL_CONTROLLER.v')	
		shutil.copyfile(verilogSrcDir+'TDC_COUNTER.v',flowDir+'/src/TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'SSC_GENERATOR.v',flowDir+'/src/SSC_GENERATOR.v')	
		shutil.copyfile(verilogSrcDir+'dco_CC.v',flowDir+'/src/dco_CC.v')	
		shutil.copyfile(verilogSrcDir+'dco_FC.v',flowDir+'/src/dco_FC.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp.v',flowDir+'/src/synth_pll_dco_interp.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff.v',flowDir+'/src/synth_pll_dco_outbuff.v')	
		print(outMode,'mode: verilog sources are generated in ',flowDir,'src/')
	elif outMode=='verilog':
		shutil.copyfile(verilogSrcDir+'FUNCTIONS.v',outDir+'/FUNCTIONS.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER_TDC_COUNTER.v',outDir+'/PLL_CONTROLLER_TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'PLL_CONTROLLER.v',outDir+'/PLL_CONTROLLER.v')	
		shutil.copyfile(verilogSrcDir+'TDC_COUNTER.v',outDir+'/TDC_COUNTER.v')	
		shutil.copyfile(verilogSrcDir+'SSC_GENERATOR.v',outDir+'/SSC_GENERATOR.v')	
		shutil.copyfile(verilogSrcDir+'dco_CC.v',outDir+'/dco_CC.v')	
		shutil.copyfile(verilogSrcDir+'dco_FC.v',outDir+'/dco_FC.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_interp.v',outDir+'/synth_pll_dco_interp.v')	
		shutil.copyfile(verilogSrcDir+'synth_pll_dco_outbuff.v',outDir+'/synth_pll_dco_outbuff.v')	
		print(outMode,'mode: verilog sources are generated in ',outDir)
		print('verilog mode: verilog sources are generated in '+outDir)
		#--- generate verilog file ---
		r_pll_v=open(formatDir+'/form_pll_PD.v','r')
		nm1=HSPICE_mds.netmap()
		nm1.get_net('iN',designName,None,None,None)
		nm1.get_net('nM',None,nstg,nstg,1)
		nm1.get_net('nD',None,ndrv,ndrv,1)
		nm1.get_net('nF',None,nfc,nfc,1)
		nm1.get_net('nC',None,ncc,ncc,1)
		nm1.get_net('dN',designName+'_ffdco',None,None,None)
		with open(outDir+'/'+designName+'.v','w') as wvfile:
			lines_pll=list(r_pll_v.readlines())
			for line in lines_pll:
				nm1.printline(line,wvfile)
		#--- generate verilog file ---
		r_dco_v=open(formatDir+'/form_ffdco.v','r')
		nm1=HSPICE_mds.netmap()
		nm1.get_net('iN',designName+'_ffdco',None,None,None)
		nm1.get_net('nM',None,nstg,nstg,1)
		nm1.get_net('nD',None,ndrv,ndrv,1)
		nm1.get_net('nF',None,nfc,nfc,1)
		nm1.get_net('nC',None,ncc,ncc,1)
		with open(outDir+'/'+designName+'_ffdco.v','w') as wvfile:
			lines_dco=list(r_dco_v.readlines())
			for line in lines_dco:
				nm1.printline(line,wvfile)


