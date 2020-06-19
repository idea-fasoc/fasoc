import numpy as np
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from numpy.polynomial import Polynomial
import pandas as pd
import csv
import json
import os
import time
import heapq
from collections import defaultdict
import glob
import operator


import sys
import getopt
import math
import subprocess as sp
import fileinput
import re
import shutil
import argparse




#------------------------------------------------------------------------------
# Parse the command line arguments
#------------------------------------------------------------------------------
print("#----------------------------------------------------------------------")
print("# Parsing command line arguments...")
print("#----------------------------------------------------------------------")
print( sys.argv)

genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

head_tail_0 = os.path.split(os.path.abspath(genDir))
head_tail_1 = os.path.split(head_tail_0[0])
privateGenDir = os.path.relpath(os.path.join(genDir, '../../', 'private', head_tail_1[1], head_tail_0[1]))
print(head_tail_0)
print(head_tail_1)
print(privateGenDir)


parser = argparse.ArgumentParser(description='CDC design generator')
parser.add_argument('--specfile', required=True,
                    help='File containing the specification for the generator')
parser.add_argument('--outputDir', required=True,
                    help='Output directory for generator results')
parser.add_argument('--platform', required=True,
                    help='PDK/process kit for cadre flow (.e.g tsmc16)')
parser.add_argument('--mode', required=True,
                    help='Specify the outputs to be generated: verilog, macro, full (includes PEX extraction)')
args = parser.parse_args()



if not os.path.isfile(args.specfile):
   print('Error: specfile does not exist')
   print('File Path: ' + args.specfile)
   sys.exit(1)
if args.platform != 'tsmc65lp' and args.platform != 'gf12lp':
  print("Error: tsmc65lp and gf12lp are the only platform supported as of now")
  sys.exit(1)

if args.mode != 'verilog':
   if not os.path.isdir(privateGenDir):   
      print('Error. Private directory does not exist. ' + \
            'Please use only \'verilog\' mode.')
      sys.exit(1)


# Load json spec file
print("Loading specfile...")
try:
  with open(args.specfile) as file:
    jsonSpec = json.load(file)
except ValueError as e:
  print("Error occurred opening or loading json file.")
  print >> sys.stderr, 'Exception: %s' % str(e)
  sys.exit(1)


try:
   generator = jsonSpec['generator']
except KeyError as e: 
   print('Error: Bad Input Specfile. \'generator\' variable is missing.')
   sys.exit(1)

if jsonSpec['generator'] != 'cdc-gen':
  print("Error: Generator specification must be \"cdc-gen\".")



# Load json config file
print("Loading platform_config file...")
try:
  with open(genDir + '../../config/platform_config.json') as file:
    jsonConfig = json.load(file)
except ValueError as e:
  print("Error occurred opening or loading json file.")
  print >> sys.stderr, 'Exception: %s' % str(e)
  sys.exit(1)


# Get the config variable from platfom config file
if args.mode != 'verilog':
   simTool = jsonConfig['simTool']
   if simTool != 'hspice' and simTool != 'finesim':
      print('Error: Supported simulators are \'hspice\' or \'finesim\' ' + \
            'as of now')
      sys.exit(1)

   if args.mode == 'full':
      extTool = jsonConfig['extractionTool']
      if extTool != 'calibre':
         print('Error: Only support calibre extraction now')
         sys.exit(1)
      
      netlistTool = jsonConfig['netlistTool']
      if netlistTool != 'calibredrv':
         print('Error: Only support calibredrv netlist tool now')
         sys.exit(1)

# # Get the config variable from platfom config file
# simTool = jsonConfig['simTool']
# if simTool != 'hspice':
#    print("Error: Only support hspice simulator now")
#    sys.exit(1)

# extTool = jsonConfig['extractionTool']
# if extTool != 'calibre':
#    print("Error: Only support calibre extraction now")
#    sys.exit(1)

# netlistTool = jsonConfig['netlistTool']
# if netlistTool != 'calibredrv':
#    print("Error: Only support calibredrv netlist tool now")
#    sys.exit(1)
if args.mode == 'full':
   calibreRulesDir = platformConfig['calibreRules']


try:
   platformConfig = jsonConfig['platforms'][args.platform]
except ValueError as e:
   print("Error: \"' + args.platform + '\" config not available")
   sys.exit(1)




try:
   designName = jsonSpec['module_name']
except KeyError as e:
   print('Error: Bad Input Specfile. \'module_name\' variable is missing.')
   sys.exit(1)


try:
   capacitance_min = float(jsonSpec['specifications']['capacitance range']['min'])
   capacitance_max = float(jsonSpec['specifications']['capacitance range']['max'])
   error = float(jsonSpec['specifications']['error'])
