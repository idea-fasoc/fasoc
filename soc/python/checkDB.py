#!/usr/bin/env python3
#MIT License

#Copyright (c) 2018 The University of Michigan

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
import shutil
import os
import json  # json parsing
import zipfile
from modifyDBFiles import modifyDBFiles

def checkDB(moduleJson,databaseDir,outputDir,ipXactDir):
    genJson = moduleJson['generator']
    searchDir = os.path.join(databaseDir,'JSN',genJson)
    if 'specifications' in moduleJson:
        target_specsJson = moduleJson['specifications']

        if os.path.exists(searchDir):
            if len(os.listdir(searchDir)) != 0:
                for file in os.listdir(searchDir):
                    overlap_tag = True
                    with open(os.path.join(searchDir,file), 'r') as search_file:
                        srchJson = json.load(search_file)
                    if 'specifications' in srchJson:
                        srch_specifications= srchJson['specifications']

                        for target_specName, target_specVal in target_specsJson.items():

                            if target_specVal != "" and isinstance(target_specVal, str) != True:
                                if target_specName in srch_specifications:
                                    srch_specVal = srch_specifications[target_specName]

                                    if srch_specVal != "" and isinstance(srch_specVal, str) != True:
                                        if isinstance(target_specVal, dict):
                                            if "min" in target_specVal:
                                                if isinstance(srch_specVal, dict):
                                                    if srch_specVal["min"] < target_specVal["min"]:
                                                        overlap_tag = False
                                                        break
                                                else:
                                                    if srch_specVal < target_specVal["min"]:
                                                        overlap_tag = False
                                                        break 

                                            if "max" in target_specVal:
                                                if isinstance(srch_specVal, dict):
                                                    if srch_specVal["max"] > target_specVal["max"]:
                                                        overlap_tag = False
                                                        break
                                                else:
                                                    if srch_specVal > target_specVal["max"]:
                                                        overlap_tag = False
                                                        break

                                        else:
                                            if "min" in target_specName:
                                                if isinstance(srch_specVal, dict):
                                                    if srch_specVal["min"] < target_specVal:
                                                        overlap_tag = False
                                                        break
                                                else:
                                                    if srch_specVal < target_specVal:
                                                        overlap_tag = False
                                                        break
                                            elif "max" in target_specName:
                                                if isinstance(srch_specVal, dict):
                                                    if srch_specVal["max"] > target_specVal:
                                                        overlap_tag = False
                                                        break
                                                else:
                                                    if srch_specVal > target_specVal:
                                                        overlap_tag = False
                                                        break
                                                    
                                            else:

                                                if isinstance(srch_specVal, dict):
                                                    if srch_specVal["min"] != target_specVal:
                                                        overlap_tag = False
                                                        break
                                                    if srch_specVal["max"] != target_specVal:
                                                        overlap_tag = False
                                                        break
                                                else:
                                                    if srch_specVal != target_specVal:
                                                        overlap_tag = False
                                                        break                 

                        if overlap_tag:
                            found_Filename = os.path.join(databaseDir,'ZIP',(file.split('.'))[0]+'.zip')
                            if os.path.exists(found_Filename):
                                print(moduleJson['module_name'] + " has been found at the database")
                                zip_ref = zipfile.ZipFile(found_Filename, 'r')
                                zip_ref.extractall(outputDir)
                                zip_ref.close()
                                for output_file in os.listdir(outputDir):
                                    output_file_name = (output_file.split('.'))[0]
                                    postfix = (output_file.split(output_file_name))[-1]
                                    os.rename(os.path.join(outputDir,output_file),os.path.join(outputDir,moduleJson['module_name'] + postfix))
                                    modifyDBFiles(os.path.join(outputDir,moduleJson['module_name'] + postfix),postfix,moduleJson['module_name'],srchJson["module_name"])
                                #shutil.copy(os.path.join(outputDir,moduleJson['module_name'] + '.xml'),ipXactDir)
                                return True
                            else:#When there is no zipfile it means search was unsuccessfull
                                return False

                return False# when code reaches here it means it could not find the correct file
            else:#if the database is empty => search was unsuccessfull
                return False
        
        else:#If database does not exist it means search was unsuccessfull
            return False

    else:#If the target file has no specification, all files are acceptable
        if os.path.exists(searchDir):
            if len(os.listdir(searchDir)) != 0:
                with open(os.path.join(searchDir,os.listdir(searchDir)[0]), 'r') as search_file:
                    srchJson = json.load(search_file) 
                found_Filename = os.path.join(databaseDir,'ZIP',(os.listdir(searchDir)[0].split('.'))[0]+'.zip')
                if os.path.exists(found_Filename):
                    print(moduleJson['module_name'] + " has been found at the database")
                    zip_ref = zipfile.ZipFile(found_Filename, 'r')
                    zip_ref.extractall(outputDir)
                    zip_ref.close()
                    for output_file in os.listdir(outputDir):
                        output_file_name = (output_file.split('.'))[0]
                        postfix = (output_file.split(output_file_name))[-1]
                        os.rename(os.path.join(outputDir,output_file),os.path.join(outputDir,moduleJson['module_name'] + postfix))
                        modifyDBFiles(os.path.join(outputDir,moduleJson['module_name'] + postfix),postfix,moduleJson['module_name'],srchJson["module_name"])
                    #shutil.copy(os.path.join(outputDir,moduleJson['module_name'] + '.xml'),ipXactDir)
                    return True
                else:#When there is no zipfile it means search was unsuccessfull
                    return False

            else:#if the database is empty => search was unsuccessfull
                return False
        else:#If database does not exist it means search was unsuccessfull
            return False