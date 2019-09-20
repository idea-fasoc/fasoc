import numpy as np
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from numpy.polynomial import Polynomial
import pandas as pandas
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


parser = argparse.ArgumentParser(description='DC-DC Cnverter design generator')
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



if args.platform != 'tsmc65lp':
  print("Error: tsmc65lp is the only platform supported")
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

if jsonSpec['generator'] != 'dcdc-gen':
  print("Error: Generator specification must be \"dcdc-gen\".")

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

# Get the design spec & parameters from spec file

try:
   designName = jsonSpec['instance_name']
except KeyError as e:
   print('Error: Bad Input Specfile. \'instance_name\' variable is missing.')
   sys.exit(1)


try:
   iloadmin = jsonSpec['specifications']['ILOAD']['min']
   iloadmax = jsonSpec['specifications']['ILOAD']['max']
   output_voltage = jsonSpec['specifications']['output voltage']

except KeyError as e:
   print('Error: Bad Input Specfile. \'range or voltage\' value is missing under ' + \
         '\'specifications\'.')
   sys.exit(1)
except ValueError as e:
   print('Error: Bad Input Specfile. Please use a float value for \'range and voltage\' '+ \
         'under \'specifications\'.')
   sys.exit(1)



if (iloadmax > 0.0001 or iloadmax < 0.00001) or (iloadmin < 0.00001 or iloadmin > 0.0001) or iloadmin > iloadmax:
   print("Error: Supported load current must be inside the following range [0.00001 to 0.0001] A")
   sys.exit(1)



mFile1 = platformConfig['model_lib'] + '/modelfile-dcdc-gen.xlsx'
mFilePublic1 = genDir + '/models/' + args.platform + '.model_dcdc.xlsx'

if not os.path.isfile(mFile1):
   if args.mode == 'verilog':
      print('Model file \'' + mFile + '\' is not valid. ' + \
            'Using the model file provided in the repo.')
      mFile1 = mFilePublic1
   else:
      print('Please provide/generate a model file')
      p.wait()


#Open the json file and read the content
#with open('./sc_data.json', 'r') as myfile:
#    data=myfile.read()

    # parse file
#obj = json.loads(data)

Model = mFile1


#df = pandas.read_excel(Model)

def mergingdataframes():
    mergedf= pandas.concat(pandas.read_excel(Model, sheetname=[0,1,2,3,4,5,6]))
    return mergedf

df = mergingdataframes()

print('------------------START-------------------')
print(df)
print('------------------END-------------------')

#nearesrt
#df_sort = df.ix[(df['num']-input).abs().argsort()[:2]]

#within
    #value_min = splited_data['Power']-(x/100*splited_data['Power'])
    #value_max = splited_data['Power']+(x/100*splited_data['Power'])

def search_within(df, x):
    value_min = output_voltage-(x/100*output_voltage)
    value_max = output_voltage+(x/100*output_voltage)
    return value_min, value_max

def check_empty_data(df_ILOAD):
    a,b = search_within(df_ILOAD, 1)
    df_max = df_ILOAD[(df_ILOAD['VOUT'] >= a) & (df_ILOAD['VOUT'] <= b) & (df_ILOAD['VOUT'] >= 0)]
    if df_max.empty:
        print('DataFrame is empty!')
        i=2
        while df_max.empty:
            a,b = search_within(df_ILOAD, i)
            df_max = df_ILOAD[(df_ILOAD['VOUT'] >= a) & (df_ILOAD['VOUT'] <= b) & (df_ILOAD['VOUT'] >= 0)]
            i += 1
            print('-------i%------', i)
        return df_max
    else:
        return df_max

