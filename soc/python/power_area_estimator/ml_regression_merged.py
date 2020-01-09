from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LassoCV
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd
import xlrd

def ml_regression_merged(inFile,outFile,outName,inArrName):
	X_book = xlrd.open_workbook(inFile)
	X_sheet = X_book.sheet_by_name('Sheet1')
	X=[[X_sheet.cell_value(r, c) for c in range(X_sheet.ncols)] for r in range(1,X_sheet.nrows)]

	df_in = pd.read_excel(inFile, sheet_name=0, header=0,index_col=False,keep_default_na=True)
	df_out = pd.read_excel(outFile, sheet_name=0, header=0,index_col=False,keep_default_na=True)
	df_in[outName] = df_out[outName]

	poly = PolynomialFeatures(6,include_bias=False)
	X_poly = poly.fit_transform(X)
	X_poly_feature_name = poly.get_feature_names(inArrName)
	df_poly = pd.DataFrame(X_poly, columns=X_poly_feature_name)
	df_poly[outName]=df_in[outName]
	X_train=df_poly.drop(outName,axis=1)
	y_train=df_poly[outName]

	model1 = LassoCV(cv=10,verbose=0,normalize=True,eps=0.001,n_alphas=100, tol=0.0001,max_iter=5000)  
	model1.fit(X_train,y_train)
	y_pred = np.array(model1.predict(X_train))

	RMSE_1=np.sqrt(np.sum(np.square(y_pred-y_train)))/len(y_pred)
	print("RMSE:")
	print(RMSE_1)
	AlPha = model1.alpha_
	print("AlPha:")
	print(AlPha)
	r2Score = r2_score(y_train, y_pred)
	print("r2Score:")
	print(r2Score)
	coeff1 = pd.DataFrame(model1.coef_,index=df_poly.drop(outName,axis=1).columns, columns=['Coefficients Metamodel'])
	print(coeff1[coeff1['Coefficients Metamodel']!=0])
