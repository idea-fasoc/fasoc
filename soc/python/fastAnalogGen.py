import sys  # exit function
import shutil  # filesystem manipulation
import os  # filesystem manipulation
import json  # json parsing
import subprocess  # process
import zipfile
from subprocess import call

from checkDB import checkDB
from jsonXmlGenerator import jsonXmlGenerator

def fastAnalogGen(module,configJson,databaseDir,outputDir,inputDir,ipXactDir,fasoc_dir,jsnDir,args_platform,args_mode,args_database,units):

  if module["generator"] in configJson["generators"] and "rtl" not in module["generator"]:

#---------------------------------------------------------------------------------------
# Generate analog block      
    print(module["module_name"] + " is going to be generate")
    specFilePath = os.path.join(inputDir, module["module_name"] + ".spec")
    outputSpec = module
    if "instance_name" in outputSpec:
      del outputSpec["instance_name"]
    with open(specFilePath, "w") as specfile:
      json.dump(outputSpec, specfile, indent=True)

    try:
      cmd1 = os.path.join(fasoc_dir,configJson["generators"][module["generator"]]["path"])
    except KeyError:
      print("Please specify path for module: " + module["module_name"] + "instance: " + module["instance_name"])
    cmd = cmd1 + " --specfile " + specFilePath + " --output " + outputDir + " --platform " + args_platform + " --mode " + args_mode
    print("Launching: ", cmd)
    
    try:
      ret = subprocess.check_call([cmd1,"--specfile",specFilePath,"--output",outputDir,"--platform",args_platform,"--mode",args_mode])
      if ret:
        print("Error: Command returned error: " + subprocess.CalledProcessError)
        sys.exit(1)
    except:
      print ("Error/Exception occurred while running command:", sys.exc_info()[0])
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# Add to database/cache
    if args_database == 'add':
      try:
        os.makedirs(os.path.join(databaseDir,'ZIP'))
        print("Directory " + os.path.join(databaseDir,'ZIP') +  " Created in the database") 
      except FileExistsError:
        print("Directory " + os.path.join(databaseDir,'ZIP') + " already exists in the database")
      
      if not os.path.exists(os.path.join(databaseDir,"DB_mem.txt")):
        with open(os.path.join(databaseDir,"DB_mem.txt"), 'w') as DBetxt:
          DBetxt.write('0')

      with open(os.path.join(databaseDir,"DB_mem.txt"),'r') as DBetxt:
        DBNumber=DBetxt.readlines()
      intDBNumber=int((DBNumber[0].split('\n'))[0])
      with zipfile.ZipFile(os.path.join(databaseDir,'ZIP',module["module_name"] + str(intDBNumber) + '.zip'), 'w') as myzip:
        for file in os.listdir(outputDir):
          if not '.xml' in file:   
            myzip.write(os.path.join(outputDir,file),file)

      try:
        os.makedirs(os.path.join(databaseDir,'JSN',module["generator"]))
        print("Directory " + os.path.join(databaseDir,'JSN',module["generator"]) +  " Created in the database") 
      except FileExistsError:
        print("Directory " + os.path.join(databaseDir,'JSN',module["generator"]) + " already exists in the database")

      shutil.copy(os.path.join(outputDir,module['module_name'] + '.json'),os.path.join(databaseDir,'JSN',module["generator"],module["module_name"] + str(intDBNumber) + '.json'))

      intDBNumber += 1
      with open(os.path.join(databaseDir,"DB_mem.txt"), 'w') as DBetxt:
          DBetxt.write(str(intDBNumber))
    moduleIsGenerator = True
#---------------------------------------------------------------------------------------       

#---------------------------------------------------------------------------------------       
# Check if generator and database are done and make ipxact, and add json files to json folder
    jsonXmlGenerator(configJson["generators"][module["generator"]],module,units,outputDir,ipXactDir)
    postfixes = ['.db','.gds.gz','.json','.lef','.lib','.spi','.v','.cdl','.xml']
    for postfix in postfixes:
      if not os.path.exists(os.path.join(outputDir,module["module_name"] + postfix)):
        print(module["module_name"] + postfix + " does not exist")
    shutil.copy(os.path.join(outputDir,module["module_name"]+'.json'),jsnDir)
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
  else:
    moduleIsGenerator = False

  return moduleIsGenerator