# def search_main():
#     search_param = 'iloadmin:'+str(iloadmin)+','+'iloadmax:'+str(iloadmax)+','+'output voltage:'+str(output_voltage)+','+'Model:'+Model
#     df_ILOAD = df[(df['ILOAD'] >= iloadmin) & (df['ILOAD'] <= iloadmax)]
#     print('df_ILOAD', df_ILOAD)
#     df_result = df_ILOAD[(df_ILOAD['VOUT'] == output_voltage )]
#     if df_result.empty:
#         print('test')
#         df_max = check_empty_data(df_ILOAD)
#         print('result----df_max', df_max)
#         max_EFFICIENCY = df_max['EFFICIENCY'].max()
#         max_EFFICIENCY_idx = df_max['EFFICIENCY'].idxmax()        
#         print('result----max_EFFICIENCY', max_EFFICIENCY, max_EFFICIENCY_idx)
#         con= df_ILOAD.CON[max_EFFICIENCY_idx]
#         pd = df_ILOAD.PD[max_EFFICIENCY_idx]
#         ef = df_ILOAD.EFFICIENCY[max_EFFICIENCY_idx]
#         iload = df_ILOAD.ILOAD[max_EFFICIENCY_idx]
#         vout = df_ILOAD.VOUT[max_EFFICIENCY_idx]
#         print(con,pd, ef, iload, vout)
#         raw_data_search = {'con': [con], 'pd' : [pd], 'efficiency':[ef], 'iload':[iload], 'vout': [vout], 'search_param': [search_param]}
#         df_search_result = pandas.DataFrame(raw_data_search,  columns=['con', 'pd' ,'efficiency', 'iload', 'vout',  'search_param' ])
#         if not glob.glob('search_result_scd.csv'):
#             df_search_result.to_csv('search_result_scd.csv', index=False)
#         else:
#             print(' I am adding new search result to CSV file')
#             df_search_result.to_csv('search_result_scd.csv', index=False, mode='a', header=False)
#         return con, pd, ef, iload, vout, search_param
#     else:
#         print(df_result['CON'][1], df_result['PD'][1])
#         raw_data_search = {'con': [df_result['CON'][1]], 'pd' : [df_result['PD'][1]],'efficiency':[df_result['EFFICIENCY'][1]], 'iload':[df_result['ILOAD'][1]], 'vout':[df_result['VOUT'][1]],'search_param': [search_param]}
#         df_search_result = pandas.DataFrame(raw_data_search, columns=['con', 'pd' ,'efficiency', 'iload', 'vout','search_param' ])
#         if not glob.glob('search_result_scd.csv'):
#             df_search_result.to_csv('search_result_scd.csv', index=False)
#         else:
#             print(' I am adding new search result to CSV file')
#             df_search_result.to_csv('search_result_scd.csv', index=False, mode='a', header=False)
#         return df_result['CON'][1], df_result['PD'][1],df_result['EFFICIENCY'][1], df_result['ILOAD'][1],df_result['VOUT'][1], search_param


def search_main():
    search_param = 'iloadmin:'+str(iloadmin)+','+'iloadmax:'+str(iloadmax)+','+'output voltage:'+str(output_voltage)+','+'Model:'+Model
    df_ILOAD = df[(df['ILOAD'] >= iloadmin) & (df['ILOAD'] <= iloadmax)]
    print('df_ILOAD', df_ILOAD)
    df_result = df_ILOAD[(df_ILOAD['VOUT'] >= output_voltage-(1/100*output_voltage)) & (df_ILOAD['VOUT'] <= output_voltage+(1/100*output_voltage)) & (df_ILOAD['VOUT'] >= 0)]
    print('df_result', df_result)
    if df_result.empty:
        df_max = check_empty_data(df_ILOAD)
        print('result----df_max', df_max)
        max_EFFICIENCY = df_max['EFFICIENCY'].max()
        max_EFFICIENCY_idx = df_max['EFFICIENCY'].idxmax()        
        print('result----max_EFFICIENCY', max_EFFICIENCY, max_EFFICIENCY_idx)
        con= df_ILOAD.CON[max_EFFICIENCY_idx]
        pd = df_ILOAD.PD[max_EFFICIENCY_idx]
        ef = df_ILOAD.EFFICIENCY[max_EFFICIENCY_idx]
        iload = df_ILOAD.ILOAD[max_EFFICIENCY_idx]
        vout = df_ILOAD.VOUT[max_EFFICIENCY_idx]
        print(con,pd, ef, iload, vout)
        raw_data_search = {'con': [con], 'pd' : [pd], 'efficiency':[ef], 'iload':[iload], 'vout': [vout], 'search_param': [search_param]}
        df_search_result = pandas.DataFrame(raw_data_search,  columns=['con', 'pd' ,'efficiency', 'iload', 'vout',  'search_param' ])
        if not glob.glob('search_result_scd.csv'):
            df_search_result.to_csv('search_result_scd.csv', index=False)
        else:
            print(' I am adding new search result to CSV file')
            df_search_result.to_csv('search_result_scd.csv', index=False, mode='a', header=False)
        return con, pd, ef, iload, vout, search_param
    else:
        max_EFFICIENCY = df_result['EFFICIENCY'].max()
        max_EFFICIENCY_idx = df_result['EFFICIENCY'].idxmax()
        print('result----max_EFFICIENCY IN 1% RANGE', max_EFFICIENCY, max_EFFICIENCY_idx)
        con= df_ILOAD.CON[max_EFFICIENCY_idx]
        pd = df_ILOAD.PD[max_EFFICIENCY_idx]
        ef = df_ILOAD.EFFICIENCY[max_EFFICIENCY_idx]
        iload = df_ILOAD.ILOAD[max_EFFICIENCY_idx]
        vout = df_ILOAD.VOUT[max_EFFICIENCY_idx]
        raw_data_search = {'con': [con], 'pd' : [pd], 'efficiency':[ef], 'iload':[iload], 'vout': [vout], 'search_param': [search_param]}
        df_search_result = pandas.DataFrame(raw_data_search, columns=['con', 'pd' ,'efficiency', 'iload', 'vout','search_param' ])
        if not glob.glob('search_result_scd.csv'):
            df_search_result.to_csv('search_result_scd.csv', index=False)
        else:
            print('I am adding new search result to CSV file')
            df_search_result.to_csv('search_result_scd.csv', index=False, mode='a', header=False)
        return con, pd, ef, iload, vout, search_param

