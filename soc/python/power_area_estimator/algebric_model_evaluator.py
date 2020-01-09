import csv
import os
import pandas as pd
from sklearn.metrics import r2_score

def algebric_model_evaluator(inputPath,outName,genName,inputsName):
	df = pd.read_csv(inputPath) #For CSV files
	input_list = ['None'] * len(inputsName)
	for counter,inputs in enumerate(inputsName):
		input_list[counter] = df[inputs]
	y_real = df[outName]

	if genName == 'ldo' and outName == 'area':
		y_pred = 8.057712617e+04 + -1.423940e+05*input_list[0] + 4.189547e+06*input_list[1] + 1.787496e+04*(input_list[0]**2) + -1.412762e+06*input_list[0]*input_list[1] + 4.790724e+04*(input_list[0]**3) + -1.341138e+06*(input_list[0]**2)*input_list[1] + -4.912363e+07*input_list[0]*(input_list[1]**2) + 3.292007e+03*(input_list[0]**4) + -7.892173e+03*(input_list[0]**6) + 1.442646e+05*(input_list[0]**5)*input_list[1] +  2.869955e+07*(input_list[0]**4)*(input_list[1]**2) + -5.204883e+10*(input_list[0]**2)*(input_list[1]**4) + -7.779279e+11*input_list[0]*(input_list[1]**5) + 2.295740e+14*(input_list[1]**6) # ldo area

	elif genName == 'ldo' and outName == 'power':
		y_pred = 0.0009 + 0*input_list[0] + 0*input_list[1] # ldo power

	elif genName == 'pll' and outName == 'area':
		y_pred = 3.7442024014121142e04 + -6.846677e-05*input_list[0] + 2.229949e-14*input_list[0]**2 + 3.062494e-23*input_list[0]**3 + -1.706576e-50*(input_list[0]**6) # pll area

	elif genName == 'memory' and outName == 'area':
		y_pred = 70503.80482990188 + 4.891463*input_list[0]

	elif genName == 'memory' and outName == 'power':
		y_pred = 0.00010545470969408155 + 7.316895e-09*input_list[0]
		
	r2Score = r2_score(y_real, y_pred)
	print(r2Score)