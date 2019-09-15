#========================================================================
# Derive loop parameters and generate testbench.v
#========================================================================
import HSPICE_mds

def tb_verilog_gen(formatDir,tbDir,relBW,Kp_o_Ki,Fref,dFf,dFc,FCW,Fbase,ndrv,ncc,nfc,nstg):
	Kp=relBW*Fref/dFf
	Ki=Kp/Kp_o_Ki

	nm1=HSPICE_mds.netmap()
	nm1.get_net('ns',None,nstg,nstg,1)
	nm1.get_net('nc',None,ncc,ncc,1)
	nm1.get_net('nf',None,nfc,nfc,1)
	nm1.get_net('nd',None,ndrv,ndrv,1)
	nm1.get_net('fb',None,Fbase,Fbase,1)
	nm1.get_net('dc',None,dFc,dFc,1)
	nm1.get_net('df',None,dFf,dFf,1)
	nm1.get_net('FR',None,Fref,Fref,1)
	nm1.get_net('Kp',None,Kp,Kp,1)
	nm1.get_net('Ki',None,Ki,Ki,1)
	nm1.get_net('FW',None,FCW,FCW,1)
	nm1.get_net('CT',None,30,30,1) # coarse_lock_threshold
	nm1.get_net('CC',None,10,10,1) # coarse_lock_count
	nm1.get_net('FT',None,10,10,1) # fine_lock_threshold
	nm1.get_net('FC',None,30,30,1) # fine_lock_count

	r_TB=open(formatDir+'form_TB_PLL_CONTROLLER_TDC_COUNTER.sv','r')
	w_TB=open(tbDir+'TB_PLL_CONTROLLER_TDC_COUNTER.sv','w')

	lines=list(r_TB.readlines())
	for line in lines:
		nm1.printline(line,w_TB)
	print('verilog testbench ready')