def main():
    #check model
    if Model == "":
        print("the model file is missing")
        exit()
    else:
        #Check if temparature range field is not empty
        if iloadmin == "" or iloadmax == "":
            print("Please provide ILOAD range")
            exit()
        else:
            return search_main()

def check_search_done():
    file_present = glob.glob('search_result_scd.csv')
    if file_present:
        print('---check_search_done---- FILE IS PRESENT LETS CHECK IF SEARCH WAS ALREADY DONE')
        df_search_all = pandas.read_csv('search_result_scd.csv', delimiter=',')
        search_param = 'iloadmin:'+str(iloadmin)+','+'iloadmax:'+str(iloadmax)+','+'output voltage:'+str(output_voltage)+','+'Model:'+Model
        print('---check_search_done---- search_param :   ', search_param)        
        df_search_done = df_search_all[(df_search_all['search_param'] == search_param)]
        print('---check_search_done---- df_search_done :   ', df_search_done)        
        if not df_search_done.empty:
                print('File present : SEARCH already done')
                return df_search_done['con'].iloc[0], df_search_done['pd'].iloc[0],df_search_done['efficiency'].iloc[0],df_search_done['iload'].iloc[0],df_search_done['vout'].iloc[0],  df_search_done['search_param'].iloc[0]
        else:
            print('File present : NEW SEARCH')
            return search_main()
    else:
        return search_main()




con, pd, ef, il, vo, hist = check_search_done()
print ('config (CON) : ' , con)
print('# of parallel cells (PD) : ' , pd)
print('History : ' , hist)



#look for points with same con and pd as the search result and plot them
def search_points(con, pd):
    df_points = df[(df['CON'] == con) & (df['PD'] == pd)]
    return df_points['ILOAD'], df_points['EFFICIENCY']



# #Plot section
# def scatterplot():
#   x = df['ILOAD']
#   y = df['EFFICIENCY']
#   fig, ax = plt.subplots(figsize=(12, 6))
#   ax.set_title('SDC CON and PD search')
#   ax.set_xlabel('ILOAD')
#   ax.set_ylabel('EFFICIENCY')
#   ax.plot(x,y, 'o')

#   label = '  CON : ' + str(con) + '   PD : ' + str(pd)
#   plt.annotate(label, xy=(il, ef),arrowprops=dict(facecolor='black', shrink=0.05),)
#   plt.plot(search_points(con, pd)[0], search_points(con, pd)[1], 'ro')

#   plt.show()

# scatterplot()

#Plot section
def scatterplot():
  df_positif = df[(df['EFFICIENCY'] >=0)]

  x = df_positif['ILOAD']
  y = df_positif['EFFICIENCY']
  fig, ax = plt.subplots(figsize=(12, 6))
  ax.set_title('SDC CON and PD search')
  ax.set_xlabel('ILOAD')
  ax.set_ylabel('EFFICIENCY')
  ax.plot(x,y, 'o')

  label = '  CON : ' + str(con) + '   PD : ' + str(pd)
  plt.annotate(label, xy=(il, ef),arrowprops=dict(facecolor='black', shrink=0.05),)
  plt.plot(search_points(con, pd)[0], search_points(con, pd)[1], 'ro')

  plt.show()
###scatterplot()
