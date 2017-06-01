import DBOperater
import Constant

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

if __name__ == "__main__":
    totalplayer()
    playerhandsdis()
    payoffdis()