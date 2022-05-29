
from flask import request

import DBOperater

import Constant
import datetime
import json
import os
from werkzeug import secure_filename
from urllib2 import urlopen
import urllib2
# from urllib.request import urlopen
import time
import traceback
import requests
from fake_useragent import UserAgent
from requests.auth import HTTPBasicAuth
import socket

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
        DBOperater.StoreData(Constant.HANDSDB, Constant.RAWHANDSCLT, content)
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

    def myselfnumber2pos(self, number, dealerpos, playernum):
        playerposdata = [0] * (playernum + 1)
        poslist = range(dealerpos, 0, -1) + range(playernum, dealerpos, -1)
        playerposdata[poslist[-1]] = 9
        playerposdata[poslist[-2]] = 8
        for idx, pos in enumerate(poslist[:-2]):
            playerposdata[pos] = idx + 1

    def getplayernum(self):
        return len(self.m_handsdata["STAGE"]["TABLE"]["SEAT"])

    def getmyselfrawhanddatastruct(self):
        handsdata = self.m_handsdata["STAGE"]
        rawhandsdoc = {"_id": str(handsdata["TIME"]) + " " + str(handsdata["ID"])}
        sb = handsdata["TABLE"]["SBLIND"]["CHIPS"]
        anti = handsdata["TABLE"]["ante"]
        playernum = len(handsdata["TABLE"]["SEAT"])

        sbpos = handsdata["TABLE"]["SBLIND"]["NUMBER"]
        bbpos = handsdata["TABLE"]["BBLIND"]["NUMBER"]
        dealerpos = handsdata["TABLE"]["DEALER"]

        stack = [0.0] * 10
        stack[9] = float(handsdata["TABLE"]["SEAT"][sbpos-1]["CHIPS"])
        stack[8] = float(handsdata["TABLE"]["SEAT"][bbpos-1]["CHIPS"])
        name = [0] * 10
        name[9] = handsdata["TABLE"]["SEAT"][sbpos-1]["NAME"]
        name[8] = handsdata["TABLE"]["SEAT"][bbpos-1]["NAME"]
        idlist = [0] * 10
        idlist[9] = handsdata["TABLE"]["SEAT"][sbpos-1]["ID"]
        idlist[8] = handsdata["TABLE"]["SEAT"][bbpos-1]["ID"]
        for idx,pos in enumerate(range(dealerpos, 0, -1) + range(playernum, dealerpos + 2, -1)):
        # for idx in xrange(len(handsdata["TABLE"]["SEAT"]) - 2):
            stack[idx + 1] = float(handsdata["TABLE"]["SEAT"][pos - 1]["CHIPS"])
            name[idx + 1] = handsdata["TABLE"]["SEAT"][pos - 1]["NAME"]
            idlist[idx + 1] = handsdata["TABLE"]["SEAT"][pos - 1]["ID"]

        rawhandsdoc["data"] = {}
        rawhandsdata = rawhandsdoc["data"]
        rawhandsdata["BB"] = float(sb) * 2
        rawhandsdata["ante"] = anti
        rawhandsdata["PLAYQUANTITY"] = playernum
        rawhandsdata["STACK"] = stack
        rawhandsdata["NAME"] = name
        rawhandsdata["ID"] = idlist
        rawhandsdata["BETDATA"] = {}

        betdata = handsdata["POKERCARD"]
        boarddata = ""

        playerposdata = [0] * (playernum + 1)
        poslist = range(dealerpos, 0, -1) + range(playernum, dealerpos, -1)
        playerposdata[poslist[-1]] = 9
        playerposdata[poslist[-2]] = 8
        for idx, pos in enumerate(poslist[:-2]):
            playerposdata[pos] = idx + 1


        for turnidx, pokerturn in enumerate(["PREFLOP", "FLOP", "TURN", "RIVER"]):
            if pokerturn not in betdata:
                continue
            curturnbetdata = betdata[pokerturn]["PLAYER"]
            newbetdata = []
            for actiondata in curturnbetdata:
                number = actiondata["NUMBER"]
                action = actiondata["ACTION"]
                if action == "showwait" or action.find("straddle") != -1:
                    continue
                # print action
                action, value = action.split(" ")
                pos = playerposdata[number]
                # pos = self.number2pos(number)
                newbetdata.append([pos, action, float(value)])
            if newbetdata:
                rawhandsdata["BETDATA"][pokerturn] = newbetdata
            if "CARD" in betdata[pokerturn]:
                boarddata += " "+betdata[pokerturn]["CARD"]

        myhand = betdata["HOLECARD"]["CARD"]
        myhand = myhand.replace(" ", "")
        mypos = playerposdata[1]
        rawhandsdata["MYPOS"] = mypos
        rawhandsdata["MYHAND"] = myhand

        showcarddata = handsdata["SHOWDOWN"]["PLAYER"]
        pvcards = [None] * 10
        for showcardinfo in showcarddata:
            if "CARD" not in showcardinfo:
                break
            pvcardsstr = showcardinfo["CARD"]
            number = showcardinfo["NUMBER"]
            pvcards[playerposdata[number]] = pvcardsstr
        rawhandsdata["PVCARD"] = pvcards
        if boarddata:
            rawhandsdata["BOARD"] = boarddata[1:]
        else:
            rawhandsdata["BOARD"] = boarddata

        return rawhandsdoc

    def getrawhanddatastruct(self):
        handsdata = self.m_handsdata["STAGE"]
        if not handsdata["TABLE"]["look"]:
            return self.getmyselfrawhanddatastruct()

        rawhandsdoc = {"_id":str(handsdata["TIME"]) + " " + str(handsdata["ID"])}
        sb = handsdata["TABLE"]["SBLIND"]["CHIPS"]
        anti = handsdata["TABLE"]["ante"]
        playernum = len(handsdata["TABLE"]["SEAT"])

        stack = [0.0] * 10
        stack[9] = float(handsdata["TABLE"]["SEAT"][0]["CHIPS"])
        stack[8] = float(handsdata["TABLE"]["SEAT"][1]["CHIPS"])
        name = [0] * 10
        name[9] = handsdata["TABLE"]["SEAT"][0]["NAME"]
        name[8] = handsdata["TABLE"]["SEAT"][1]["NAME"]
        idlist = [0] * 10
        idlist[9] = handsdata["TABLE"]["SEAT"][0]["ID"]
        idlist[8] = handsdata["TABLE"]["SEAT"][1]["ID"]
        for idx in xrange(len(handsdata["TABLE"]["SEAT"]) - 2):
            stack[idx + 1] = float(handsdata["TABLE"]["SEAT"][- idx - 1]["CHIPS"])
            name[idx + 1] = handsdata["TABLE"]["SEAT"][- idx - 1]["NAME"]
            idlist[idx + 1] = handsdata["TABLE"]["SEAT"][- idx - 1]["ID"]

        rawhandsdoc["data"] = {}
        rawhandsdata = rawhandsdoc["data"]
        rawhandsdata["BB"] = float(sb) * 2
        rawhandsdata["ante"] = anti
        rawhandsdata["PLAYQUANTITY"] = playernum
        rawhandsdata["STACK"] = stack
        rawhandsdata["NAME"] = name
        rawhandsdata["ID"] = idlist
        rawhandsdata["BETDATA"] = {}

        betdata = handsdata["POKERCARD"]
        boarddata = ""
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.m_handsdata)
        for turnidx, pokerturn in enumerate(["PREFLOP", "FLOP", "TURN", "RIVER"]):
            if pokerturn not in betdata:
                continue
            curturnbetdata = betdata[pokerturn]["PLAYER"]
            newbetdata = []
            for actiondata in curturnbetdata:
                number = actiondata["NUMBER"]
                action = actiondata["ACTION"]
                if action == "showwait" or action.find("straddle") != -1:
                    continue
                # print action
                action, value = action.split(" ")
                pos = self.number2pos(number)
                newbetdata.append([pos, action, float(value)])
            if newbetdata:
                rawhandsdata["BETDATA"][pokerturn] = newbetdata
            if "CARD" in betdata[pokerturn]:
                boarddata += " "+betdata[pokerturn]["CARD"]

        showcarddata = handsdata["SHOWDOWN"]["PLAYER"]
        pvcards = [None] * 10
        for showcardinfo in showcarddata:
            if "CARD" not in showcardinfo:
                break
            pvcardsstr = showcardinfo["CARD"]
            number = showcardinfo["NUMBER"]
            pvcards[self.number2pos(number)] = pvcardsstr
        rawhandsdata["PVCARD"] = pvcards
        if boarddata:
            rawhandsdata["BOARD"] = boarddata[1:]
        else:
            rawhandsdata["BOARD"] = boarddata

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





