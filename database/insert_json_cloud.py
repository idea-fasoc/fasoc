import json 
import pymongo
import sys


# Making Connection 
#use if inserting to a local DB
#myclient = MongoClient("mongodb://localhost:27017/") 
#Mongo ATLAS DB
client = pymongo.MongoClient("mongodb+srv://admin:admin@clusterfasoc.hrzi9.mongodb.net/Fasoc?retryWrites=true&w=majority")

  
# Database 
db = client.Fasoc

# Created or Switched to collection 
Collection = db.fasoc_DB 

#getting file name
filename = sys.argv[-1]

# Loading or Opening the json file 
try:
    with open(filename) as file: 
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
    print("file name: " + filename + " has been successfully inserted")
except:
    print('An error occured')   