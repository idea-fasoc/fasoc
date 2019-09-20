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

genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")

#Open the json file and read the content
with open(genDir + './data.json', 'r') as myfile:
    data=myfile.read()

    # parse file
obj = json.loads(data)


Tempmin = obj['temperature']['min']
Tempmax = obj['temperature']['max']

#store content in objects
#Temp = obj['temperature']
Power = obj['power']
Error = obj['error']
Optimization = obj['optimization']
Model = obj['model']

number_rows = 7
delta_1st_pass = 10
delta_2nd_pass = 2

#read the data table (csv file)
df = pd.read_csv(Model, delimiter=',')



#get the closest new range of temp min
def get_new_temp_min():
    value = Tempmin
    if value in [-20,0,20,40,60,80,100]:
        return value
    else:
        result = df['Temp'].iloc[(df['Temp']-value).abs().argsort()[:1]].tolist()
        return result[0]

#get the closest new range of temp max
def get_new_temp_max():
    value = Tempmax
    if value in [-20,0,20,40,60,80,100]:
        return value
    else:
        result = df['Temp'].iloc[(df['Temp']-value).abs().argsort()[:1]].tolist()
        return result[0]


#store some columns in arrays to draw plots
x= df['Temp']
y = df['Power']
z =  df['Error']


#calculate min power and get index (for split function)
def calculate_max_power(df, temp_min, temp_max):
    #get the max power : one value
    #max_power = df[(df['Temp'].between(temp_min, temp_max, inclusive=True))]['Power'].max()
    df_max = df[(df['Temp'] >= temp_min) & (df['Temp'] <= temp_max)]
    max_power = df_max['Power'].max()

    #get index of the max power
    #max_power_index = df[(df['Temp'].between(temp_min, temp_max, inclusive=True))]['Power'].idxmax()
    max_power_index = df_max['Power'].idxmax()
    print('----calculate_max_power------', max_power, max_power_index )
    return max_power, max_power_index

#calculate max power and get index (for split function)
def calculate_max_error(df, temp_min, temp_max):
    #get the min error : one value
    df_max = df[(df['Temp'] >= temp_min) & (df['Temp'] <= temp_max)]
    max_error = df_max['Error'].abs().max()
    #get index of max error
    max_error_index = df_max['Error'].abs().idxmax()
    print('----calculate_max_error------', max_error, max_error_index )
    return max_error, max_error_index

print('Searching for the new Temperature Min....', get_new_temp_min())
print('Searching for the new Temperature Max....', get_new_temp_max())