def checkroom(club, room, identifier):
    room = str(room)
    result = DBOperater.Find(Constant.HANDSDB, Constant.COLLECTCHECKROOM, {})
    data = {}
    if result.count() != 0:
        # data = {room: [identifier, time.time()]}
        for doc in result:
            data = doc["data"]
    nowtime = time.time()
    for curroom in data.keys():
        if nowtime - data[curroom][1] > 36000:
            del data[curroom]
    resultvalue = "0"
    if room not in data:
        resultvalue = "1"
        data[room] = [identifier, time.time()]
    elif data[room][0] == identifier:
        resultvalue = "1"
    DBOperater.ReplaceOne(Constant.HANDSDB, Constant.COLLECTCHECKROOM, {"_id":"onlyone"}, {"_id":"onlyone", "data":data}, True)
    return resultvalue

class Crawler:
    def __init__(self):
        self.create_sessions()

    # def __del__(self):
    #     self.delete_sessions()

    def create_sessions(self):
        resopnse = requests.post("http://proxy.zyte.com:8011/sessions/", auth=HTTPBasicAuth('6398bdb3f1ec4a079b57f48bc32b9556', ''))
        print "===create session : ", resopnse.headers
        self.m_session = resopnse.headers["X-Crawlera-Session"]

    def delete_sessions(self):
        requests.delete('http://proxy.zyte.com:8011/sessions/' + self.m_session, auth=HTTPBasicAuth('6398bdb3f1ec4a079b57f48bc32b9556', ''))

    def get_real_url(self, url):
        ua = UserAgent()
        i_headers = {
            "User-Agent": str(ua.random),
        }
        print "get redirect url"
        response = requests.get(url, headers=i_headers, allow_redirects=False, timeout=30)
        print "get redirect url finish"
        print response.headers
        if 'Location' in response.headers:
            return response.headers["Location"]
        else:
            return self.get_real_url(url)

    def get_url_content(self, url):
        # url = self.get_real_url(url)
        ua = UserAgent()
        i_headers = {
            "User-Agent": str(ua.random),
            "X-Crawlera-cookies": "disable",
            "accept-encoding": "gzip, deflate, br",
            "X-Crawlera-Session": self.m_session
        }
        proxyMeta = "http://6398bdb3f1ec4a079b57f48bc32b9556:@proxy.crawlera.com:8011/"
        proxies = {"http": proxyMeta, "https": proxyMeta}
        # response = requests.get(url, headers=i_headers, proxies=proxies, verify="./zyte-smartproxy-ca.crt")
        response = requests.get(url, headers=i_headers)
        print "length : ", len(response.content)
        length = len(response.content)
        if length <= 1000:
            self.delete_sessions()
            self.create_sessions()
            print response.content
            return self.get_url_content(url)
        else:
            return response.content

