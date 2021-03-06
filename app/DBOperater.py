# -*- coding:utf-8 -*-
#mongodb operation
from pymongo import MongoClient

import urllib
import logging
from Constant import *

# password = urllib.parse.quote("pass/word")
client = None

#connect to mongodb
def Connect():
    global client
    if not client:
        # client = MongoClient("mongodb://"+DBUSERNAME+":"+DBPWD+"@"+MONGOHOST+":"+str(MONGOPORT)+"/?authSource="+AUTHDBNAME,connect=False)
        # client = MongoClient("mongodb://"+DBUSERNAME+":"+DBPWD+"@"+MONGOHOST+"/?authSource="+AUTHDBNAME,connect=False)
        client = MongoClient("mongodb://" + MONGOHOST, connect=False)
        # client = MongoClient("mongodb://localhost:27017", connect=False)
        # print ("===============================")
        # print ("")

def Disconnect():
    global client
    client.close()
    client = None

#store data to mongodb
def StoreData(db,clt,data):
    global client
    if not client:
        Connect()
    if clt not in client[db].list_collection_names():
        client[db].create_collection(clt)
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
    if clt not in client[db].list_collection_names():
        client[db].create_collection(clt)
    return client[db][clt].find(query)

# upsert为真时,如果没有通过query查到doc,那么会插入这个doc,
# upsert为假时,如果没有通过query查到doc,那么会报错
def ReplaceOne(db,clt,query,newdoc,upsert = False):
    global client
    if not client:
        Connect()
    if clt not in client[db].list_collection_names():
        client[db].create_collection(clt)
    return client[db][clt].replace_one(query,newdoc,upsert)

def testconnectdb():
    result = Find(HANDSDB,HANDSCLT,{"_id":"2017-12-15 00:43:13 84"})
    for v in result:
        print (v)

def DropCollection(db, clt):
    global client
    if not client:
        Connect()
    client[db][clt].drop()
#
# Connect()
def dropclt():
    global client
    if not client:
        Connect()
    for clt in client[HANDSDB].list_collection_names():
        if clt.startswith("1054988_"):
            client[HANDSDB][clt].drop()

if __name__ == "__main__":
    dropclt()