# read x rows of the file and calculate the min of max power
#df is the dataframe
#x in the number of lines to read
# def split_df_power(df,x):
#     s=0
#     max = []
#     serach_param = str(get_new_temp_min(Temp))+str(get_new_temp_max(Temp))+Optimization+Model+str(Delta)
#     # Give the filename you wish to save the file to
#     print('serach_param----', serach_param)
#     filename = 'golden_power_opt.csv'
#     # Use this function to search for any files which match your filename
#     file_present = glob.glob(filename)
#     if not file_present:
#         print('File not present : new search')
#         while(s < len(df)):
#             result = df.iloc[s:s+x]
#             print(result)
#             #store (maxpower, index of max power) in the list max (tuples)
#             max.append(calculate_max_power(result, get_new_temp_min(Temp), get_new_temp_max(Temp)))
#             s= s+x
#             #return min(max)[0], df.Temp[min(max)[1]], df.Error[min(max)[1]], df.inv[min(max)[1]], df.header[min(max)[1]]
#             raw_data = {'serach_param': [serach_param],'Temp': [df.Temp[min(max)[1]]], 'Frequency' : [df.Frequency[min(max)[1]]], 'Power' : [df.Power[min(max)[1]]], 'Error' : [df.Error[min(max)[1]]], 'inv' : [df.inv[min(max)[1]]], 'header' : [df.header[min(max)[1]]]}
#             df_golden = pd.DataFrame(raw_data,  columns=['serach_param', 'Temp', 'Frequency', 'Power', 'Error', 'inv' , 'header' ])
#             df_golden.to_csv(filename, index=False)
#             return df.iloc[min(max)[1]]
#     elif file_present:
#         print('File present')
#         df_golden = pd.read_csv(filename, delimiter=',')
#         df_golden_new = df_golden[(df_golden['serach_param'] == serach_param)]
#         #done1 = df_golden.loc[(df_golden['serach_param'] == serach_param)]
#         #done1_index = df_golden.ix[(df_golden['serach_param'] == serach_param)]
#         print('df_golden_new', df_golden_new)
#         #done = df_golden.loc[operator.and_(df_golden['Range_Temp_min'] == get_new_temp_min(Temp), df_golden['Range_Temp_max'] == get_new_temp_max(Temp))]
#         if not df_golden_new.empty:
#             print('File present : SEARCH already done')
#             print(df_golden_new['Error'].iloc[0], df_golden_new['inv'].iloc[0], df_golden_new['header'].iloc[0])
#             return df_golden_new['Error'].iloc[0], df_golden_new['inv'].iloc[0], df_golden_new['header'].iloc[0]
#         else:
#             print('File present : NEW SEARCH')
#             while(s < len(df)):
#                 result = df.iloc[s:s+x]
#                 print(result)
#                 #store (maxpower, index of max power) in the list max (tuples)
#                 max.append(calculate_max_power(result, get_new_temp_min(Temp), get_new_temp_max(Temp)))
#                 s= s+x
#                 #return min(max)[0], df.Temp[min(max)[1]], df.Error[min(max)[1]], df.inv[min(max)[1]], df.header[min(max)[1]]
#                 raw_data = {'serach_param': [serach_param],'Temp': [df.Temp[min(max)[1]]], 'Frequency' : [df.Frequency[min(max)[1]]], 'Power' : [df.Power[min(max)[1]]], 'Error' : [df.Error[min(max)[1]]], 'inv' : [df.inv[min(max)[1]]], 'header' : [df.header[min(max)[1]]]}
#                 df_golden_new = pd.DataFrame(raw_data,  columns=['serach_param','Temp', 'Frequency', 'Power', 'Error', 'inv' , 'header' ])
#                 df_golden.append(df_golden_new)
#                 df_golden.to_csv(filename, index=False, mode='a', header=False)
#                 return df.iloc[min(max)[1]]



def split_df_power(df,x):
    s=0
    max = []
    while(s < len(df)):
        result = df.iloc[s:s+x]
        print(result)
        #store (maxpower, index of max power) in the list max (tuples)
        max.append(calculate_max_power(result, get_new_temp_min(), get_new_temp_max()))
        s= s+x
    #return min(max)[0], df.Temp[min(max)[1]], df.Error[min(max)[1]], df.inv[min(max)[1]], df.header[min(max)[1]]
    raw_data = {'Temp': [df.Temp[min(max)[1]]], 'Frequency' : [df.Frequency[min(max)[1]]], 'Power' : [df.Power[min(max)[1]]], 'Error' : [df.Error[min(max)[1]]], 'inv' : [df.inv[min(max)[1]]], 'header' : [df.header[min(max)[1]]]}
    print('Min of powers is    ', df.Power[min(max)[1]])
    df_golden = pd.DataFrame(raw_data)
    df_golden.to_csv('golden_power_opt.csv', index=False)
    return df.iloc[min(max)[1]]

def split_df_error(df,x):
    s=0
    max = []
    while(s < len(df)):
        result = df.iloc[s:s+x]
        print(result)
        #store (maxpower, index of max power) in the list max (tuples)
        max.append(calculate_max_error(result, get_new_temp_min(), get_new_temp_max()))
        s= s+x
    #return min(max)[0], df.Temp[min(max)[1]], df.Error[min(max)[1]], df.inv[min(max)[1]], df.header[min(max)[1]]
    raw_data = {'Temp': [df.Temp[min(max)[1]]], 'Frequency' : [df.Frequency[min(max)[1]]], 'Power' : [df.Power[min(max)[1]]], 'Error' : [df.Error[min(max)[1]]], 'inv' : [df.inv[min(max)[1]]], 'header' : [df.header[min(max)[1]]]}
    print('Min of error is    ', df.Power[min(max)[1]])
    df_golden = pd.DataFrame(raw_data)
    df_golden.to_csv('golden_error_opt.csv', index=False)
    return df.iloc[min(max)[1]]

