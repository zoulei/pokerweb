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
        # client = MongoClient("mongodb://"+DBUSERNAME+":"+DBPWD+"@"+MONGOHOST+":"+str(MONGOPORT)+"/?authSource="+AUTHDBNAME,connect=False)
        client = MongoClient("mongodb://"+DBUSERNAME+":"+DBPWD+"@"+MONGOHOST+"/?authSource="+AUTHDBNAME,connect=False)

def Disconnect():
    global client
    client.close()
    client = None

#store data to mongodb
def StoreData(db,clt,data):
    global client
    if not client:
        Connect()
    return client[db][clt].insert(data)

def DeleteData(db,clt,query):
    global client
    if not client:
        Connect()
    return client[db][clt].delete_many(query)

def Find(db,clt,query):
    global client
    if not client:
        Connect()
    return client[db][clt].find(query)

def ReplaceOne(db,clt,query,newdoc,upsert = False):
    global client
    if not client:
        Connect()
    return client[db][clt].replace_one(query,newdoc,upsert)

def testconnectdb():
    result = Find(HANDSDB,HANDSCLT,{"_id":"2017-12-15 00:43:13 84"})
    for v in result:
        print v
#
# Connect()

if __name__ == "__main__":
    testconnectdb()