# crawler = Crawler()

def uploadhandsurl(club, room, handsurl):
    room = str(room)
    handsurl = generateurl(handsurl)
    print "-------------==========:", handsurl
    handsdatastr = ""
    while True:
        try:
            htmldoc = crawler.get_url_content("http://" + handsurl)
            # print htmldoc
            # return htmldoc
            # return "ddd"
            # htmldoc = urlopen(handsurl).read()
            # print "======================"
            # print "======================"
            # print "======================"
            # print htmldoc
            # print "======================"
            # print "======================"
            # print "======================"
        except:
            print "open url error"
            traceback.print_exc()
            return "2"
        prefix = str("recordHelper.data = $.parseJSON('")
        postfix = str("');")

        # print("================:", type(htmldoc))
        prefixidx = htmldoc.find(prefix)
        postfixidx = htmldoc.find(postfix, prefixidx)
        handsdatastr = htmldoc[prefixidx+len(prefix):postfixidx]
        print "prefix : ", prefixidx, "\tpostfix : ", postfixidx
        if prefixidx != -1 and postfixidx != -1:
            print "success"
            break
        else:
            print "htmldoc : ", htmldoc
            # print "sleep"
            # time.sleep(10)
            return "3"
    # print "------handsdatastr:", handsdatastr
    try:
        # print ("======================", prefixidx)
        # print ("======================", postfixidx)
        # print ("======================")
        # print(handsdatastr)
        # print ("======================")
        # print ("======================")
        # print ("======================")
        handsdata = json.loads(handsdatastr)
        player_id_list = list()
        for seat_data in handsdata["STAGE"]["TABLE"]["SEAT"]:
            player_id_list.append(seat_data["ID"])
        # urlopen("http://{}/update_player_id/{}".format(Constant.REALTIMESERVERHOST, "_".join(player_id_list)))
        handsdata = ReconstructHandsdata(handsdata).getrawhanddatastruct()
        handsdata["rawstr"] = handsdatastr
    except:
        traceback.print_exc()
        print "error"
        return "2"
    DBOperater.ReplaceOne(Constant.HANDSDB, str(club), {"_id": handsdata["_id"]}, handsdata, True)
    handsidx = int(handsdata["_id"].split(" ")[-1])
    print "---------------------------------------------------------:",handsidx

    result = DBOperater.Find(Constant.HANDSDB, Constant.COLLECTINFOCLT, {})
    data = {}
    if result.count() != 0:
        for doc in result:
            data = doc["data"]
    for curroom in data.keys():
        if time.time() - data[curroom]["time"] > 36000:
            del data[curroom]
    if room not in data:
        data[room] = {"time": time.time(), "hands": []}
    if handsidx == 1 or handsidx - 1 in data[room]["hands"]:
    # if handsidx in data[room]["hands"]:
        print "finish"
        return "2"
    else:
        data[room]["hands"].append(handsidx)
        DBOperater.ReplaceOne(Constant.HANDSDB, Constant.COLLECTINFOCLT, {"_id": "onlyone"},
                              {"_id": "onlyone", "data": data}, True)
        print "insert success"
        return "1"