#print('-----------split----- :   min power' , split_df(df,7))

#la premiere fonction developee
#calculate min power and extract inv and header
def calculate_min_error_new(df, x, number_rows):
    search_param = 'Tempmin:'+str(Tempmin)+','+'Tempmax:'+str(Tempmax)+','+'Optimization:'+Optimization+','+'Model:'+Model+','+'Delta_1st_pass:'+str(delta_1st_pass)
    # Give the filename you wish to save the file to
    print('search_param----', search_param)
    splited_data = split_df_power(df,number_rows)
    temp = splited_data['Temp']
    print('-------calculate_min_error_new-------SPLIT DATA RESULT temperature', temp)
    #search csv table and get temp that matches the power golden value with x value
    #look at error and compare to golden value, display smallest valueget the min power : one value
    df_temp = df.loc[(df['Temp'] == temp )]
    print('-------calculate_min_error_new-------matching temp to power golden value', df_temp)
    #get the values for power within x%
    value_min = splited_data['Power']-(x/100*splited_data['Power'])
    value_max = splited_data['Power']+(x/100*splited_data['Power'])
    print ('calculate_min_error_new-----range power----', value_min, value_max)
    df_temp_new_all = df_temp[(df_temp['Power'] >= value_min) & (df_temp['Power'] <= value_max)]
    print('-------calculate_min_error_new-------all power values within the new range', df_temp_new_all)
    df_temp_new_all.to_csv('power_within_x.csv', index = False)
    df_temp_new = df_temp[(df_temp['Power'] >= value_min) & (df_temp['Power'] <= value_max)]['Error']
    df_temp_new_abs = df_temp_new.abs()
    print('-------calculate_min_error_new-------all Error values within the new range of power', df_temp_new)
    df_temp_new_index= df_temp_new.idxmin()
    print('-------calculate_min_error_new-------index value of the min error within the new range of power', df_temp_new_index)
    #abs(errror-gold) - 0.1*abs(errorgold) > smallest of all the other errors
    compare= abs(splited_data['Error'])-delta_2nd_pass/100*abs(splited_data['Error'])
    print('calculate_min_error_new-----delta error golden ------', compare)
    if abs(df_temp_new.min()) <= compare:
            min_error = df_temp_new.min()
            power = df_temp_new_all.Power[df_temp_new_index]
            temp = df_temp_new_all.Temp[df_temp_new_index]
            Inv = df_temp_new_all.inv[df_temp_new_index]
            Header = df_temp_new_all.header[df_temp_new_index]
            print('calculate_min_error_new-----min_error, Inv, Header------', min_error, Inv, Header)
    else:
            min_error = splited_data['Error']
            Inv = splited_data['inv']
            Header = splited_data['header']
            power = splited_data['Power']
            temp = splited_data['Temp']
            print('calculate_min_error_new-----min_error, Inv, Header------', min_error, Inv, Header)
    raw_data_search = {'Temp': [temp],'Power': [power],'Error': [min_error], 'Inv' : [Inv], 'Header' : [Header], 'search_param': [search_param]}
    df_search_result = pd.DataFrame(raw_data_search,  columns=['Temp', 'Power','Error', 'Inv' , 'Header', 'search_param' ])
    if not glob.glob('search_result.csv'):
        df_search_result.to_csv('search_result.csv', index=False)
    else:
        #df_search_result_old = pd.read_csv('search_result.csv', delimiter=',')
        #print('df_search_result_old', df_search_result_old)
        #df_search_result_old.append(df_search_result)
        print(' I am adding new search result to CSV file')
        df_search_result.to_csv('search_result.csv', index=False, mode='a', header=False)
    return temp, power, min_error, Inv, Header, search_param



