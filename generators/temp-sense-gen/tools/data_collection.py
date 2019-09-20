import os
genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

dir_name = 'run'
folders = os.listdir(genDir + "./%s"%(dir_name))
current = os.getcwd()
print("Temp,Frequency,Power,Error")
#print(current)
for folder in folders:
	os.chdir("%s/%s/%s"%(current,dir_name,folder))
	os.system("source cal_result")
for folder in folders:
	f = open("%s/%s/%s/code_result_with_error"%(current,dir_name,folder),'r')
	data = f.read()
	print(data)
