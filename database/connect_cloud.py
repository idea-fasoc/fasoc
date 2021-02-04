from pymongo import MongoClient

#class to connect to cloud mongodb
class Connect(object):
    @staticmethod    
    def get_connection():
        return MongoClient("mongodb+srv://admin:admin@clusterfasoc.hrzi9.mongodb.net/Fasoc?retryWrites=true&w=majority")
        