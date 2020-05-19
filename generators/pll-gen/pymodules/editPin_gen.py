# gen_floorplan
import sys
import getopt
import math
import subprocess as sp
import fileinput
import re
import os
import shutil
import numpy as np
import argparse
import json
sys.path.append('./../pymodules/')
import HSPICE_mds2

#Ndrv=1
#Ncc=24
#Nfc=10
#Nstg=16
def editPin_gen(Ndrv,Ncc,Nfc,Nstg,formatDir,version,wfile_name):
	nCC=Ncc*Nstg
	nFC=Nfc*Nstg
	nPout=Nstg*2
	
	#rfile=open(formatDir+'/form_floorplan_test.tcl','r')
	#rfile=open('ignore_form_floorplan.tcl','r')
	rfile=open(formatDir+'/form_ffdco_pre_place.tcl','r')
	rfile2=open(formatDir+'/form_ffdco_pre_place.tcl','r')
	wfile=open(wfile_name,'w')

	#========================================================================
	# Version 1
	#	for floor plan.tcl: spreading out the pin
	# 	this is the 1st version, with all the edge selection in the bottom,
	# 	which makes stg0 and stg7 too far
	#========================================================================
	if version==1:
		nm2=HSPICE_mds2.netmap()
		nm2.get_net('po',None,0,Nstg-1,1)
		nm2.get_net('no',None,0,Nstg-1,1)
		nm2.get_net('ep',None,0,Nstg-1,1)
		nm2.get_net('en',None,Nstg*2,Nstg*3-1,1)
		
		nm2.get_net('Po',None,Nstg,2*Nstg-1,1)
		nm2.get_net('No',None,Nstg,2*Nstg-1,1)
		nm2.get_net('Ep',None,Nstg,2*Nstg-1,1)
		nm2.get_net('En',None,3*Nstg,4*Nstg-1,1)
		
		lines=list(rfile.readlines())
		istg=0
		for line in lines:
			if line[0:2]=='@W': 
				nm1=HSPICE_mds2.netmap()
				nm1.get_net('f1','FC[',istg,istg+Nstg*(Nfc-1),Nstg)
				nm1.get_net('c1','CC[',istg,istg+Nstg*(Ncc-1),Nstg)
				nm1.printline(line,wfile)
				istg=istg+1
			else:
				nm2.printline(line,wfile)	
		
	
	#========================================================================
	# Version 2
	#	for floor plan.tcl: spreading out the pin
	# 	this is the 2nd version, with all the edge selection spread out,
	#	PH_P/N_out*, CLK_OUT are only concentrated in the bottom,
	#	all other pins are spread 4-side to reduce the delay mismatch between cells
	#========================================================================
	if version==2:
		Nedge_start=Nstg*2
		eps=int(Nstg/2) # edge_per_side per either N or P
		nm2=HSPICE_mds2.netmap()
		#--- distribute EDGE_SEL ---
		nm2.get_net('el',None,0,eps-1,1)
		nm2.get_net('eL',None,Nedge_start,Nedge_start+eps-1,1)
	
		nm2.get_net('et',None,eps,2*eps-1,1)
		nm2.get_net('eT',None,Nedge_start+eps,Nedge_start+2*eps-1,1)
	
		nm2.get_net('er',None,2*eps,3*eps-1,1)
		nm2.get_net('eR',None,Nedge_start+2*eps,Nedge_start+3*eps-1,1)
	
		#--- distribute PH_P_OUT, PH_N_OUT ---
		#if eps//2==eps/2: # eps is even
		nm2.get_net('ep',None,eps*3,eps*3+int(eps/2)-1,1)
		nm2.get_net('en',None,Nedge_start+eps*3,Nedge_start+eps*3+int(eps/2)-1,1)
		nm2.get_net('po',None,0,Nstg-1,1)
		nm2.get_net('no',None,0,Nstg-1,1)
		nm2.get_net('Po',None,Nstg,2*Nstg-1,1)
		nm2.get_net('No',None,Nstg,2*Nstg-1,1)
		nm2.get_net('Ep',None,int(eps*3.5),eps*4-1,1)
		nm2.get_net('En',None,Nedge_start+int(eps*3.5),Nedge_start+eps*4-1,1)
		#else: # eps is odd
		#	nm2.get_net('ep',None,eps*3,eps*3+int(eps/2)-1,1)   # 1 less 
		#	nm2.get_net('en',None,Nedge_start+eps*3,Nedge_start+eps*3+int(eps/2)-1,1) # 1 less
		#	nm2.get_net('Po',None,Nstg,2*Nstg-1,1)
		#	nm2.get_net('No',None,Nstg,2*Nstg-1,1)
		#	nm2.get_net('Ep',None,int(eps*3.5),eps*4-1,1) # 1 more
		#	nm2.get_net('En',None,Nedge_start+int(eps*3.5),Nedge_start+eps*4-1,1) # 1 more
		
		lines=list(rfile2.readlines())
		istg=0
		for line in lines:
			if line[0:2]=='@W': 
				nm1=HSPICE_mds2.netmap()
				nm1.get_net('f1','FC[',istg,istg+Nstg*(Nfc-1),Nstg)
				nm1.get_net('c1','CC[',istg,istg+Nstg*(Ncc-1),Nstg)
				nm1.printline(line,wfile)
				istg=istg+1
			else:
				nm2.printline(line,wfile)
	














	
