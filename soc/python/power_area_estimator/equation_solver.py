from scipy.optimize import fsolve
import math

def equations(p):
    #vin, imax = p
    #return (-78*vin + 3700*imax-2194*vin*imax-23410*imax**2+22.9*vin**3+716382*imax**3)
#vin, imax =  fsolve(equations, (0.9, 0.01))
#print (equations((vin, imax)))
	fnom = p
	return(3.7442024014121142e04 + -6.846677e-05*fnom + 2.229949e-14*fnom**2 + 3.062494e-23*fnom**3 + -1.706576e-50*(fnom**6) - 8424)
fnom = fsolve(equations, (512120593.997046))
print(equations(fnom))
print(fnom)