except KeyError as e:
   print('Error: Bad Input Specfile. \'range or error\' value is missing under ' + \
         '\'specifications\'.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'range and error\' '+ \
         'under \'specifications\'.')
   sys.exit(1)
#Open the json file and read the content
#with open('./cdc_data.json', 'r') as myfile:
#    data=myfile.read()

    # parse file
#obj = json.loads(data)



# if capacitance_max > 100 or capacitance_min < -20 or capacitance_max < -20 or capacitance_min > 100 or :
#    print("Error: Supported temperature sensing must be inside the following range [-20 to 100] Celcius")
#    sys.exit(1)



mFile1 = platformConfig['model_lib'] + '/CDC_precharge.csv'
mFile2 = platformConfig['model_lib'] + '/CDC_weep.csv'
mFilePublic1 = genDir + '/models/' + args.platform + '.model_cdcprecharge'
mFilePublic2 = genDir + '/models/' + args.platform + '.model_cdc_sweep'

if not os.path.isfile(mFile1 or mFile2):
   if args.mode == 'verilog':
      print('Model file \'' + mFile1 + 'or' + mFile2 + '\' is not valid. ' + \
            'Using the model file provided in the repo.')
      mFile1 = mFilePublic1
      mFile2 = mFilePublic2
   else:
      print('Please provide/generate a model file')
      p.wait()

try:
   f = open(mFile1, 'r')
except ValueError as e:
   print('Model file creation failed')
   sys.exit(1)
try:
   f = open(mFile2, 'r')
except ValueError as e:
   print('Model file creation failed')
   sys.exit(1)

##Model1 = platformConfig['model_lib'] + '/CDC_precharge.csv'
##Model2 = platformConfig['model_lib'] + '/CDC_weep.csv'
Model1= mFile1
Model2= mFile2

# Get the design spec & parameters from spec file
designName = jsonSpec['module_name']

df_sheet1 = pd.read_csv(Model1, delimiter=',')
df_sheet2bis = pd.read_csv(Model2, delimiter=',')

df_sheet2 = df_sheet2bis[(df_sheet2bis['linearity Error(%)'] != 'failed')]
numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
for c in [c for c in df_sheet2.columns if df_sheet2[c].dtype in numerics]:
    df_sheet2['linearity Error(%)'] = df_sheet2['linearity Error(%)'].astype(float).abs()




#get the closest new range of capacitance min
def get_new_capacitance_min():
    value = capacitance_min
    result = df_sheet2['Capacitor(pF)'].iloc[(df_sheet2['Capacitor(pF)'] - value).abs().argsort()[:1]].tolist()
    return result[0]

#get the closest new range of capacitance max
def get_new_capacitance_max():
    value = capacitance_max
    result = df_sheet2['Capacitor(pF)'].iloc[(df_sheet2['Capacitor(pF)'] - value).abs().argsort()[:1]].tolist()
    return result[0]

def get_stages_cells():
    min = get_new_capacitance_min()
    max = get_new_capacitance_max()
    #df_without_failure = df_sheet2[(df_sheet2['linearity Error(%)'] != 'failed')]
    df_without_failure = df_sheet2
    #print('--df_without_failure---', df_without_failure)
    df_within_range = df_without_failure[(df_without_failure['Capacitor(pF)'] >= min) & (df_sheet2['Capacitor(pF)'] <= max)]
    #print('df_within_range', df_within_range)
    #print('df_within_range error', df_within_range['linearity Error(%)'].astype(float))
    df_error = pd.to_numeric(df_within_range[(df_within_range['linearity Error(%)'].astype(float).abs() <= abs(error))]['Power']).idxmin()
    power_min= df_sheet2.Power[df_error]
    cells= df_sheet2['No. of stages'][df_error]
    error_min = df_sheet2['linearity Error(%)'][df_error]
    #df_error_index = df_within_range[(df_within_range['linearity Error(%)'].astype(float).abs() <= abs(error))]['Power'].idxmin()
    #result = df_within_range['linearity Error(%)'].iloc[(df_within_range['linearity Error(%)']- error).abs().argsort()[:1]].tolist()
    print('--cells---', cells)
    print('--power_min---', power_min)
    return cells, power_min, error_min






def get_precharge():
    value = capacitance_max
    result = df_sheet1['Max Capacitor (1us settling)'].iloc[(df_sheet1['Max Capacitor (1us settling)'] - value).abs().argsort()[:1]]
    print('-----result-----', result)
    df_final = df_sheet1[(df_sheet1['Precharge'] == result.iloc[0])]
    print('precharge', df_final.Precharge.iloc[0])
    return df_final.Precharge.iloc[0]




