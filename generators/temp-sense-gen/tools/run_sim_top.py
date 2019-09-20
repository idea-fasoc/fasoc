import os
genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

dir_name='run'
folders = os.listdir(genDir + "./%s"%(dir_name))
current = os.getcwd()
#w_file4 = open("./run_sim_top","w")
for folder in folders:
	print(folder)
	os.chdir("%s/%s/%s"%(current,dir_name,folder))
	os.system("source run_sim")
