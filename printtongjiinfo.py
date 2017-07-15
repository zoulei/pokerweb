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
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    rawdata = result.next()
    print "rawkey: ",rawdata.keys()
    rawdata = rawdata[Constant.FTDATA]
    # rawdata = rawdata[Constant.FTDATA]
    pp = pprint.PrettyPrinter(indent= 4)
    # for pos, data in rawdata.items():
    print "rawdata"
    print rawdata.keys()
    pos = "9"
    data = rawdata[pos]
    print "====================="*2,pos,"==========================="*2
    betbblist = data.keys()
    betbblist.sort(key = lambda v:int(v),reverse=True)

    for key in betbblist:
        print "betbb: ",key
        pp.pprint(data[key])

def prefloprepaireddata():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    rawdata = result.next()
    rawdata = rawdata[Constant.REPAIRJOINRATE]
    # rawdata = rawdata[Constant.FTDATA]
    pp = pprint.PrettyPrinter(indent= 4)
    # for pos, data in rawdata.items():
    pos = "9"
    data = rawdata[pos]
    print "====================="*2,pos,"==========================="*2
    betbblist = data.keys()
    betbblist.sort(key = lambda v:int(v),reverse=True)

    for key in betbblist:
        print "betbb: ",key
        pp.pprint(data[key])

def printdatalen6():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})
    null2 = 0
    null3 = 0 # preflop all in
    null4 = 0 # flop all in
    yes7 = 0 # play to river
    total = 0 # show card
    for rawdata in result:
        if len(rawdata["data"]) >= 6:
            # total += 1
            if isinstance(rawdata["data"][5][0][0],list):
                total += 1
            if isinstance(rawdata["data"][5][0][0],list) and rawdata["data"][2] == None:
                null2 += 1
            elif isinstance(rawdata["data"][5][0][0],list) and rawdata["data"][3] == None:
                # preflop all in
                null3 += 1
            elif isinstance(rawdata["data"][5][0][0],list) and rawdata["data"][4] == None:
                # flop all in
                null4 += 1
            if isinstance(rawdata["data"][5][0][0],list) and len(rawdata["data"]) == 7 and  rawdata["data"][4] == None:
                # play to river
                yes7 += 1
                # print rawdata["_id"]
        if len(rawdata["data"]) == 6:
            if not isinstance(rawdata["data"][5][0][0],list):
                print rawdata["_id"]
    print null2
    print null3
    print null4
    print yes7
    print total
                # print rawdata["_id"]

if __name__ == "__main__":
    # totalplayer()
    # playerhandsdis()
    # payoffdis()
    # printdatalen6()
    # prefloprepaireddata()
    #  printcombinationinfo()
    preflopftdata()