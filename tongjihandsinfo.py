import DBOperater
import Constant
import hunlgame
import copy
import traceback
import time
import json
import handsinfocommon

def nextplayer(inpoolstate,curplayer):
    for i in xrange(curplayer - 1,0,-1):
        if inpoolstate[i] == 1:
            return i
    for i in xrange(len(inpoolstate) - 1,curplayer ,-1):
        if inpoolstate[i] == 1:
            return i
    return 0

def isprivatecardvalid(privatecard,inpoolstate):
    for idx, state in enumerate(inpoolstate):
        if state != 0:
            hands = privatecard[idx - 1][0]
            for i in hands:
                for v in i:
                    if v == 0:
                        return False
    return True

def extractprivatecard(competitor, privatecard):
    newprivatecard = []
    for pos in competitor:
        newprivatecard.append(privatecard[pos - 1][0])
    return newprivatecard

def readwinner(privatecard):
    winner = []
    for idx,hands in enumerate(privatecard):
        if hands[1] == 1:
            winner.append(idx+1)
    return winner

def calpot(gameinvest, pos):
    base = gameinvest[pos]
    potsize = 0
    for value in gameinvest:
        if value > base:
            potsize += base
        else:
            potsize += value
    return potsize

# the return value : [[[pot competitor],pot size],...]
def seppot(gameinvest, inpoolstate):
    potresult = []
    inpoolinvest = {}
    for idx, state in enumerate(inpoolstate):
        if state != 0:
            value = gameinvest[idx]
            if value not in inpoolinvest:
                inpoolinvest[value] = []
            inpoolinvest[value].append(idx)
    # print "-"*100
    # print gameinvest
    # print inpoolinvest

    inpoolinvestlist = inpoolinvest.keys()
    inpoolinvestlist.sort()
    inpoolinvestlist.insert(0,0)
    for idx in xrange(len(inpoolinvestlist[1:])):
        lowbound = inpoolinvestlist[idx]
        upperbound = inpoolinvestlist[idx + 1]
        newsep = [[],0]

        for betvalue in inpoolinvestlist[idx + 1:]:
            newsep[0].extend(inpoolinvest[betvalue])

        for idx,value in enumerate(gameinvest):
            if value <= lowbound:
                continue
            if value > upperbound:
                newsep[1] += (upperbound - lowbound)
            else:
                newsep[1] += (value - lowbound)

        potresult.append(newsep)

    return potresult

def calpayoff(showcard, seppotresult,inpoolstate,gameinvest ,handsdata = []):
    if showcard != 1:
        # donot showcard
        payofflist = [0]* 10
        for idx, value in enumerate(gameinvest):
            if inpoolstate[idx] == 0:
                # fold
                payofflist[idx] = - value
            else:
                payofflist[idx] = sum(gameinvest) - value
        return payofflist

    # show card, compare card strength
    inpoolnum = 0
    for value in inpoolstate:
        if value != 0:
            inpoolnum += 1

    board = handsinfocommon.getboard(handsdata)
    privatecard = handsdata[5]

    if not isprivatecardvalid(privatecard, inpoolstate):
        # read card fail, try to read the winner
        if len(seppotresult) == 1:
            # no side pot, we can read the winner directly
            winner = readwinner(privatecard)

            payofflist = [0]*10
            for idx, value in enumerate(gameinvest):
                if idx in winner:
                    # winner
                    payofflist[idx] = sum(gameinvest) / len(winner) - value
                else:
                    # fold
                    payofflist[idx] = - value
            return payofflist
        else:
            # sep pot, but donot read hand card, cannot calculate
            return []

    # start to compare card
    payofflist = [0]*10
    for idx,value in enumerate(gameinvest):
        payofflist[idx] = - value

    for potinfo in seppotresult:
        competitor = potinfo[0]
        potsize = potinfo[1]
        newprivatecard = extractprivatecard(competitor,privatecard)
        winner = hunlgame.getwinner(board,newprivatecard,-1)
        for idx in xrange(len(winner)):
            winner[idx] = competitor[winner[idx]]

        for pos in winner:
            payofflist[pos] += (potsize / len(winner))

    return payofflist

