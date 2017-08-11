import DBOperater
import Constant
import pprint
import handsinfocommon

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
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{"_id":handsid})
    handsinfocommon.pp.pprint(result.next())

if __name__ == "__main__":
    # totalplayer()
    # playerhandsdis()
    # payoffdis()
    # preflopftdata()
    # printdatalen6()
    # prefloprepaireddata()
    #  printcombinationinfo()
    # preflopftdata()
    printhandsinfo("35357006093039820170320130340")