#call to get precharge, it returns one value
get_precharge()

#call to get num of cells, returns 1 value
get_stages_cells()


def search_main():
    search_param = 'capacitance_min:'+str(capacitance_min)+','+'capacitance_max:'+str(capacitance_max)+','+'error:'+str(error)
    precharge = get_precharge()
    cells, power_min, error_min = get_stages_cells()
    raw_data_search = {'precharge': [precharge], 'cells' : [cells],'power_min': [power_min], 'error_min' : [error_min],'search_param': [search_param]}
    df_search_result = pd.DataFrame(raw_data_search,  columns=['precharge', 'cells' , 'power_min','error_min' , 'search_param' ])
    if not glob.glob('search_result_cdc.csv'):
        df_search_result.to_csv('search_result_cdc.csv', index=False)
    else:
        print(' I am adding new search result to CSV file')
        df_search_result.to_csv('search_result_cdc.csv', index=False, mode='a', header=False)
    print('---------',precharge,cells,'----------')
    return precharge, cells, power_min, error_min


def main():
    #check model
    if capacitance_min == "" or capacitance_max == "":
        print("Please provide a range")
        exit()
    else:
        #Check if temparature range field is not empty
        if error == "":
            print("Please provide error value")
            exit()
        else:
            return search_main()


def check_search_done():
    file_present = glob.glob('search_result_cdc.csv')
    if file_present:
        print('---check_search_done---- FILE IS PRESENT LETS CHECK IF SEARCH WAS ALREADY DONE')
        df_search_all = pd.read_csv('search_result_cdc.csv', delimiter=',')
        search_param = 'capacitance_min:'+str(capacitance_min)+','+'capacitance_max:'+str(capacitance_max)+','+'error:'+str(error)
        print('---check_search_done---- search_param :   ', search_param)
        df_search_done = df_search_all[(df_search_all['search_param'] == search_param)]
        print('---check_search_done---- df_search_done :   ', df_search_done)
        if not df_search_done.empty:
                print('File present : SEARCH already done')
                return df_search_done['precharge'].iloc[0], df_search_done['cells'].iloc[0], df_search_done['power_min'].iloc[0], df_search_done['error_min'].iloc[0]
        else:
            print('File present : NEW SEARCH')
            return search_main()
    else:
        return search_main()

precharge, cells, power_min, error_min = check_search_done()
print ('---precharge----- : ' , precharge)
print('#------cells------ ' , cells)

""" df_rounded = df_sheet2.round(1)['linearity Error(%)']

plt.plot(df_sheet2['Power'],df_rounded, color='green', linestyle='dashed', marker='o')

label = '  Precharge : ' + str(precharge) + '   Nb cells : ' + str(cells)
plt.annotate(label, xy=(power_min, error_min),arrowprops=dict(facecolor='black', shrink=0.05),)
plt.legend(loc='upper left', frameon=True)

plt.title('CDC Precharge and nb of Cells search')

plt.show() """


#look for points with same cells and precharge as the search result and plot them
# def search_points(precharge, cells):
#     df_points = df_sheet2[(df_sheet2['No. of stages'] == cells) & (df_sheet2['number of precharge cells'] == precharge)]

#     return df_points['Power'], df_points['linearity Error(%)']
def search_points(precharge, cells):
    #df_without_failure = df_sheet2[(df_sheet2['linearity Error(%)'] != 'failed')]
    df_without_failure = df_sheet2


    df_points = df_without_failure[(df_without_failure['No. of stages'] == cells) & (df_without_failure['number of precharge cells'] == precharge)]

    return df_points['Power'], df_points['linearity Error(%)']




#Plot section
def scatterplot():
  x = df_sheet2['Power']
  y = df_sheet2['linearity Error(%)']

  fig, ax = plt.subplots(figsize=(12, 6))
  ax.scatter(x, y, color='green', linestyle='dashed', marker='o')

  #adds a title and axes labels
  ax.set_title('CDC Precharge and nb of Cells search')
  ax.set_xlabel('Power')
  ax.set_ylabel('linearity Error(%)')
  label = '  Precharge : ' + str(precharge) + '   Nb cells : ' + str(cells)
  plt.annotate(label, xy=(power_min, error_min),arrowprops=dict(facecolor='yellow', shrink=0.05),)
  plt.plot(search_points(precharge, cells)[0], search_points(precharge, cells)[1], 'ro')

  #weird display if I don't give a specify a number of ticks on each axis
  plt.xticks([0, 100, 200, 300, 320])
  #plt.yticks([0,100,200,300,320])

  ###plt.show()

scatterplot()