##for HSPICE netlist
import function
import fileinput

def gen_SC_netlist(CON, PD, aux1,srcDir):
	r_netlist=open(srcDir + "/SC_AUTO_test.nl.v","r")
	lines=list(r_netlist.readlines())
	w_netlist=open(srcDir + "/SC_AUTO.nl.v","w")
	N2 = ' '
	N3 = ' '

	P2 = 'low'
	P3 = 'low'
	vss2 = 'VSS'
	vdd2 = 'VDD'
	vss3 = 'VSS'
	vdd3 = 'VDD'
	if CON == 0.111 or CON == 0.101 or CON == 0.011 or CON == 0.001:
		N2 = ' '
		N3 = ' '
		if CON == 0.111 or CON == 0.011:
			P2 = 'high'
			vss2 = 'VOUT'
			vdd2 = 'VDD'
		else:
			P2 = 'low'
			vss2 = 'VSS'
			vdd2 = 'VOUT'
		if CON == 0.111 or CON == 0.101:
			P3 = 'high'
			vss3 = 'VOUT2'
			vdd3 = 'VDD'
		else:
			P3 = 'low'
			vss3 = 'VSS'
			vdd3 = 'VOUT2'
	elif CON == 0.11 or CON == 0.01 :
		N2 = ' '
		N3 = '//'
		if CON == 0.11:
			P2 = 'high'			
			vss2 = 'VOUT'
			vdd2 = 'VDD'

		else:
			P2 = 'low'
			vss2 = 'VSS'
			vdd2 = 'VOUT'


	elif CON == 0.1:
		N2 = '//'
		N3 = '//'
	else:
		print('stage error')	


	
	netmap1=function.netmap() #modify here
	netmap1.get_net('c1',aux1,1,PD,1)
	netmap1.get_net('ni',None,1,PD,1)
	netmap1.get_net('s2',N2,1,2*PD,1)
	netmap1.get_net('c2',aux1,1,2*PD,1)
	netmap1.get_net('u2',P2,1,2*PD,1)
	netmap1.get_net('nj',None,1,2*PD,1)
	netmap1.get_net('g2',vss2,1,2*PD,1)
	netmap1.get_net('d2',vdd2,1,2*PD,1)
	netmap1.get_net('s3',N3,1,4*PD,1)
	netmap1.get_net('c3',aux1,1,4*PD,1)
	netmap1.get_net('u3',P3,1,4*PD,1)
	netmap1.get_net('nk',None,1,4*PD,1)
	netmap1.get_net('g3',vss3,1,4*PD,1)
	netmap1.get_net('d3',vdd3,1,4*PD,1)
	for line in lines:
		netmap1.printline(line,w_netlist)