#calculate min power and extract inv and header
def calculate_min_power_new(df, x, number_rows):
    search_param = 'Tempmin:'+str(Tempmin)+','+'Tempmax:'+str(Tempmax)+','+'Optimization:'+Optimization+','+'Model:'+Model+','+'Delta_1st_pass:'+str(delta_1st_pass)
    splited_data = split_df_error(df,number_rows)
    temp = splited_data['Temp']
    print('-------calculate_min_power_new-------SPLIT DATA RESULT tempareature', temp)
    #search csv table and get temp that matches the power golden value with x value
    #look at error and compare to golden value, display smallest valueget the min power : one value
    df_temp = df.loc[(df['Temp'] == temp )]
    print('-------calculate_min_power_new-------matching temp to power golden value', df_temp)
    #get the values for error within x%
    value_min = abs(splited_data['Error'])-(x/100*abs(splited_data['Error']))
    value_max = abs(splited_data['Error'])+(x/100*abs(splited_data['Error']))
    print ('calculate_min_power_new-----range Error----', value_min, value_max)
    df_temp_new_all = df_temp[(df_temp['Error'].abs() >= value_min) & (df_temp['Error'].abs() <= value_max)]
    print('-------calculate_min_power_new-------all Error values within the new range of error', df_temp_new_all)
    df_temp_new_all.to_csv('error_within_x.csv', index = False)
    df_temp_new = df_temp[(df_temp['Error'].abs() >= value_min) & (df_temp['Error'].abs() <= value_max)]['Power']
    df_temp_new_index= df_temp[(df_temp['Error'].abs() >= value_min) & (df_temp['Error'].abs() <= value_max)]['Power'].idxmin()
    if (df_temp_new.min() <= splited_data['Power']):
            min_power = df_temp_new.min()
            Inv = df_temp_new_all.inv[df_temp_new_index]
            Header = df_temp_new_all.header[df_temp_new_index]
            min_error= df_temp_new_all.Error[df_temp_new_index]
            temp= df_temp_new_all.Temp[df_temp_new_index]
            print('calculate_min_power_new-----min_power, Inv, Header------', min_power, Inv, Header)
    else:
            min_power = splited_data['Power']
            min_error = splited_data['Error']
            Inv = splited_data['inv']
            Header = splited_data['header']
            temp= splited_data['Temp']
            print('calculate_min_power_new-----min_power, Inv, Header------', min_power, Inv, Header)
    raw_data_search = {'Temp': [temp],'Power': [min_power], 'Error':[min_error], 'Inv' : [Inv], 'Header' : [Header], 'search_param': [search_param]}
    df_search_result = pd.DataFrame(raw_data_search,  columns=['Temp', 'Power','Error', 'Inv' , 'Header', 'search_param' ])
    if not glob.glob('search_result.csv'):
        df_search_result.to_csv('search_result.csv', index=False)
    else:
        print(' I am adding new search result to CSV file')
        df_search_result.to_csv('search_result.csv', index=False, mode='a', header=False)
    return temp, min_power, min_error, Inv, Header, search_param





def read_plot_power_opt():
    #read new data
    power_within_data = pd.read_csv("power_within_x.csv", delimiter=',')
    x_within= power_within_data['Temp']
    y_within = power_within_data['Power']
    z_within =  power_within_data['Error']
    golden_data_power = pd.read_csv("golden_power_opt.csv", delimiter=',')
    x_golden = golden_data_power['Temp']
    y_golden = golden_data_power['Power']
    z_golden =  golden_data_power['Error']
    print('series', x_golden, y_golden)
    label2 = '   Error:' + str(error)
    label1 = '  INV : ' + str(inv) + '   Header : ' + str(header)
    label = label2+label1
    plt.annotate(label, xy=(x_golden, y_golden),arrowprops=dict(facecolor='black', shrink=0.05),)
    p = Polynomial.fit(x, y, 3)
    #print('p COEFF',p.coef)
    plt.plot(*p.linspace(), 'bo')
    plt.plot(x, y, color='green', linestyle='dashed', marker='o')
    plt.plot(search_points(inv, header)[0], search_points(inv, header)[1], 'ro')
    plt.show()


