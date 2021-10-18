#=============================================================
#	modules for HSPICE sim
#=============================================================

#=============================================================
#	varmap definition          				
#------------------------------------------------------------- 
#	This class is to make combinations of given variables 
#	mostly used for testbench generation     					
#-------------------------------------------------------------					
#	Example:  				
#	varmap1=HSPICE_varmap.varmap(4) %%num of var=4 
#	varmap1.get_var('vdd',1.5,1.8,0.2) %%vdd=1.5:0.2:1.8
#	varmap1.get_var('abc', ........ %%do this for 4 var 
#	varmap1.cal_nbigcy()             %%end of var input
#	varmap1.combinate  %%returns variable comb 1 by 1  
#=============================================================

class varmap:
	def __init__(self):
		self.n_smlcycle=1
		self.last=0
		#self.smlcy=1
		self.smlcy=0
		self.vv=0
		self.vf=1
		self.nvar=0

	def get_var(self,name,start,end,step):
		if self.nvar==0:
			self.map=[None]
			self.comblist=[None]
			self.flag=[None]
		else:
			self.map.append(None)
			self.comblist.append(None)
			self.flag.append(None)
		self.map[self.nvar]=list([name])
		self.flag[self.nvar]=(name)
		self.comblist[self.nvar]=list([name])
		self.nswp=int((end-start)//step+1)
		for i in range(1,self.nswp+1):
			self.map[self.nvar].append(start+step*(i-1))
		self.nvar+=1

	def add_val(self,flag,start,end,step):
		varidx=self.flag.index(flag)
		if start!=None:
			nval=int((end-start+step/10)//step+1)
			for i in range(1,nval+1):
				self.map[varidx].append(start+step*(i-1))
		else:
			for i in range(1,step+1):
				self.map[varidx].append(end)

	def cal_nbigcy(self):
		self.bias=[1]*(len(self.map))
		for j in range(1,len(self.map)+1):
			self.n_smlcycle=self.n_smlcycle*(len(self.map[j-1])-1)
		self.n_smlcycle=self.n_smlcycle*len(self.map)

	def increm(self,inc):			#increment bias
		self.bias[inc]+=1
		if self.bias[inc]>len(self.map[inc])-1:
			self.bias[inc]%len(self.map[inc])-1

	def check_end(self,vf):     #When this is called, it's already last stage of self.map[vf]
		self.bias[vf]=1
#		if vf==0 and self.bias[0]==len(self.map[0])-1:
#			return 0	
		if self.bias[vf-1]==len(self.map[vf-1])-1:   #if previous column is last element
			self.check_end(vf-1)
		else:
			self.bias[vf-1]+=1
			return 1

	def combinate(self):
#		print self.map[self.vv][self.bias[self.vv]]
		self.smlcy+=1
		if self.vv==len(self.map)-1:   #last variable
			for vprint in range(0,len(self.map)):   #fill in the current pointer values
				self.comblist[vprint].append(self.map[vprint][self.bias[vprint]])
				#print self.map[vprint][self.bias[vprint]]
			if self.bias[self.vv]==len(self.map[self.vv])-1:  #last element
				if self.smlcy<self.n_smlcycle:
					self.check_end(self.vv)
					self.vv=(self.vv+1)%len(self.map)
					self.combinate()
				else:
					pass
			else:
				self.bias[self.vv]+=1
				self.vv=(self.vv+1)%len(self.map)
				self.combinate()
		else:
			self.vv=(self.vv+1)%len(self.map)
			self.combinate()
	
	def find_comb(self,targetComb):  #function that returns the index of certain combination
		if len(self.comblist)!=len(targetComb):
			print('the length of the list doesnt match')
		else:
			for i in range(1,len(self.comblist[0])):
				match=1
				for j in range(len(self.comblist)):
					match=match*(self.comblist[j][i]==targetComb[j])
				if match==1:
					return i	 
							
#=============================================================
#	netmap  				
#-------------------------------------------------------------					
#	This class is used for replacing lines   
#	detects @@ for line and @ for nets 
#-------------------------------------------------------------					
#	Example:	
#	netmap1.get_net('ab','NN',1,4,1) %flag MUST be 2 char
#	netmap2.get_net('bc','DD',2,5,1) %length of var must match
#	netmap2.get_net('bc','DD',None,5,9) repeat DD5 x9  
#	netmap2.get_net('bc','DD',None,None,None) write only DD  
#	netmap2.get_net('bc','DD',None,5,None) write only DD for 5 times  
#	!!caution: do get_var in order, except for lateral prints 
#	which is using @W => varibales here, do get_var at last 
#	for line in r_file.readlines(): 
#	netmap1.printline(line,w_file)
# 	printline string added 
#=============================================================


class netmap:
	def __init__(self):
		self.nn=0
		self.pvar=1
		self.cnta=0
		self.line_nvar=0      # index of last variable for this line
		self.nxtl_var=0      # index of variable of next line
		self.ci_at=-5
		self.ci_and=-50

	#try has been added to reduce unnecessary "add_val" usage: but it might produce a problem when the user didn't know this(thought that every get_net kicks old value out)	
	def get_net(self,flag,netname,start,end,step):       #if start==None: want to repeat without incrementation(usually for tab) (end)x(step) is the num of repetition 
		try:  #incase it's already in the netmap => same as add_val
			varidx=self.flag.index(flag)
			if start!=None:
				try:
					nval=abs(int((end-start+step/10)//step+1))
					for i in range(1,nval+1):
						self.map[varidx].append(start+step*(i-1))
				except:
					self.map[varidx].append(start)
			else:
				for i in range(1,step+1):
					self.map[varidx].append(end)
		except:  #registering new net
			if self.nn==0:
				self.map=[None]
				self.flag=[None]
				self.name=[None]
				self.nnet=[None]
				self.stringOnly=[None]
			else:
				self.map.append(None)
				self.name.append(None)
				self.flag.append(None)
				self.nnet.append(None)
				self.stringOnly.append(None)
			if netname==None:
				self.name[self.nn]=0
			else:
				self.name[self.nn]=1
			self.map[self.nn]=list([netname])
			self.flag[self.nn]=(flag)
			if start!=None and start!='d2o' and start!='d2oi':    #normal n1 n2 n3 ...
				try: 
					self.nnet[self.nn]=int((end-start+step/10)//step+1)
					for i in range(1,self.nnet[self.nn]+1):
						self.map[self.nn].append(start+step*(i-1))
				except:
					self.map[self.nn].append(start)
					
			elif start=='d2o':                    #decimal to binary
				for i in range(0,end):
					if step-i>0:
						self.map[self.nn].append(1)
					else:
						self.map[self.nn].append(0)
					i+=1
			elif start=='d2oi':                    #decimal to thermal inversed 
				for i in range(0,end):
					if step-i>0:
						self.map[self.nn].append(0)
					else:
						self.map[self.nn].append(1)
					i+=1
			elif start==None and end==None and step==None:  #write only string
				self.stringOnly[self.nn]=1
				self.map[self.nn].append(netname) #this is just to make len(self.map[])=2 to make it operate 
			elif self.name[self.nn]!=None and start==None and end!=None and step==None:  #repeatedely printing string (write name x end)
				for i in range(1,end+1):
					self.map[self.nn].append(netname)
			else:					# start==None : repeat 'end' for 'step' times
				for i in range(1,step+1):
					self.map[self.nn].append(end)
	#			self.map[self.nn]=[None]*step
	#			for i in range(1,self.nnet[self.nn]+1):
	#				self.map[self.nn][i]=None
			self.nn+=1
			#print self.map

	def add_val(self,flag,netname,start,end,step):
		varidx=self.flag.index(flag)
		if start!=None:
			nval=int((end-start+step/10)//step+1)
			for i in range(1,nval+1):
				self.map[varidx].append(start+step*(i-1))
		else:
			for i in range(1,step+1):
				self.map[varidx].append(end)

	def printline(self,line,wrfile):
		if line[0:2]=='@@':
			#print('self.ci_at=%d'%(self.ci_at))
			self.nline=line[3:len(line)]
			self.clist=list(self.nline)       #character list
			for iv in range (1,len(self.map[self.nxtl_var])):
				for ci in range(0,len(self.clist)):
					if (ci==self.ci_at+1 or ci==self.ci_at+2) and ci!=len(self.clist)-1:
						pass
					elif self.clist[ci]=='@':
						try:
							varidx=self.flag.index(self.clist[ci+1]+self.clist[ci+2])
							#print self.cnta
							self.cnta+=1
							self.line_nvar+=1
							if self.stringOnly[varidx]==1:
								wrfile.write(self.map[varidx][0])
								self.ci_at=ci	
							else:	
								#print ('flag=')	
								#print (self.clist[ci+1]+self.clist[ci+2])
								#print (self.map[varidx])
								#print (self.pvar)
								if self.name[varidx]:
									wrfile.write(self.map[varidx][0])
								if type(self.map[varidx][self.pvar])==str: 
									wrfile.write('%s'%(self.map[varidx][self.pvar]))      #modify here!!!!
								if type(self.map[varidx][self.pvar])==float: 
									wrfile.write('%e'%(self.map[varidx][self.pvar]))      #modify here!!!!
									#wrfile.write('%.2f'%(self.map[varidx][self.pvar]))      #modify here!!!!
								elif type(self.map[varidx][self.pvar])==int: 
									wrfile.write('%d'%(self.map[varidx][self.pvar]))
								#elif type(self.map[varidx][self.pvar])==str: 
								#	wrfile.write('%s'%(self.map[varidx][self.pvar]))
								self.ci_at=ci
						except:
							print("%s not in netmap!"%(self.clist[ci+1]+self.clist[ci+2]))
							wrfile.write(self.clist[ci])
					elif ci==len(self.clist)-1:     #end of the line
						if self.pvar==len(self.map[self.nxtl_var+self.line_nvar-1])-1:   #last element
							self.pvar=1
							self.nxtl_var=self.nxtl_var+self.line_nvar
							self.line_nvar=0
							self.cnta=0
							self.ci_at=-6
							#print('printed all var for this line, %d'%(ci))
						else:
							self.pvar+=1
							self.line_nvar=self.cnta
							self.line_nvar=0
							#print ('line_nvar= %d'%(self.line_nvar))
							self.cnta=0 
						wrfile.write(self.clist[ci])
					else:
						wrfile.write(self.clist[ci])
		elif line[0:2]=='@W':  #lateral writing
			#print('found word line')
			self.nline=line[3:len(line)]
			self.clist=list(self.nline)
			for ci in range(0,len(self.clist)):
				if (ci==self.ci_at+1 or ci==self.ci_at+2):
					pass
				elif self.clist[ci]=='@':
					varidx=self.flag.index(self.clist[ci+1]+self.clist[ci+2])
					for iv in range(1,len(self.map[varidx])):
						if self.name[varidx]:
							wrfile.write(self.map[varidx][0])
						if type(self.map[varidx][iv])==int:
							wrfile.write('%d	'%(self.map[varidx][iv])) #this is added for edit pin
						elif type(self.map[varidx][iv])==float:
							wrfile.write('%.1f	'%(self.map[varidx][iv]))
					self.ci_at=ci
				else:
					wrfile.write(self.clist[ci])
			self.ci_at=-5
		elif line[0:2]=='@E':  #lateral writing for edit pin
			#print('found word line')
			self.nline=line[3:len(line)]
			self.clist=list(self.nline)
			for ci in range(0,len(self.clist)):
				if (ci==self.ci_at+1 or ci==self.ci_at+2):
					pass
				elif self.clist[ci]=='@':
					varidx=self.flag.index(self.clist[ci+1]+self.clist[ci+2])
					for iv in range(1,len(self.map[varidx])):
						if self.name[varidx]:
							wrfile.write(self.map[varidx][0])
						if type(self.map[varidx][iv])==int:
							wrfile.write('%d] '%(self.map[varidx][iv])) #this is added for edit pin
						elif type(self.map[varidx][iv])==float:
							wrfile.write('%.1f	'%(self.map[varidx][iv]))
					self.ci_at=ci
				else:
					wrfile.write(self.clist[ci])
			self.ci_at=-5
		elif line[0:2]=='@C':  # cross lateral writing
			#print('found word line')
			self.nline=line[3:len(line)]
			self.clist=list(self.nline)
			for ci in range(0,len(self.clist)):
				if (ci==self.ci_at+1 or ci==self.ci_at+2 or ci==self.ci_and+1 or ci==self.ci_and+2 or ci==self.ci_and+3 or ci==self.ci_and+4):
					pass
				elif self.clist[ci]=='@':
					varidx=self.flag.index(self.clist[ci+1]+self.clist[ci+2])
					for iv in range(1,len(self.map[varidx])):
						if self.name[varidx]:
							wrfile.write(self.map[varidx][0])
						if type(self.map[varidx][iv])==int:
							wrfile.write('%d '%(self.map[varidx][iv])) #this is added for edit pin
						elif type(self.map[varidx][iv])==float:
							wrfile.write('%.1f	'%(self.map[varidx][iv]))
					self.ci_at=ci
				elif self.clist[ci]=='&':
					varidx1=self.flag.index(self.clist[ci+1]+self.clist[ci+2])
					varidx2=self.flag.index(self.clist[ci+3]+self.clist[ci+4])
					for iv in range(1,len(self.map[varidx1])):
						if type(self.map[varidx1][iv])==int:
							wrfile.write('%d '%(self.map[varidx1][iv])) #this is added for edit pin
						elif type(self.map[varidx1][iv])==float:
							wrfile.write('%e '%(self.map[varidx1][iv]))
						if type(self.map[varidx2][iv])==int:
							wrfile.write('%d '%(self.map[varidx2][iv])) #this is added for edit pin
						elif type(self.map[varidx2][iv])==float:
							wrfile.write('%e '%(self.map[varidx2][iv]))
					self.ci_and=ci
				else:
					wrfile.write(self.clist[ci])
			self.ci_at=-5
		elif line[0:2]=='@S':
			self.nline=line[3:len(line)]
			self.clist=list(self.nline)
			for ci in range(0,len(self.clist)):
				if (ci==self.ci_at+1 or ci==self.ci_at+2):
					pass
				elif self.clist[ci]=='@':
					varidx=self.flag.index(self.clist[ci+1]+self.clist[ci+2])
					wrfile.write(self.map[varidx][0])
					self.ci_at=ci
				else:
					wrfile.write(self.clist[ci])
			self.ci_at=-5
				
		else:
			wrfile.write(line)


#=============================================================
#	resmap   				
#-------------------------------------------------------------
#	This class is used to deal with results   
#	detects @@ for line and @ for nets
#-------------------------------------------------------------
#	EXAMPLE:			
#	netmap1=netmap(2) %input num_var 
#	netmap1.get_var('ab','NN',1,4,1) %flag MUST be 2 char 
#	netmap2.get_var('bc','DD',2,5,1) %length of var must match
#	for line in r_file.readlines(): 
#	netmap1.printline(line,w_file) 
#	self.tb[x][y][env[]]     			
#=============================================================

class resmap:
	def __init__(self,num_tb,num_words,index):           #num_words includes index
		self.tb=[None]*num_tb
		self.tbi=[None]*num_tb
		self.vl=[None]*num_tb
		self.vlinit=[None]*num_tb
		self.svar=[None]*num_tb
		self.index=index
		self.nenv=0
		self.num_words=num_words
		self.vr=[None]*(num_words+index)             #one set of variables per plot 
		self.vidx=[None]*(num_words+index)
		self.env=[None]*(num_words+index)
#		self.vl=[None]*(num_words+index)             #one set of variables per plot 
		for itb in range(0,len(self.tb)):
		#	self.tb[itb].vr=[None]*(num_words+index)
			self.tbi[itb]=0      #index for counting vars within tb
			self.vl[itb]=[None]*(num_words+index)
			self.vlinit[itb]=[0]*(num_words+index)
	def get_var(self,ntb,var):
		self.vr[self.tbi[ntb]]=(var) # variable
#		self.vl[ntb][self.tbi[ntb]]=list([None])
		self.tbi[ntb]+=1
		if self.tbi[ntb]==len(self.vr):    #????????
			self.tbi[ntb]=0                

	def add(self,ntb,value):
		if self.vlinit[ntb][self.tbi[ntb]]==0:   #initialization
			self.vl[ntb][self.tbi[ntb]]=[value] # value
			self.vlinit[ntb][self.tbi[ntb]]+=1
		else:
			self.vl[ntb][self.tbi[ntb]].append(value) # value
		self.tbi[ntb]=(self.tbi[ntb]+1)%len(self.vr)

	def plot_env(self,ntb,start,step,xvar,xval):            #setting plot environment: if ntb=='all': x axis is in terms of testbench 
		if ntb=='all':
			self.nenv+=1
			self.xaxis=[None]*len(self.tb)
			for i in range(0,len(self.tb)):
				self.xaxis[i]=start+i*step
			self.vidx[self.nenv]=self.vr.index(xvar)
			#print self.vl[0][self.vidx[self.nenv]]
			self.env[self.nenv]=[i for (i,x) in enumerate(self.vl[0][self.vidx[self.nenv]]) if x=='%s'%(xval)]
		else:
			self.nenv+=1
			self.xaxis=[None]  #one output
			self.xaxis=[start]
			self.vidx[self.nenv]=self.vr.index(xvar)
			self.env[self.nenv]=[i for (i,x) in enumerate(self.vl[0][self.vidx[self.nenv]]) if x=='%s'%(xval)]	
		
	def rst_env(self):
		self.vidx[self.nenv]=None
		self.env[self.nenv]=0
		self.nenv=0
		#print self.vl[0][self.vidx[self.nenv]]

	
	def plot_y(self,yvar):
		self.yidx=self.vr.index(yvar)
		#print ('yidx=%d'%(self.yidx))
		#print self.vl[0][self.yidx][self.env[self.nenv][0]]
		self.yaxis=[None]*len(self.xaxis)
		for xx in range(0,len(self.xaxis)):
			self.yaxis[xx]=self.vl[xx][self.yidx][self.env[self.nenv][0]]
		#plt.plot(self.xaxis,self.yaxis)
		#plt.ylabel(self.vr[self.yidx])	


	def sort(self,var):
		varidx=self.vr.index(var)
		for k in range(len(self.vl)):    #all testbenches
			self.svar[k]={} #define dict 
			for i in range(len(self.vl[0][0])):    #all values
				self.svar[k][self.vl[k][varidx][i]]=[]	
				for j in range(len(self.vr)):    #all variables
					if j!=varidx:
						self.svar[k][self.vl[k][varidx][i]].append(self.vl[k][j][i])	


#=============================================================
#	sort   				
#-------------------------------------------------------------
#	This function sorts 2D-list according to given index value  
#	outputs the sorted 2D-list  
#-------------------------------------------------------------
#	EXAMPLE:			
#=============================================================

def sort_via(list_ind,list_vic,index,i):
	index=int(index)
	i=int(i)
	if len(list_ind)!=len(list_vic):
		print('lengths of two lists dont match')
	else:
		#print('%d th'%(i))
		t_ind=0
		t_vic=0
		if i<len(list_ind)-1 and i>=0:
			if list_ind[i][index]>list_ind[i+1][index]:
				#print list_ind
				#print list_vic
				#print('switch %d from %d and %d'%(i,len(list_ind),len(list_vic)))
				t_ind=list_ind[i]
				t_vic=list_vic[i]
				list_ind[i]=list_ind[i+1]
				list_vic[i]=list_vic[i+1]
				list_ind[i+1]=t_ind
				list_vic[i+1]=t_vic
				i=i-1
				sort_via(list_ind,list_vic,index,i)
			else:
				#print('pass %d'%(i))
				i+=1
				sort_via(list_ind,list_vic,index,i)
		elif i<0:
			i+=1
			sort_via(list_ind,list_vic,index,i)
		elif i==len(list_ind)-1:
			#print('came to last')
			#print list_ind
			#print list_vic
			return list_ind, list_vic	

#=============================================================
#	sort 1D		
#-------------------------------------------------------------
#	This function sorts 1D-list according to given index value  
#	outputs the sorted 1D-list  
#-------------------------------------------------------------
#	EXAMPLE:	
#	a=[3,2,1], b=[1,2,3]	
#	a,b=sort_via_1d(a,b,0)
#	print a => [1,2,3]	
#	print b => [3,2,1]	
#=============================================================

def sort_via_1d(list_ind,list_vic,i):
	i=int(i)
	if len(list_ind)!=len(list_vic):
		print('lengths of two lists dont match')
	else:
		#print('%d th'%(i))
		t_ind=0
		t_vic=0
		if i<len(list_ind)-1 and i>=0:
			if list_ind[i]>list_ind[i+1]:
				#print list_ind
				#print list_vic
				#print('switch %d from %d and %d'%(i,len(list_ind),len(list_vic)))
				t_ind=list_ind[i]
				t_vic=list_vic[i]
				list_ind[i]=list_ind[i+1]
				list_vic[i]=list_vic[i+1]
				list_ind[i+1]=t_ind
				list_vic[i+1]=t_vic
				i=i-1
				sort_via_1d(list_ind,list_vic,i)
			else:
				#print('pass %d'%(i))
				i+=1
				sort_via_1d(list_ind,list_vic,i)
		elif i<0:
			i+=1
			sort_via_1d(list_ind,list_vic,i)
		elif i==len(list_ind)-1:
			#print('came to last')
			#print list_ind
			#print list_vic
			return list_ind, list_vic	

def sort_via_1d_mult(list_ind,*list_vics):
	i=int(0)
	for list_vic in list_vics:
		list_ind_temp=list(list_ind)
		sort_via_1d(list_ind_temp,list_vic,0)	
	sort_via_1d(list_ind,list_ind,0)
#=============================================================
#	mM   				
#-------------------------------------------------------------
#	This function picks min, Max,  of 1-D list  
#	outputs min, Max, step  
#-------------------------------------------------------------
#	EXAMPLE:			
#=============================================================



def mM(inp_list):
	min_item=0
	max_item=0
	step_item=0
	reg_item=0
	err_step=0
	cnt=0
	for item in inp_list:
		if cnt==0:
			min_item=item
			max_item=item
		else:
			if min_item>item:
				min_item=item
			if max_item<item:
				max_item=item
			#if cnt>1 and step_item!=abs(item-reg_item):
			#	print('step is not uniform')
			#	err_step=1
			#	print reg_item-item
			#else: 	
			#	step_item=abs(item-reg_item)
		reg_item=item
		cnt+=1
	if err_step==0:
		return min_item,max_item
#	else:
#		print('step error')	









