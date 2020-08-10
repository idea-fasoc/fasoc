import csv
import os
import pandas as pd

cwd = os.getcwd()
pwd = os.path.abspath(os.path.join(cwd, os.pardir))
root_path_ml = os.path.join(pwd,'database','sheets','ML','generator')

#df = pd.read_csv(os.path.join(root_path_ml,'inv_train_test_input.csv')) #For CSV files
df = pd.read_excel(os.path.join(root_path_ml,'pll_train_test_output.xlsx'), sheet_name=0, header=0,index_col=False,keep_default_na=True) #For XLSX files

saved_column = df['area']
#updated_column = saved_column / 10000 #ldo area
updated_column = saved_column / 10000 #pll area

df['area'] = updated_column
#df.to_csv(os.path.join(root_path_ml,'ldo_area_train_test_input.csv'),index = False) #For CSV files
df.to_excel(excel_writer = os.path.join(root_path_ml,'pll_train_test_output.xlsx'),index = False) #For XLSX files