#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import subprocess  # process
import shutil
import errno
import os
designDir = r'/n/trenton/v/fayazi/testtesttest/myresolved_design.json'
designName = 'fasoc_test8'
socrates_installDir = r'/afs/eecs.umich.edu/cadre/projects/fasoc/soft/arm-socrates-1.3.0'
workplaceDir = r'/n/trenton/v/fayazi/testtesttest'
projectName = designName + '_socrates_proj'
ipxactDir = r'/n/trenton/v/fayazi/FASOC/fasoc/fasoc/SoC-Integration/test/ipxact'
projectDir = os.path.join(workplaceDir,projectName)
rubiDir = r'/n/trenton/v/fayazi/FASOC/fasoc/fasoc/SoC-Integration/rubi'
subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,
'--project', projectName,'--flow', 'AddNewProject'])
configuragtion = r'/n/trenton/v/fayazi/testtesttest/IDEA_ChecksCoherencyCheck.config'

for file in os.listdir(ipxactDir):
	shutil.copy(os.path.join(ipxactDir,file), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA4','APB4','r0p0_0','APB4_rtl.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite.xml'), projectDir)
shutil.copy(os.path.join(socrates_installDir,'catalog','busdefs','amba.com','AMBA3','AHBLite','r2p0_0','AHBLite_rtl.xml'), projectDir)

subprocess.call([socrates_installDir + '/socrates_cli', '-data', workplaceDir,'--project', projectName,
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_00_convert_json.rb?arg1='+designDir+'&arg2='+designName+'&arg3='+rubiDir+'/CLI_01_Create_Hier.rb&arg4='+rubiDir+'/CLI_02_Connect.rb',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_01_Create_Hier.rb',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_02_Connect.rb',
'--check',
'--result', projectDir+'/DRC.log',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_03_Report.rb?arg1='+designName+'&arg2='+projectDir+'/Design_Report.txt',
'--flow', 'RunScript', 'ScriptFile='+rubiDir+'/CLI_04_Generate.rb?arg1='+designName+'&arg2='+os.path.join(projectDir,'logical',designName)])