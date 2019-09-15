###### resmap test ############
import HSPICE_mds
import matplotlib.pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import math as math 

#index=1       #exist:1 no:0
#num_meas=2     #measurements
#skip_line=2   #default titles


def gen_resultrf(ncell,ndrv,nfc,stg_start,stg_swp,Ncf,fcidx,num_meas,index,freq_cc,len_ncell):
	skip_line=2   #default titles
	num_var=nfc+ncell+1
	num_words=num_var+num_meas+1   #+1 is +alter# index not included
	il=0
	iw=1
	k=0
	icc=0
	n_cc=0
	rm=HSPICE_mds.resmap(stg_swp*3,num_words,index)
	#dvmap=[[0]*5]*(stg_swp*3)     # 3 is the number of 'cc' sweep
	dvmap=[]
	set_tb=0
	cnt=0
	for j in range(stg_swp):   #netlist
		for cc, freq in freq_cc[j].iteritems(): #testbench
			try:
				r_result=open('./HSPICE/DUMPrf_result/tbrf_%dring%d_osc%d_cc%d.mp0'%(ndrv,ncell,stg_start+j,cc),'r')
				dvmap.append([])
				dvmap[cnt].append(ndrv)
				dvmap[cnt].append(ncell)
				dvmap[cnt].append(stg_start+j)
				dvmap[cnt].append(cc)
				dvmap[cnt].append(nfc)
				dvmap[cnt].append(freq)
				#================================================================================================
				#    reading values, storing on rm.map 
				#================================================================================================
				for line in r_result.readlines():
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								if iw<num_words+index+1:
									rm.get_var(cnt,word)
								#	print("got %s"%(word))
								else:
									rm.add(cnt,word)
								iw+=1
					elif il>skip_line+round(float(num_words)/3+float(1)/3)-1:    #change here!!!
						words=line.split()
						for word in words:
							rm.add(cnt,word)
							iw+=1
					il+=1
				set_tb=1
				il=0
				iw=1
				k+=1
				cnt+=1
			except: 
				pass
			set_tb=0
			k=0
		
		
	print rm.vr
	print('dvmap='),
	print dvmap
	#print rm.vl
	#print rm.vl[1]
	#print freq_cc
		
	fc=0
	cc=0
	freq_per=0
	kacc=0
	kavg=0
	kidx=0
	icc=0	
	cc_d=0
	fc_d=0
	Kc_d=0
	Kc=0    ##const
	Nstg=0    
	rm2=HSPICE_mds.resmap(stg_swp*3,10,0)   #result map for cleaner data
#	for ntb in range(stg_swp):   #for all netlist
	#================================================================================================
	#    organizing data in rm.map and restoring it on rm2.map 
	#================================================================================================
	for ntb in range(len(dvmap)):   #for all mp0
		Nstg=dvmap[ntb][2] 
#		for Cc, freq in freq_cc[ntb-1].iteritems():
		rm2.get_var(ntb,'FC')
		rm2.get_var(ntb,'CC')
		rm2.get_var(ntb,'TW')
		rm2.get_var(ntb,'pn1meg')
		rm2.get_var(ntb,'perj')
		rm2.get_var(ntb,'rmsj')
#		rm2.get_var(ntb,'freq')
		rm2.get_var(ntb,'Kpn')
		rm2.get_var(ntb,'Kjt')
		rm2.get_var(ntb,'freq')
		rm2.get_var(ntb,'Nstg')
		#print ("ntb=%d"%(ntb))
		#for j in range(len(rm.vl[ntb+icc][0])):       # for all tuning word(testbench)
		for i in range(len(rm.vr)):       # for all variables
			if rm.vr[i][0:2]=='vf':   ###here!!!!
				fc=fc+float(rm.vl[ntb][i][icc])
			if rm.vr[i][0:2]=='vc':   ###here!!!!
				cc=cc+float(rm.vl[ntb][i][icc])
			if rm.vr[i][0:6]=='pn1meg':
				pn1meg=float(rm.vl[ntb][i][icc])	
			if rm.vr[i][0:4]=='perj':
				perj=float(rm.vl[ntb][i][icc])
			if rm.vr[i][0:4]=='rmsj':
				rmsj=float(rm.vl[ntb][i][icc])
		rm2.add(ntb,fc)			
		rm2.add(ntb,cc)			
		rm2.add(ntb,cc*Ncf+fc)			
		rm2.add(ntb,pn1meg)			
		rm2.add(ntb,perj)
		rm2.add(ntb,rmsj)
