##for HSPICE netlist
import function
from readparamgen import check_search_done, platformConfig, designName, args, jsonSpec


def gen_cdc_invchainiso(ninv,aux1,aux2,srcDir):
	if args.platform == 'tsmc65lp' :
		r_netlist=open(srcDir + "/INVCHAIN_ISOVDD_template.nl.v","r")
		lines=list(r_netlist.readlines())
		w_netlist=open(srcDir + "/INVCHAIN_ISOVDD.nl.v","w")
	if args.platform == 'gf12lp' :
		r_netlist=open(srcDir + "/INVCHAIN_ISOVDD_template_generic.nl.v","r")
		lines=list(r_netlist.readlines())
		w_netlist=open(srcDir + "/INVCHAIN_ISOVDD.nl.v","w")
	
	
	netmap1=function.netmap() #modify here
	netmap1.get_net('nn',None,1,ninv,1)
	netmap1.get_net('na',aux1,1,1,1)
	netmap1.get_net('nb',aux1,1,ninv-1,1)
	netmap1.get_net('ni',None,1,ninv-1,1)
	netmap1.get_net('n1',None,1,ninv-1,1)	
	netmap1.get_net('n2',None,2,ninv,1)
	netmap1.get_net('nc',aux2,1,1,1)
	netmap1.get_net('n3',None,ninv,ninv,1)
	for line in lines:
		netmap1.printline(line,w_netlist)
		

def gen_cdc_invchain(ninv,aux1,aux2,srcDir):
	r_netlist=open(srcDir + "/CDC_ANALOG2_template.nl.v","r")
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/CDC_ANALOG2.nl.v","w")
	
	netmap2=function.netmap() #modify here
	netmap2.get_net('nn',None,1,ninv,1)
	netmap2.get_net('na',aux1,1,1,1)
	netmap2.get_net('nb',aux1,1,ninv-1,1)
	netmap2.get_net('ni',None,1,ninv-1,1)
	netmap2.get_net('n1',None,1,ninv-1,1)	
	netmap2.get_net('n2',None,2,ninv,1)
	netmap2.get_net('nc',aux2,1,1,1)
	netmap2.get_net('n3',None,ninv,ninv,1)
	for line in lines:
		netmap2.printline(line,w_netlist)

def gen_cdc_nxt_edge_gen(aux1,aux2,aux3,aux4,srcDir):
	r_netlist=open(srcDir + "/NEXT_EDGE_GEN_template.nl.v","r")
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/NEXT_EDGE_GEN.nl.v","w")
	
	netmap3=function.netmap() #modify here
	for i in range(0,12): 
		netmap3.get_net('na',aux1,1,1,1)
	for i in range(0,4): 
		netmap3.get_net('nb',aux2,1,1,1)	
	for i in range(0,8): 
		netmap3.get_net('nc',aux3,1,1,1)
	for i in range(0,2): 
		netmap3.get_net('nd',aux4,1,1,1)
	for line in lines:
		netmap3.printline(line,w_netlist)

def gen_cdc_dly_comp(aux1,aux2,aux3,aux4,aux5,srcDir):
	r_netlist=open(srcDir + "/DLY_COMP_template.nl.v","r")
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/DLY_COMP.nl.v","w")
	
	netmap4=function.netmap() #modify here
	for i in range(0,5): 
		netmap4.get_net('na',aux1,1,1,1)
	for i in range(0,2): 
		netmap4.get_net('nb',aux2,1,1,1)
	for i in range(0,2): 
		netmap4.get_net('nc',aux3,1,1,1)
	netmap4.get_net('nd',aux4,1,1,1)
	netmap4.get_net('nf',aux5,1,1,1)
	for line in lines:
		netmap4.printline(line,w_netlist)

def gen_cdc_analog(npre,aux1,aux2,srcDir):	
	if args.platform == 'tsmc65lp' :
		r_netlist=open(srcDir + "/CDC_ANALOG_template.nl.v","r")
		lines=list(r_netlist.readlines())
		w_netlist=open(srcDir + "/CDC_ANALOG.nl.v","w")
	if args.platform == 'gf12lp' :
		r_netlist=open(srcDir + "/CDC_ANALOG_template_generic.nl.v","r")
		lines=list(r_netlist.readlines())
		w_netlist=open(srcDir + "/CDC_ANALOG.nl.v","w")

	netmap5=function.netmap() #modify here
	netmap5.get_net('na',aux1,1,npre,1)
	netmap5.get_net('ni',None,1,npre,1)
	for i in range(0,2): 
		netmap5.get_net('nb',aux2,1,1,1)

	for line in lines:
		netmap5.printline(line,w_netlist)



def gen_cdc_cnt(aux1,aux2,aux3,aux4,srcDir):
	r_netlist=open(srcDir + "/CDCW_CNT_template.v","r")
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/CDCW_CNT.v","w")
	
	netmap6=function.netmap() #modify here
	netmap6.get_net('na',aux1,1,1,1)
	for i in range(0,2): 
		netmap6.get_net('nb',aux2,1,1,1)
	netmap6.get_net('nc',aux3,1,1,1)
	netmap6.get_net('nd',aux4,1,1,1)
	for line in lines:
		netmap6.printline(line,w_netlist)


def gen_cdc_top(aux1,aux2,srcDir):
	r_netlist=open(srcDir + "/CDC_template.v","r")
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/cdcInst.v","w")
	
	netmap7=function.netmap() #modify here
	for i in range(0,16): 
		netmap7.get_net('na',aux1,1,1,1)
	for i in range(0,3): 
		netmap7.get_net('nb',aux2,1,1,1)
	for i in range(0,2): 
		netmap7.get_net('nc',aux1,1,1,1)

	for line in lines:
		netmap7.printline(line,w_netlist)
