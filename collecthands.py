
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




def gameseq(phoneid):
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":phoneid})
    result = list(result)
    if not len(result):
        return json.dumps([])
    data = result[0]["data"]
    now = time.time()
    for seq,realtime in data.items():
        if now - realtime > 3600 * 15:
            del data[seq]
    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":phoneid},{"_id":phoneid,"data":data},True)
    return json.dumps([int(v) for v in data.keys()])

def joingame(seq,phoneid):
    seq = int(seq)
    # this deals with the collect game information, add this seq to the to be collected list
    result = DBOperater.Find(Constant.HANDSDB,Constant.COLLECTGAMECLT,{})
    result = list(result)
    if not len(result):
        data = {}
    else:
        data = result[0].get("data")
    data[str(seq)] = {
        "handidx":0,
        "time":time.time(),
        "phoneid":None
    }
    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.COLLECTGAMECLT,{"_id":"onlyone"},{"_id":"onlyone","data":data},True)

    # this deals with the join game information, add this seq to the joined game list
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":phoneid})
    result = list(result)
    if not len(result):
        data = {}
    else:
        data = result[0]["data"]
    data[str(seq)] = time.time()
    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":phoneid},{"_id":phoneid,"data":data},True)
    return "1"

def collectgamelist(phoneid):
    result = DBOperater.Find(Constant.HANDSDB,Constant.COLLECTGAMECLT,{})
    result = list(result)

    if not len(result):
        return json.dumps([])

    data = result[0].get("data")
    # delete data of 24 hours ago
    for seq,gameinfo in data.items():
        if time.time() - gameinfo["time"] > 3600 * 15:
            del data[seq]

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.COLLECTGAMECLT,{"_id":"onlyone"},{"_id":"onlyone","data":data},True)
    return json.dumps([int(v[0]) for v in data.items() if (v[1]["phoneid"] is None or v[1]["phoneid"] == phoneid)] )

def collectgamehandidx(seq,phoneid):
    result = DBOperater.Find(Constant.HANDSDB,Constant.COLLECTGAMECLT,{})
    result = list(result)
    if not len(result):
        data = {
            str(seq)    :   {
                "handidx":0,
                "time":time.time(),
                "phoneid":phoneid
            }
        }
    else:
        data = result[0].get("data")
    if data[str(seq)]["phoneid"] and data[str(seq)]["phoneid"] != phoneid:
        # this hand has been occupied
        return "-1"
    else:
        data[str(seq)]["phoneid"] = phoneid
    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.COLLECTGAMECLT,{"_id":"onlyone"},{"_id":"onlyone","data":data},True)
    return str(data[str(seq)]["handidx"])

def completegamecollect(seq):
    result = DBOperater.Find(Constant.HANDSDB,Constant.COLLECTGAMECLT,{})
    result = list(result)

    data = result[0].get("data")
    if str(seq) in data.keys():
        del data[str(seq)]

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.COLLECTGAMECLT,{"_id":"onlyone"},{"_id":"onlyone","data":data},True)
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
        rawhandsdoc = {"_id":str(handsdata["TIME"]) + " " + str(handsdata["ID"])}
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
        rawhandsdoc["data"] = {}
        rawhandsdata = rawhandsdoc["data"]
        rawhandsdata["BB"] = int(sb) * 2
        rawhandsdata["ante"] = anti
        rawhandsdata["PLAYQUANTITY"] = playernum
        rawhandsdata["STACK"] = stack
        rawhandsdata["NAME"] = name
        rawhandsdata["ID"] = idlist
        rawhandsdata["BETDATA"] = {}

        betdata = handsdata["POKERCARD"]
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.m_handsdata)
        for turnidx, pokerturn in enumerate(["PREFLOP","FLOP","TURN","RIVER"]):
            if pokerturn not in betdata:
                continue
            curturnbetdata = betdata[pokerturn]["PLAYER"]
            newbetdata = []
            for actiondata in curturnbetdata:
                number = actiondata["NUMBER"]
                action = actiondata["ACTION"]
                if action == "showwait":
                    continue
                action,value = action.split(" ")
                pos = self.number2pos(number)
                newbetdata.append([pos,action,value])
            if newbetdata:
                rawhandsdata["BETDATA"][pokerturn] = newbetdata

        showcarddata = handsdata["SHOWDOWN"]["PLAYER"]
        pvcards = [None] * 10
        for showcardinfo in showcarddata:
            if "CARD" not in showcardinfo:
                break
            pvcardsstr = showcardinfo["CARD"]
            number = showcardinfo["NUMBER"]
            pvcards[self.number2pos(number)] = pvcardsstr
        rawhandsdata["PVCARD"] = pvcards

        return rawhandsdoc

def generateurl(rawurl):
    tranmap =  {":":"0018fenghao",
				"/":"0018zhexian",
				".":"0018dot",
				"?":"0018question",
				"=":"0018equal",
				"&":"0018with"}
    for key, value in tranmap.items():
        rawurl = rawurl.replace(value,key)
    return rawurl

def uploadhandsurl(gameidx,handidx,handsurl):
    handsurl = generateurl(handsurl)
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
    handsdata["rawstr"] = handsdatastr
    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(handsdata)
    # print "===================================="

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.TESTCLT,{"_id":handsdata["_id"]},handsdata,True)

    # update collect information
    result = DBOperater.Find(Constant.HANDSDB,Constant.COLLECTGAMECLT,{})
    result = list(result)
    if not len(result):
        data = {str(gameidx):[handidx,time.time()]}
    else:
        data = result[0].get("data")
    data[str(gameidx)]["handidx"] = handidx
    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.COLLECTGAMECLT,{"_id":"onlyone"},{"_id":"onlyone","data":data},True)

    return "1"

# if __name__ == "__main__":
#     uploadhandsurl("http0018fenghao0018zhexian0018zhexianreplay0018dotpaiyou0018dotme0018fenghao80800018zhexianhandplayer0018zhexianreplay0018zhexian0018questionurl0018equalnew9492ecaf53d5d99072cb2fea860ed4a866e7337dff285bdec167db9f68bfd74177afbc0bb01945005689caa07c2c97eb917b5bc07d4b2ba5")