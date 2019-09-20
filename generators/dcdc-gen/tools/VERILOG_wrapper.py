#======== Verilog wrapper ==========
import function
import TEMP_netlist

print("Number of INV(odd number):")
ninv=int(input())
print("Number of HEADER:")
nhead=int(input())
print("INV:{0} HEADER:{1}".format(ninv,nhead))
aux1 = 'NAND2X1HVT_ISOVDD'
aux2 = 'INVX1HVT_ISOVDD'
aux3 = 'BUFX1HVT_ISOVDD'
aux4 = 'BUFX8HVT_ISOVDD'
aux5 = 'HEADERX1HVT'


TEMP_netlist.gen_temp_netlist(ninv,nhead,aux1,aux2,aux3,aux4,aux5)