def calinvest(invest,actiondict,inpool,anti,bbvalue,handsdata,inpoolstate):
    remainplayer = len(inpool)
    allinplayer = 0

    antilist = [0]*10
    for pos in inpool:
        antilist[pos] = anti
    invest[0] = antilist[1:]

    showcard = 1

    alltotalaction = []
    for idx in xrange(9):
        alltotalaction.append({})
    # enumerate each round
    for roundnum in xrange(1,5):
        totalinvest = [0] * 10
        if roundnum == 1:
            curbet = bbvalue
            curplayer = inpool[1]

            totalinvest[inpool[0]] = bbvalue / 2
            totalinvest[inpool[1]] = bbvalue
        else:
            curbet = 0
            curplayer = inpool[-1]

        currounddata = handsdata[roundnum]

        totalaction = []
        for idx in xrange(9):
            totalaction.append({})

        # enumerate each action
        for actioninfo in currounddata:
            curplayer = nextplayer(inpoolstate, curplayer)
            curactiondict = totalaction[curplayer - 1]
            allcuractiondict = alltotalaction[curplayer - 1]

            action = actioninfo[0]
            value = actioninfo[1]

            if action == 1 or action == -1:
                # fold
                remainplayer -= 1
                inpoolstate[curplayer] = 0
            elif action == 2:
                # raise
                curbet = value
                totalinvest[curplayer] = curbet
            elif action == 3:
                # check
                pass
            elif action == 4:
                # all in
                if value <= curbet:
                    # call all in
                    totalinvest[curplayer] = value
                    allinplayer += 1
                    inpoolstate[curplayer] = 2
                    action = 4.6
                else:
                    # raise all in
                    curbet = value
                    totalinvest[curplayer] = curbet
                    allinplayer += 1
                    inpoolstate[curplayer] = 2
                    action = 4.2
            elif action == 6:
                # call
                totalinvest[curplayer] = curbet
            elif action == 12:
                # win pot
                for iiidx in xrange(len(inpoolstate)):
                    inpoolstate[iiidx] = 0
                inpoolstate[curplayer] = 1
                remainplayer = 1
                allinplayer= 0

            if action not in curactiondict:
                curactiondict[action] = 0
            curactiondict[action] += 1

            if action not in allcuractiondict:
                allcuractiondict[action] = 0
            allcuractiondict[action] += 1

        invest[roundnum] = totalinvest[1:]
        actiondict[roundnum] = totalaction
        if remainplayer - allinplayer <= 1 :
            # bet over
            if remainplayer == 1:
                # game over
                showcard = 0
                break
            else:
                # all in
                break
    actiondict["total"] = alltotalaction

    return showcard

def tongjiinfo(handsinfo):
    handsdata = handsinfo["data"]

    # read info
    bbvalue = handsdata[0][0]
    inpool = handsdata[0][2]
    anti = handsdata[0][1] / len(inpool)

    # start from index 1, value 0 means fold, value 1 means in pool, value 2 means all in
    inpoolstate = [0]*10
    for pos in inpool:
        inpoolstate[pos] = 1

    invest = {  }
    action = {  }

    showcard = calinvest(invest,action,inpool,anti,bbvalue,handsdata,inpoolstate)

    gameinvest = [0]*10
    for investlist in invest.values():
        for idx, value in enumerate(investlist):
            gameinvest[idx + 1] += value

    invest["total"]  = gameinvest[1:]

    seppotresult = seppot(gameinvest,inpoolstate)

    payofflist = calpayoff(showcard,seppotresult,inpoolstate,gameinvest,handsdata)
    if not payofflist:
        # cannot calculate payoff, this hand must be abandoned
        pass
        return False

    handsinfo["payoff"] = json.dumps(payofflist[1:])
    handsinfo["invest"] = json.dumps(invest)
    handsinfo["action"] = json.dumps(action)

    # if len(seppotresult) == 5:
    #     import pprint
    #     pp = pprint.PrettyPrinter(indent=4)
    #     pp.pprint(handsinfo)
    #     print "="*100
    #     pp.pprint(seppotresult)
    #     abc

# tongji total wins, and total hands
def tongjicumuinfo(handsinfo):
    # update all player
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})
    if result.count() == 0:
        playerdoc = {"_id":"player","name":{}}
    else:
        playerdoc = result.next()

    for playername in handsinfo["playername"]:
        playerdoc[playername] = 1

    if result.count() != 0:
        DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"},playerdoc)


    # update total win


def tongjimain():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})

    for rawhand in result:
        try:
            curid = rawhand["_id"]

            # store history hands data
            try:
                DBOperater.StoreData(Constant.HANDSDB,Constant.TJHISHANDSCLT,rawhand)
            except:
                DBOperater.DeleteData(Constant.HANDSDB,Constant.TJHISHANDSCLT,{"_id":curid})
                DBOperater.StoreData(Constant.HANDSDB,Constant.TJHISHANDSCLT,rawhand)

            tongjiinfo(rawhand)

            tongjicumuinfo(rawhand)

            # store complete hands data
            try:
                DBOperater.StoreData(Constant.HANDSDB,Constant.TJHANDSCLT,rawhand)
            except:
                DBOperater.DeleteData(Constant.HANDSDB,Constant.TJHANDSCLT,{"_id":curid})
                DBOperater.StoreData(Constant.HANDSDB,Constant.TJHANDSCLT,rawhand)

            # remove raw hands data
            # delresult = DBOperater.DeleteData(Constant.HANDSDB,Constant.HANDSCLT,{"_id":curid})
            # if delresult.deleted_count == 0:
            #     print "error: the _id is ",curid
            #     break
        except KeyboardInterrupt:
            raise
        except:
            print "excepttion occur:",curid
            traceback.print_exc()
            raise
        #break

def main():
    while True:
        try:
            tongjimain()
            time.sleep( 10)
        except KeyboardInterrupt:
            raise
        except:
            print "excepttion occur:"
            traceback.print_exc()

if __name__ == "__main__":
    #main()
    #tongjimain()
    tongjicumuinfo(0)
