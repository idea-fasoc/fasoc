##for HSPICE netlist
import re
import function
from readparamgen import check_search_done, platformConfig, designName, args, jsonSpec
#import os

def gen_temp_netlist(ninv,nhead,aux1,aux2,aux3,aux4,aux5, srcDir):
	if args.platform == 'tsmc65lp' :
		r_netlist=open(srcDir + "/TEMP_ANALOG_lv.v","r")
		lines=list(r_netlist.readlines())
		w_netlist=open(srcDir + "/TEMP_ANALOG_lv.nl.v","w")
		port = 'Y'
		slc_cell = "LC1P2TO3P6X1RVT_VDDX4 a_lc_0(.A(out), .AB(outb), .Y(lc_0));"
	if args.platform == 'gf12lp' or args.platform == 'sky130':
		r_netlist=open(srcDir + "/TEMP_ANALOG_lv.v","r")
		lines=list(r_netlist.readlines())
		w_netlist=open(srcDir + "/TEMP_ANALOG_lv.nl.v","w")
		port = 'Y' if args.platform == 'gf12lp' else 'X'
		if args.platform == 'sky130':
			slc_cell = "SLC a_lc_0(.IN(out), .INB(outb), .VOUT(lc_0));"
		else:
			slc_cell = "SLC_cell a_lc_0(.A(out), .AB(outb), .Y(lc_0));"

	netmap1=function.netmap() #modify here
	netmap1.get_net('nn',None,1,int(ninv),1)
	netmap1.get_net('n0',None,int(ninv),int(ninv),1)
	netmap1.get_net('na',aux1,1,1,1)
	netmap1.get_net('nb',aux2,0,int(ninv)-2,1)
	netmap1.get_net('ni',None,0,int(ninv)-2,1)
	netmap1.get_net('n1',None,1,int(ninv)-1,1)	
	netmap1.get_net('n2',None,2,int(ninv),1)
	netmap1.get_net('ng',aux2,1,1,1)
	netmap1.get_net('n3',None,int(ninv),int(ninv),1)
	netmap1.get_net('nk',aux2,1,1,1)
	netmap1.get_net('n4',None,int(ninv),int(ninv),1)
	netmap1.get_net('nm',aux2,1,1,1)
	netmap1.get_net('np',aux3,1,1,1)
	netmap1.get_net('nc',aux3,1,1,1)
	netmap1.get_net('nd',aux4,1,1,1)
	netmap1.get_net('ne',aux4,1,1,1)
	for line in lines:
		line = line.replace("nbout", port)
		if args.platform == 'tsmc65lp':
			line = re.sub("\)\);", "), .VIN(1'b1));", line);
		netmap1.printline(line,w_netlist)
	
	
	r_netlist=open(srcDir + "/TEMP_ANALOG_hv.v","r")	
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/TEMP_ANALOG_hv.nl.v","w")

	netmap1.get_net('nf',aux5,0,int(nhead)-1,1)
	netmap1.get_net('nh',None,0,int(nhead)-1,1)
	netmap1.get_net('no',aux3,1,1,1)
	for line in lines:
		line = line.replace("SLC", slc_cell)
		line = line.replace("nbout", port)
		netmap1.printline(line,w_netlist)
	
	r_netlist=open(srcDir + "/counter_generic.v","r")	
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/counter.v","w")

	netmap1.get_net('np',aux3,1,1,1)
	for line in lines:
		line = line.replace("nbout", port)
		netmap1.printline(line,w_netlist)

	return;


	#netmap1=function.netmap() #modify here
	#netmap1.get_net('nn',None,1,int(ninv),1)
	#netmap1.get_net('n0',None,int(ninv),int(ninv),1)
	#netmap1.get_net('na',aux1,1,1,1)
	#netmap1.get_net('nb',aux2,0,int(ninv)-2,1)
	#netmap1.get_net('ni',None,0,int(ninv)-2,1)
	#netmap1.get_net('n1',None,1,int(ninv)-1,1)	
	#netmap1.get_net('n2',None,2,int(ninv),1)
	#netmap1.get_net('ng',aux2,1,1,1)
	#netmap1.get_net('n3',None,int(ninv),int(ninv),1)
	#netmap1.get_net('nk',aux2,1,1,1)
	#netmap1.get_net('n4',None,int(ninv),int(ninv),1)
	#netmap1.get_net('nm',aux2,1,1,1)
	#netmap1.get_net('np',aux3,1,1,1)
	#netmap1.get_net('nc',aux3,1,1,1)
	#netmap1.get_net('nd',aux4,1,1,1)
	#netmap1.get_net('ne',aux4,1,1,1)
	#netmap1.get_net('nf',aux5,0,int(nhead)-1,1)
	#netmap1.get_net('nh',None,0,int(nhead)-1,1)
	#for line in lines:
	#	netmap1.printline(line,w_netlist)

