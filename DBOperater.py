#mongodb operation
from pymongo import MongoClient

import urllib
import logging
from Constant import *

password = urllib.quote_plus("pass/word")
client = None

#connect to mongodb
def Connect():
    global client
    if not client:
        client = MongoClient("mongodb://"+DBUSERNAME+":"+DBPWD+"@"+MONGOHOST+":"+str(MONGOPORT)+"/?authSource="+AUTHDBNAME,connect=False)

def Disconnect():
    global client
    client.close()
    client = None

#store data to mongodb
def StoreData(db,clt,data):
    return client[db][clt].insert(data)

def DeleteData(db,clt,query):
    return client[db][clt].delete_many(query)

def Find(db,clt,query):
    return client[db][clt].find(query)

def ReplaceOne(db,clt,query,newdoc,upsert = False):
    return client[db][clt].replace_one(query,newdoc,upsert)

Connect()