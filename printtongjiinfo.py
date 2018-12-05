import DBOperater
import Constant
import pprint
import handsinfocommon
import sys
import time
import random

def totalplayer():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})

    playerdoc = result.next()
    playerinfo = playerdoc["name"]

    print "total player:", len(playerinfo)

def playerhandsdis():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})

    playerdoc = result.next()
    playerinfo = playerdoc["name"]

    handsdis = {}
    for info in playerinfo.values():
        handsnum = info["hands"]
        if handsnum not in handsdis:
            handsdis[handsnum] = 0
        handsdis[handsnum] += 1

    handsnumlist = handsdis.keys()
    handsnumlist.sort(reverse=True)

    for idx in xrange(100):
        key = handsnumlist[idx]
        print key," : ",handsdis[key]

def payoffdis():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})

    playerdoc = result.next()
    playerinfo = playerdoc["name"]

    handsdis = {}
    for info in playerinfo.values():
        handsnum = info["payoff"]
        if handsnum not in handsdis:
            handsdis[handsnum] = 0
        handsdis[handsnum] += 1

    handsnumlist = handsdis.keys()
    handsnumlist.sort(reverse=True)

    for idx in xrange(100):
        key = handsnumlist[idx]
        print key," : ",handsdis[key]

    handsnumlist.sort()

    for idx in xrange(100):
        key = handsnumlist[idx]
        print key," : ",handsdis[key]

def printcombinationinfo():
    print "possible hands:",handsinfocommon.combination(52,2)
    print "possible hands after removing symmetry:",13 * 12 * 2 + 13
    print "possible flop:",handsinfocommon.combination(52,3)
    print "possible turn:",handsinfocommon.combination(52,4)
    print "possible river:",handsinfocommon.combination(52,5)


def preflopftdata():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPREPAIRJOINRATEDOC})
    rawdata1 = result.next()
    print "rawkey: ",rawdata1.keys()
    for key in rawdata1.keys():
        if key == "_id":
            continue
        rawdata = rawdata1[key]
        # rawdata = rawdata[Constant.FTDATA]
        pp = pprint.PrettyPrinter(indent= 4)
        # for pos, data in rawdata.items():
        print "---------------------------------------rawdatakey: ",key,"----------------------------------"
        print rawdata.keys()
        for idx in rawdata.keys():
            # print ""
            pos = idx
            data = rawdata[pos]
            print "====================="*2,pos,"==========================="*2
            betbblist = data.keys()
            betbblist.sort(key = lambda v:int(v),reverse=True)

            for key in betbblist:
                print "betbb: ",key
                pp.pprint(data[key])

def printdatalen6():
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{})
    showcardinfo = {}
    for rawdata in result:
        showcard = rawdata["showcard"]
        if showcard not in showcardinfo:
            showcardinfo[showcard] = 0
        showcardinfo[showcard] += 1
    handsinfocommon.pp.pprint(showcardinfo)
    sumhands = sum(showcardinfo.values())
    for key in showcardinfo.keys():
        showcardinfo[key] /= sumhands * 1.0
    print "============================="
    handsinfocommon.pp.pprint(showcardinfo)
    print "sumhands :   ",sumhands

def printhandsinfo(handsid):
    result = DBOperater.Find(Constant.HANDSDB,Constant.STATEINFOHANDSCLT,{"_id":handsid})
    print "handsid:",handsid
    handsinfocommon.pp.pprint(result.next())

def printrandomhandsinfo():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})
    doclen = result.count()
    rate = 1.0 / min(doclen,10000)
    for doc in result:
        if random.random() < rate:
            handsinfocommon.pp.pprint(doc)
            break

def printplayerquantitydis():
    doclen = {}
    for idx in xrange(1,10):
        result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{"data.PLAYQUANTITY":idx})
        doclen[idx] = result.count()
    totaldoc = sum(doclen.values())
    for key, value in doclen.items():
        print key,":",value * 1.0 / totaldoc * 100

def printcollectgamedata():
    result = DBOperater.Find(Constant.HANDSDB,Constant.COLLECTGAMECLT,{})
    if result.count() == 0:
        print "no data"
        return
    doc = result.next()
    doc = doc["data"]
    keylist = doc.keys()
    keylist.sort(key = lambda v:int(v))
    for key in keylist:
        curtime = time.localtime(doc[key]["time"])
        print key,"\t",curtime.tm_mday,"\t",curtime.tm_hour,doc[key]["phoneid"]

def printgameseqdata():
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":Constant.getphoneid(sys.argv[2])})
    if result.count() == 0:
        print "no data"
        return
    doc = result.next()
    doc = doc["data"]
    keylist = doc.keys()
    keylist.sort(key = lambda v:int(v))
    for key in keylist:
        curtime = time.localtime(doc[key])
        print key,"\t",curtime.tm_mday,"\t",curtime.tm_hour

def printmisscollectgameseq():
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":Constant.getphoneid(sys.argv[2])})
    if result.count() == 0:
        print "no data"
        return
    doc = result.next()
    doc = doc["data"]
    keylist = doc.keys()
    keylist.sort(key = lambda v:int(v))

    result = DBOperater.Find(Constant.HANDSDB,Constant.COLLECTGAMECLT,{})
    if result.count() == 0:
        print "no data"
        return
    newdoc = result.next()
    newdoc = newdoc["data"]
    for key in keylist:
        if key in newdoc:
            curtime = time.localtime(doc[key])
            print key,"\t",curtime.tm_mday,"\t",curtime.tm_hour

if __name__ == "__main__":
    # totalplayer()
    # playerhandsdis()
    # payoffdis()
    # printdatalen6()
    #  printcombinationinfo()
    # preflopftdata()
    # printplayerquantitydis()
    if len(sys.argv) == 1:
        printrandomhandsinfo()
    elif sys.argv[1] == "1":
        printcollectgamedata()
    elif sys.argv[1] == "2":
        printgameseqdata()
    elif sys.argv[1] == "3":
        printmisscollectgameseq()
    else:
        printhandsinfo(sys.argv[1])