def read_plot_error_opt():
   #read new data
    error_within_data = pd.read_csv("error_within_x.csv", delimiter=',')
    x_within_e= error_within_data['Temp']
    y_within_e = error_within_data['Power']
    z_within_e =  error_within_data['Error']
    golden_data_error = pd.read_csv("golden_error_opt.csv", delimiter=',')
    x_golden_e= golden_data_error['Temp']
    y_golden_e = golden_data_error['Power']
    z_golden_e=  golden_data_error['Error']
    label2 = '   Error:' + str(error)
    label1 = '  INV : ' + str(inv) + '   Header : ' + str(header)
    label = label2+label1
    plt.annotate(label, xy=(x_golden_e, z_golden_e),arrowprops=dict(facecolor='yellow', shrink=0.05),)
    #p = Polynomial.fit(x_golden_e, z_golden_e, 3)
    #print('p COEFF',p.coef)
    #plt.plot(*p.linspace(), 'bo')
    plt.plot(x, z, color='green', linestyle='dashed', marker='o')
    plt.plot(search_points(inv, header)[0], search_points(inv, header)[2], 'ro')
    plt.show()



def main():
    #check model
    if Model == "":
        print("the model file is missing")
        exit()
    else:
        #Check if temparature range field is not empty
        if Tempmin == "" or Tempmax == "":
            print("Please provide a temperature range")
            exit()
        else:
            if Optimization == "power":
                #THIS IS THE MAIN FUNCTION for power optimization
                print("*********Performing Power Optimization*********")
                time.sleep(5)
                return calculate_min_error_new(df, delta_1st_pass, number_rows)
            elif Optimization == "error":
                print("*********Performing Error Optimization*********")
                time.sleep(5)
                #THIS IS THE MAIN FUNCTION for error optimization
                return calculate_min_power_new(df, delta_1st_pass, number_rows)


def check_search_done():
    file_present = glob.glob('search_result.csv')
    if file_present:
        print('---check_search_done---- FILE IS PRESENT LETS CHECK IF SEARCH WAS ALREADY DONE')
        df_search_all = pd.read_csv('search_result.csv', delimiter=',')
        search_param = 'Tempmin:'+str(Tempmin)+','+'Tempmax:'+str(Tempmax)+','+'Optimization:'+Optimization+','+'Model:'+Model+','+'Delta_1st_pass:'+str(delta_1st_pass)
        print('---check_search_done---- search_param :   ', search_param)
        df_search_done = df_search_all[(df_search_all['search_param'] == search_param)]
        print('---check_search_done---- df_search_done :   ', df_search_done)
        if not df_search_done.empty:
                print('File present : SEARCH already done')
                print('---check_search_done---- get old research results :   ', df_search_done['Temp'].iloc[0], df_search_done['Power'].iloc[0], df_search_done['Error'].iloc[0], df_search_done['Inv'].iloc[0], df_search_done['Header'].iloc[0], df_search_done['search_param'].iloc[0])
                return df_search_done['Temp'].iloc[0], df_search_done['Power'].iloc[0], df_search_done['Error'].iloc[0], df_search_done['Inv'].iloc[0], df_search_done['Header'].iloc[0], df_search_done['search_param'].iloc[0]
        else:
            print('File present : NEW SEARCH')
            return main()
    else:
        return main()


#plot the appropriate data source and results
def plot():
    if Optimization == "power":
        read_plot_power_opt()
    elif Optimization == "error":
        read_plot_error_opt()


#final result is put in these 3 variables that you can use in your
temp, power, error, inv, header, hist = check_search_done()
print ('Error : ' , error)
print('Inv : ' , inv)
print('Header : ' , header)
print('History : ' , hist)


#look for points with same inv and Header as the search result and plot them
def search_points(inv, header):
    df_points = df[(df['inv'] == inv) & (df['header'] == header)]
    return df_points['Temp'], df_points['Power'], df_points['Error']

plot()