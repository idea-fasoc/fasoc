#======== write file ==========
import HSPICE_mds

def write_K(ncell,ndrv,nfc,Kg,Kg_err,dK,idK): 
	wrkg=open("./model/%ddco_K%d_val_fc%d.py"%(ndrv,ncell,nfc),"w")
	readf=open("./formats/dco_K_val.py","r")
	lines=list(readf.readlines())
	Kmap=HSPICE_mds.netmap()
	Kmap.get_net('kg',None,Kg,Kg,1)
	Kmap.get_net('ke',None,Kg_err,Kg_err,1)
	Kmap.get_net('dK',None,dK[0],dK[0],1)
	Kmap.get_net('iK',None,idK[0],idK[0],1)
	for i in range(1,len(dK)):
		Kmap.add_val('dK',None,dK[i],dK[i],1)
		Kmap.add_val('iK',None,idK[i],idK[i],1)
	for line in lines:
		Kmap.printline(line,wrkg)