def fetchjoinedroom():
    result = DBOperater.Find(Constant.HANDSDB, Constant.JOINEDROOMCLT, {})
    result = list(result)

    if not len(result):
        return json.dumps([])

    data = result[0].get("data")
    # delete data of 24 hours ago
    for seq, gameinfo in data.items():
        if time.time() - gameinfo["time"] > 3600 * 24:
            del data[seq]

    DBOperater.ReplaceOne(Constant.HANDSDB, Constant.JOINEDROOMCLT, {"_id": "onlyone"},
                          {"_id": "onlyone", "data": data}, True)
    return json.dumps([int(v[0]) for v in data.items()])

def joinroom(roomid):
    seq = int(roomid)
    # this deals with the collect game information, add this seq to the to be collected list
    result = DBOperater.Find(Constant.HANDSDB, Constant.JOINEDROOMCLT, {})
    result = list(result)
    if not len(result):
        data = {}
    else:
        data = result[0].get("data")
    data[str(seq)] = {
        # "handidx": 0,
        "time": time.time(),
        # "phoneid": None
    }
    DBOperater.ReplaceOne(Constant.HANDSDB, Constant.JOINEDROOMCLT, {"_id": "onlyone"},
                          {"_id": "onlyone", "data": data}, True)
    return "1"

def fetchuploadsuccess():
    result = DBOperater.Find(Constant.HANDSDB, Constant.UPLOADSUCCESS, {})
    result = list(result)

    if not len(result):
        return "0"
    else:
        success = result[0].get("data")
        if success:
            DBOperater.ReplaceOne(Constant.HANDSDB, Constant.UPLOADSUCCESS, {"_id": "onlyone"},
                                  {"_id": "onlyone", "data": False}, True)
            print "success:", success
            return "1"
        return "0"

def cleanroom():
    DBOperater.ReplaceOne(Constant.HANDSDB, Constant.JOINEDROOMCLT, {"_id": "onlyone"},
                          {"_id": "onlyone", "data": {}}, True)
    return "1"


def reconstructallhands():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})
    for doc in result:
        # if doc["_id"] != "2019-07-23 19:19:42 133":
        #     continue
        handsdatastr = doc["rawstr"]
        handsdata = json.loads(handsdatastr)
        handsdata = ReconstructHandsdata(handsdata).getrawhanddatastruct()
        handsdata["rawstr"] = handsdatastr
        DBOperater.ReplaceOne(Constant.HANDSDB,Constant.HANDSCLT,{"_id":doc["_id"]},handsdata)

class SocketServer:
    def __init__(self):
        ip_port = ("192.168.0.21", 9998)
        web = socket.socket()
        web.bind(ip_port)
        web.listen(5)
        while True:
            print "wati for accept"
            conn, addr = web.accept()
            print "wati for data"
            data = conn.recv(1024)
            print "data : ", data + "123"

            response = requests.get(data.strip(), timeout=1800)
            print "response : ", response.content
            print "header : ", response.headers

            # data = data.split("/")
            print data[-3], data[-2], data[-1]
            # conn.send(bytes(uploadhandsurl(data[-3], data[-2], data[-1])))
            conn.send(bytes(response.content))
            # import time
            # time.sleep(20)
            # conn.send(bytes("1"))
            conn.close()


if __name__ == "__main__":
    # response = requests.get(bytes("http://192.168.0.21:8080/init/8_2_1_0S0S_5_0_424_303_809_329_143_559_0_596_369_0_0_0_0_0_0_0_0_0_0"), timeout=30)
    # print "response : ", response.content
    SocketServer()
    # reconstructallhands()