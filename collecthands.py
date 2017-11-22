
from flask import request

import DBOperater

import Constant
import datetime
import json
import os
from werkzeug import secure_filename
import urllib2
import time

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Constant.ALLOWED_EXTENSIONS

def uploadNameImg(request):
    # Get the name of the uploaded file
    filelist = request.files.getlist("file[]")
    # Check if the file is one of the allowed types/extensions
    for file in filelist:
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            file.save(os.path.join(Constant.UPLOAD_FOLDER, filename))
        else:
            return "0"
    return "1"

def uploadHandsInfo(request):
    contents = request.get_json(silent=True)
    if not contents:
        return "0"
    for content in contents:
        DBOperater.StoreData(Constant.HANDSDB,Constant.RAWHANDSCLT,content)
    return "1"

def gameseq():
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{})
    result = list(result)

    if not len(result):
        return json.dumps([])
    today = time.gmtime().tm_day
    lastupdatedate = result[0].get("update",None)
    if lastupdatedate is None or lastupdatedate != today:
        # new day, clear all data
        DBOperater.ReplaceOne(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone"},{"_id":"onlyone","data":[],"update":today},True)
        return json.dumps([])
    seqdata = result[0]["data"]
    return json.dumps(seqdata)

def joingame(seq):
    seq = int(seq)
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{})
    result = list(result)

    if not len(result):
        DBOperater.StoreData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone","data":[seq]})
        return "1"

    seqdata = result[0]["data"]
    if seq not in seqdata:
        seqdata.append(seq)

    DBOperater.DeleteData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone"})
    DBOperater.StoreData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone","data":seqdata,"update":time.gmtime().tm_day})
    return "1"

class ReconstructHandsdata:
    def __init__(self, handsdata):
        self.m_handsdata = handsdata

    def number2pos(self,number):
        if number == 1:
            return 9
        if number == 2:
            return 8
        return self.getplayernum() - number + 1

    def getplayernum(self):
        return len(self.m_handsdata["STAGE"]["TABLE"]["SEAT"])

    def getrawhanddatastruct(self):
        handsdata = self.m_handsdata["STAGE"]
        rawhandsdoc = {"_id":handsdata["TIME"] + " " + handsdata["ID"]}
        sb = handsdata["TABLE"]["SBLIND"]["CHIPS"]
        anti = handsdata["TABLE"]["ante"]
        playernum = len(handsdata["TABLE"]["SEAT"])
        stack = [0] * 10
        stack[9] = handsdata["TABLE"]["SEAT"][0]["CHIPS"]
        stack[8] = handsdata["TABLE"]["SEAT"][1]["CHIPS"]
        name = [0] * 10
        name[9] = handsdata["TABLE"]["SEAT"][0]["NAME"]
        name[8] = handsdata["TABLE"]["SEAT"][1]["NAME"]
        idlist = [0] * 10
        idlist[9] = handsdata["TABLE"]["SEAT"][0]["ID"]
        idlist[8] = handsdata["TABLE"]["SEAT"][1]["ID"]

        for idx in xrange(len(handsdata["TABLE"]["SEAT"]) - 2):
            stack[idx + 1] = handsdata["TABLE"]["SEAT"][- idx - 1]["CHIPS"]
            name[idx + 1] = handsdata["TABLE"]["SEAT"][- idx - 1]["NAME"]
            idlist[idx + 1] = handsdata["TABLE"]["SEAT"][- idx - 1]["ID"]
        rawhandsdoc["data"] = []
        rawhandsdata = rawhandsdoc["data"]
        rawhandsdata["BB"] = sb * 2
        rawhandsdata["ante"] = anti
        rawhandsdata["PLAYQUANTITY"] = playernum
        rawhandsdata["STACK"] = stack
        rawhandsdata["NAME"] = name
        rawhandsdata["ID"] = idlist
        rawhandsdata["BETDATA"] = {}

        betdata = handsdata["POKERCARD"]
        for turnidx, pokerturn in enumerate(["PREFLOP","FLOP","TURN","RIVER"]):
            if pokerturn not in betdata:
                continue
            curturnbetdata = betdata[pokerturn]["PLAYER"]
            newbetdata = []
            for actiondata in curturnbetdata:
                number = actiondata["NUMBER"]
                action = actiondata["ACTION"]
                action,value = action.split(" ")
                pos = self.number2pos(number)
                newbetdata.append([pos,action,value])
            rawhandsdata["BETDATA"][pokerturn] = newbetdata

        showcarddata = handsdata["SHOWDOWN"]["PLAYER"]
        pvcards = [None] * 10
        for showcardinfo in showcarddata:
            pvcardsstr = showcardinfo["CARD"]
            number = showcardinfo["NUMBER"]
            pvcards[self.number2pos(number)] = pvcardsstr
        rawhandsdata["PVCARD"] = pvcards

        return rawhandsdoc

def uploadhandsurl(handsurl):
    try:
        htmldoc = urllib2.urlopen(handsurl).read()
    except:
        return "0"
    prefix = "recordHelper.data = $.parseJSON('"
    postfix = "');"
    prefixidx = htmldoc.find(prefix)
    postfixidx = htmldoc.find(postfix,prefixidx)
    handsdatastr = htmldoc[prefixidx+len(prefix):postfixidx]
    handsdata = json.loads(handsdatastr)
    handsdata = ReconstructHandsdata(handsdata).getrawhanddatastruct()
    # DBOperater.StoreData(Constant.HANDSDB,Constant.RAWHANDSCLT,handsdata)
    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.RAWHANDSCLT,{"_id":handsdata["_id"]},handsdata,True)
    return "1"