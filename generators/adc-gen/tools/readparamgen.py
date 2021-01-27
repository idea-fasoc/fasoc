import numpy as np
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from numpy.polynomial import Polynomial
import matplotlib.gridspec as gridspec
import pandas as pd
import csv
import json
import os
import time
import heapq
from collections import defaultdict
import glob
import operator
from pylab import *

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


parser = argparse.ArgumentParser(description='ADC design generator')
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
  print("Error: tsmc65lp and gf12lp are the only platforms supported")
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

if jsonSpec['generator'] != 'adc-gen':
  print("Error: Generator specification must be \"adc-sense-gen\".")



# Load json config file
print("Loading platform_config file...")
try:
  with open('../../config/platform_config.json') as file:
    jsonConfig = json.load(file)
except ValueError as e:
  print("Error occurred opening or loading json file.")
  print >> sys.stderr, 'Exception: %s' % str(e)
  sys.exit(1)



# Get the config variable from platfom config file
simTool = jsonConfig['simTool']
if simTool != 'hspice':
   print("Error: Only support hspice simulator now")
   sys.exit(1)

extTool = jsonConfig['extractionTool']
if extTool != 'calibre':
   print("Error: Only support calibre extraction now")
   sys.exit(1)

netlistTool = jsonConfig['netlistTool']
if netlistTool != 'calibredrv':
   print("Error: Only support calibredrv netlist tool now")
   sys.exit(1)

calibreRulesDir = jsonConfig['calibreRules']

try:
   platformConfig = jsonConfig['platforms'][args.platform]
except ValueError as e:
   print("Error: \"' + args.platform + '\" config not available")
   sys.exit(1)


#Open the json file and read the content
#with open('./adc_data.json', 'r') as myfile:
#    data=myfile.read()

#    # parse file
#obj = json.loads(data)


# Get the design spec & parameters from spec file

try:
   designName = jsonSpec['instance_name']
except KeyError as e:
   print('Error: Bad Input Specfile. \'module_name\' variable is missing.')
   sys.exit(1)

try:
   fsampling = jsonSpec['specifications']['fsampling']
   enob = jsonSpec['specifications']['target enob']
except KeyError as e:
   print('Error: Bad Input Specfile. \'parameter o\' value is missing under ' + \
         '\'specifications\'.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'sampling speed and ENOB \' '+ \
         'under \'specifications\'.')
   sys.exit(1)

optimization = str(jsonSpec['specifications']['optimization'])
if optimization != "area" and optimization != "power":
   print("Error: Please enter a supported optmization strategy [error or power]")
   sys.exit(1)


mFile1 = platformConfig['model_lib'] + '/SAR_ADC_modelfile.xlsx'
mFilePublic1 = genDir + 'models/' + args.platform + '.model_adc.xlsx'


#if not os.path.isfile(mFile1):
#   if args.mode == 'verilog':
#      print('Model file \'' + mFile1 + '\' is not valid. ' + \
#            'Using the model file provided in the repo.')
#      mFile1 = mFilePublic1
#   else:
#      print('Please provide/generate a model file')
#      p.wait()


print('Model file \'' + mFile1 + '\' is not valid. ' + \
      'Using the model file provided in the repo.')
mFile1 = mFilePublic1

Model = mFile1

fsampling_target = fsampling
enob_target = enob

#print(fsampling, enob, optimization)

#df = pd.read_excel('./SAR_ADC_modelfile.xlsx')

df = pd.read_excel(Model)
def search_power(s, e):
    df_within_fsampling = df[(df['enob'] >= e) & (df['fsmpl'] == s)]
    power = df_within_fsampling['pwr'].min()
    power_indx= df_within_fsampling['pwr'].idxmin()
    power_with_inx= df_within_fsampling.pwr[power_indx]
    fsampling = df_within_fsampling.fsmpl[power_indx]
    resolution = df_within_fsampling.nbit[power_indx]
    enob = df_within_fsampling.enob[power_indx]
    area = df_within_fsampling.area[power_indx]
    nisw = df_within_fsampling.nisw[power_indx]
    ncsw = df_within_fsampling.ncsw[power_indx]
    return power_with_inx, fsampling, resolution, enob, area, nisw, ncsw

def search_area(s, e):
    df_within_fsampling = df[(df['enob'] >= e) & (df['fsmpl'] == s)]
    area_indx= df_within_fsampling['area'].idxmin()
    power= df_within_fsampling.pwr[area_indx]
    fsmpl = df_within_fsampling.fsmpl[area_indx]
    resolution = df_within_fsampling.nbit[area_indx]
    enobtarget = df_within_fsampling.enob[area_indx]
    area = df_within_fsampling.area[area_indx]
    nisw = df_within_fsampling.nisw[area_indx]
    ncsw = df_within_fsampling.ncsw[area_indx]
    return power, fsmpl, resolution, enobtarget, area, nisw, ncsw


