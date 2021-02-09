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

import json
import argparse # arguement parsing
import pymongo
import sys

parser = argparse.ArgumentParser(description='FASoC Database')
parser.add_argument('--filename', required=True,
                                        help='Json file path')
args = parser.parse_args()

# Making Connection 
#use if inserting to a local DB
#myclient = MongoClient("mongodb://localhost:27017/") 
#Mongo ATLAS DB
client = pymongo.MongoClient("mongodb+srv://admin:admin@clusterfasoc.hrzi9.mongodb.net/Fasoc?retryWrites=true&w=majority")

  
# Database 
db = client.Fasoc

# Created or Switched to collection 
Collection = db.fasoc_DB 

# Loading or Opening the json file 
try:
    with open(args.filename) as file: 
	    file_data = json.load(file) 
except:
    print("please enter the path to the Json file you want to insert")
    sys.exit(1)  # abort

	
# Inserting the loaded data in the Collection 
# if JSON contains data more than one entry 
# insert_many is used else inser_one is used 
try:
    if isinstance(file_data, list): 
        Collection.insert_many(file_data) 
    else: 
        Collection.insert_one(file_data) 
    print("file name: " + args.filename + " has been successfully inserted")
except:
    print('An error occured')   