#		rm2.add(ntb,freq)
		#rm2.add(ntb,(10**(pn1meg/20))/freq/freq)
		#rm2.add(ntb,pn1meg+10*math.log10((stg_start+ntb)**2/(ndrv+cc)))
		rm2.add(ntb,10**(pn1meg/10)*(Nstg)**2.9/(ndrv+cc))   #Kpn
		#rm2.add(ntb,10**(pn1meg/10)/(freq**2)*(ndrv+cc))
		rm2.add(ntb,rmsj**2*(ndrv+cc)**2/Nstg)   #Kjitter
		rm2.add(ntb,dvmap[ntb][5])   #frequency
		rm2.add(ntb,Nstg)
		fc=0
		cc=0
		#print('icc=%d'%(icc))
	#	icc+=1
	#icc=0
	i=0
	#=======================================================================
	#  removing blanks in rm2 (due to the rf test errors...)
	#=======================================================================				
	for j in rm2.vl:
		if j[0]==None:
			i+=1
	
	for k in range(i):
		rm2.vl.remove([None,None,None,None,None,None,None,None])

	for k in range(stg_swp):
		for i in rm2.vl:
			if i[7][0]==stg_start+k:
				print i
	#=======================================================================
	# print the constants Kpn, Kjt 
	#=======================================================================				
	print('frequency,perJ,rmsJ,Nstg=')
	for j in rm2.vl:
		print j[8],
		print j[4][0],
		print j[5][0],
		print j[9]	
	#print rm2.vl
	print('end result_rf')

