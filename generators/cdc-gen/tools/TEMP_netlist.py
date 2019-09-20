##for HSPICE netlist
import function


def gen_temp_netlist(ninv,nhead,aux1,aux2,aux3,aux4,aux5):
	r_netlist=open("flow/src/TEMP_ANALOG_test.nl.v","r")
	lines=list(r_netlist.readlines())
	w_netlist=open("flow/src/TEMP_ANALOG.nl.v","w")


	
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
	netmap1.get_net('nf',aux5,0,int(nhead)-1,1)
	netmap1.get_net('nh',None,0,int(nhead)-1,1)
	for line in lines:
		netmap1.printline(line,w_netlist)