def search_main(s,e):
    search_param = 'fsampling:'+str(s)+','+'enob:'+str(e)+','+'optimization:'+str(optimization)
    if optimization == "power" :
        power_with_inx, fsampling, resolution, enob, area, nisw, ncsw = search_power(s, e )
    elif optimization == "area" :
        power_with_inx, fsampling, resolution, enob, area, nisw, ncsw = search_area(s, e )
    raw_data_search = {'power_min': [power_with_inx], 'fsampling': [fsampling], 'resolution': [resolution], 'enob' : [enob], 'area' : [area], 'nisw' : [nisw], 'ncsw' : [ncsw], 'search_param': [search_param]}
    df_search_result = pd.DataFrame(raw_data_search,  columns=['power_min', 'fsampling' , 'resolution','enob' , 'area', 'nisw', 'ncsw', 'search_param' ])
    if not glob.glob('search_result_adc.csv'):
        df_search_result.to_csv('search_result_adc.csv', index=False)
    else:
        print(' I am adding new search result to CSV file')
        df_search_result.to_csv('search_result_adc.csv', index=False, mode='a', header=False)
    return power_with_inx, fsampling, resolution, enob, area, nisw, ncsw        

def check_search_done(s,e):
    file_present = glob.glob('search_result_adc.csv')
    if file_present:
        print('---check_search_done---- FILE IS PRESENT LETS CHECK IF SEARCH WAS ALREADY DONE')
        df_search_all = pd.read_csv('search_result_adc.csv', delimiter=',')
        search_param = 'fsampling:'+str(s)+','+'enob:'+str(e)+','+'optimization:'+str(optimization)
        print('---check_search_done---- search_param :   ', search_param)        
        df_search_done = df_search_all[(df_search_all['search_param'] == search_param)]
        print('---check_search_done---- df_search_done :   \n', df_search_done)        
        if not df_search_done.empty:
            if optimization == 'power':
                    print('File present : SEARCH for power already done')
                    return df_search_done['power_min'].iloc[0], df_search_done['fsampling'].iloc[0], df_search_done['resolution'].iloc[0], df_search_done['enob'].iloc[0], df_search_done['area'].iloc[0], df_search_done['nisw'].iloc[0], df_search_done['ncsw'].iloc[0]
            elif optimization == 'area':
                    print('File present : SEARCH for area already done')
                    return df_search_done['power_min'].iloc[0], df_search_done['fsampling'].iloc[0], df_search_done['resolution'].iloc[0], df_search_done['enob'].iloc[0], df_search_done['area'].iloc[0], df_search_done['nisw'].iloc[0], df_search_done['ncsw'].iloc[0]
        else:
            print('File present : NEW SEARCH')
            return search_main(s,e)
    else:
        return search_main(s,e)

def main():
    #check json
    if fsampling_target == "":
        print("Not possible")
        exit()
    else:
        power_with_inx, fsampling, resolution, enob, area, nisw, ncsw = check_search_done(fsampling_target,enob_target)
        if optimization == "power" :
            print ('-----POWER : ------', power_with_inx)
        elif optimization == "area" :
            print ('-----AREA : ------', area)  

        return power_with_inx, fsampling, resolution, enob, area, nisw, ncsw


#def main(fsampling, enob):
#    #check json
#    if fsampling == "":
#        print("Not possible")
#        exit()
#    else:
#        power_with_inx, fsampling, resolution, enob, area, nisw, ncsw = check_search_done(fsampling,enob)
#        if optimization == "power" :
#            print ('-----POWER : ------', power_with_inx)
#        elif optimization == "area" :
#            print ('-----AREA : ------', area)  
#        return power_with_inx, fsampling, resolution, enob, area, nisw, ncsw










#power_with_inx, fsampling, resolution, enob, area, nisw, ncsw = main()

#Plot section
def plot():

  gs = gridspec.GridSpec(2, 2)
  x1 = df['fsmpl']
  y1 = df['enob']
  x2 = df['nbit']
  y2 = df['pwr']
  y3 = df['area']
  fig= plt.figure(figsize=(15,8))
  plt.subplot(gs[0, 0])
  plt.plot(x1, y1, 'o')
  label1 = '  Fsampling : ' + str(fsampling) + '   enob : ' + str(enob)
  plt.annotate(label1, xy=(fsampling, enob),arrowprops=dict(facecolor='yellow', shrink=0.05),)

  plt.xlabel('Fsampling')
  plt.ylabel('Enob')
  fig = gcf()
  if optimization == "power" :
      fig.suptitle(' POWER OPTIMIZATION SEARCH   :' +str(power_with_inx), fontsize=14)
      #plt.title('-----POWER SEARCH   :' +str(power_with_inx)+'   ---------------------------  :')
  elif optimization == "area" :
      fig.suptitle(' AREA OPTIMIZATION SEARCH   :' +str(area), fontsize=14)
      #plt.title('----------------------------------------------------------AREA SEARCH   :' +str(area)+'   ---------------------------  :')


  plt.subplot(gs[0, 1])
 # plt.plot(x2, y2, '.-')
  plt.plot(x2, y2, 'o')
  plt.xlabel('Resolution')
  plt.ylabel('Power')
  label2 = '  resolution : ' + str(resolution) + '   power : ' + str(power_with_inx)
  plt.annotate(label2, xy=(resolution, power_with_inx),arrowprops=dict(facecolor='yellow', shrink=0.05),)

  plt.subplot(gs[1, :])
  plt.plot(y2, y3, 'o')
  plt.xlabel('Power')
  plt.ylabel('Area')
  label2 = '  power : ' + str(power_with_inx) + '   area : ' + str(area)
  plt.annotate(label2, xy=(power_with_inx, area),arrowprops=dict(facecolor='yellow', shrink=0.05),)
  plt.title('AREA VS POWER ')

  plt.show()

#plot()
