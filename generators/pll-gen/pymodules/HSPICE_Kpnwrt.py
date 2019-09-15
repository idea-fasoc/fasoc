#------------------------------------------------------------------------------
# Write the PN related constant 
#------------------------------------------------------------------------------
import HSPICE_mds
import numpy as np 

def write_Kpn(ncell,ndrv,nfc,Kpn,Ekpn): 
	wrkg=open("./model/%ddco_Kpn%d_val_fc%d.py"%(ndrv,ncell,nfc),"w")
	readf=open("./formats/form_Kpn.py","r")
	lines=list(readf.readlines())
	Edb=10*np.log10(1+Ekpn/100)
	#print ('Edb='),
	#print Edb
	Kmap=HSPICE_mds.netmap()
	Kmap.get_net('Kp',None,Kpn,Kpn,1)
	Kmap.get_net('Ek',None,Ekpn,Ekpn,1)
	Kmap.get_net('Ed',None,float(Edb),float(Edb),1)
	for line in lines:
		Kmap.printline(line,wrkg)