#================================================================================================
#    function for reading .pn0 file 
#================================================================================================
def gen_printpn(ncell,ndrv,nfc,stg_start,stg_swp,Kg,freq_cc):
	skip_line=3   #default titles
	num_words=4   # freq / phase noise 
	il=0
	iw=1
	k=0
	icc=0
	n_cc=0
	index=0
	rm=HSPICE_mds.resmap(stg_swp*3,num_words,index)
	#dvmap=[[0]*5]*(stg_swp*3)     # 3 is the number of 'cc' sweep
	dvmap=[]  #design-variable map
	set_tb=0
	cnt=0
	#================================================================================================
	#    reading results with name of "tbrf_XXringXX_oscX(X)_ccX.printpn0 
	#================================================================================================
	for j in range(stg_swp):   #netlist
		for cc, freq in freq_cc[j].iteritems(): #testbench
			try:
				r_result=open('./HSPICE/DUMPrf_result/tbrf_%dring%d_osc%d_cc%d.printpn0'%(ndrv,ncell,stg_start+j,cc),'r')
				#print('found tbrf_%dring%d_osc%d_cc%d.printpn0'%(ndrv,ncell,stg_start+j,cc))
				dvmap.append([])
				dvmap[cnt].append(ndrv)         #0
				dvmap[cnt].append(ncell)        #1
				dvmap[cnt].append(stg_start+j)  #2
				dvmap[cnt].append(cc)		#3
				dvmap[cnt].append(nfc)		#4
				dvmap[cnt].append(freq)		#5
				#================================================================================================
				#    reading values and store in rm.map 
				#================================================================================================
				for line in r_result.readlines():
					if set_tb==0:
						if il>skip_line-1:
							words=line.split()
							for word in words:
								if iw<num_words+index+1:
									rm.get_var(cnt,word)
								#	print("got %s"%(word))
								else:
									rm.add(cnt,word)
								iw+=1
					elif il>skip_line:    #change here!!!
						words=line.split()
						for word in words:
							rm.add(cnt,word)
							iw+=1
					il+=1
				set_tb=1
				il=0
				iw=1
				k+=1
				cnt+=1
			except:
				print('failed to find tbrf_%dring%d_osc%d_cc%d.printpn0'%(ndrv,ncell,stg_start+j,cc))
			set_tb=0
			k=0
		
		
	print('printpn dvmap='),
	print dvmap

	#print rm.vr
	#print rm.vl[0]
	#print rm.vl[1]
	#print freq_cc
		
	fc=0
	cc=0
	freq_per=0
	freq=0
	freq_d=0
	logDF=0
	kacc=0
	kavg=0
	kidx=0
	icc=0	
	cc_d=0
	fc_d=0
	Kc_d=0
	Kc=0    ##const
	Nstg=0 
	PN_slope=[None]*len(dvmap)
	PN_last=[]
	Fo_Fc_PN=[None]*len(dvmap)
	Kpn_last=[]
	PN_d=0
	logDPN=0 
	f0=0
	Fc_flag=0
	#================================================================================================
	#    organizing values from rm.map and re-store at rm2.map  
	#================================================================================================
	rm2=HSPICE_mds.resmap(len(dvmap),4,0)   #result map for cleaner data
	for ntb in range(len(dvmap)):   #for all mp0
		Nstg=dvmap[ntb][2]
		NI=dvmap[ntb][0]+dvmap[ntb][3]
		rm2.get_var(ntb,'Ndrv+Nc')
		rm2.get_var(ntb,'Nstg')
		rm2.get_var(ntb,'PN')
		rm2.get_var(ntb,'freq')  #frequency offset
		PN_slope[ntb]=[]
		Fo_Fc_PN[ntb]=[]
		for j in range(len(rm.vl[0][0])):        # for all values
			for i in range(len(rm.vr)):       # for all variables
				if rm.vr[i][0:5]=='HERTZ':   ###here!!!!
					freq=float(rm.vl[ntb][i][j])
				if rm.vr[i][0:2]=='BP':   ###here!!!!
					PN=float(rm.vl[ntb][i][j])
			rm2.add(ntb,NI)			
			rm2.add(ntb,Nstg)			
			rm2.add(ntb,10**(PN/10))			
			rm2.add(ntb,freq)
			if j!=0:
				logDF=np.log10(freq)-np.log10(freq_d)			
				logDPN=PN-PN_d
				PN_slope[ntb].append(freq)
				PN_slope[ntb].append(logDPN/logDF)
				#======= find corner frequency and PN at that point ======
				if Fc_flag==0 and logDPN/logDF>-25:
					Fo_Fc_PN[ntb].append(dvmap[ntb][5])
					Fo_Fc_PN[ntb].append(freq)
					Fo_Fc_PN[ntb].append(PN)
					Fc_flag=1 
			if j==len(dvmap)-1:
				PN_last.append(PN)
				f0=dvmap[ntb][5]  #center frequency
				#print NI,Nstg,f0
				#Kpn_last.append(10**(PN/10)*(Nstg)**3/(NI))
				Kpn_last.append(10**(PN/10)*float(NI**2)/(f0**3))


			freq_d=freq
			PN_d=PN	
		freq_d=0
		PN_d=0
		Fc_flag=0
	
	print('PN_slope='),
	print PN_slope[0]
	#print dvmap
	#================================================================================================
	#    calculate Jitter from fc, PN  
	#================================================================================================
	print('Fo_Fc_PN=')
	for i in range(len(Fo_Fc_PN)):
		print Fo_Fc_PN[i]
		Fout=Fo_Fc_PN[i][0]
		Fcorner=Fo_Fc_PN[i][1]
		PNcorner=Fo_Fc_PN[i][2]
			




	s_dvmap=[0]*len(dvmap)
	s_PN_last=[0]*len(PN_last)
	HSPICE_mds.sort_via(dvmap,PN_last,2,0)
	HSPICE_mds.sort_via(dvmap,Kpn_last,2,0)
	Kpn_avg=sum(Kpn_last)/len(Kpn_last)
	Emax=max(abs(max(Kpn_last)-Kpn_avg),abs(min(Kpn_last)-Kpn_avg))
	Emax=Emax/Kpn_avg*100
	print ('Kpn_avg=%e Errmax=%e%%'%(Kpn_avg,Emax))
	print freq_cc
	print('end')
	return Kpn_avg,Emax
