import DBOperater
import Constant
import hunlgame
import copy
import traceback
import time

def nextplayer(inpoolstate,curplayer):
    for i in xrange(curplayer - 1,0,-1):
        if inpoolstate(i) == 1:
            return i
    for i in xrange(len(inpoolstate),curplayer ,-1):
        if inpoolstate(i) == 1:
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
    inpoolinvestlist = inpoolinvest.keys()
    inpoolinvestlist.sort()
    inpoolinvestlist.insert(0,0)
    for idx in xrange(len(inpoolinvestlist[1:])):
        lowbound = inpoolinvestlist[idx]
        upperbound = inpoolinvestlist[idx + 1]
        newsep = [copy.deepcopy(inpoolinvest[upperbound]),0]
        for idx,value in enumerate(gameinvest):
            if value <= lowbound:
                continue
            if value > upperbound:
                newsep += (upperbound - lowbound)
            else:
                newsep += (value - lowbound)

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

    board = handsdata[-1]
    privatecard = handsdata[-2]

    if not isprivatecardvalid():
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
        newprivatecard = extractprivatecard(competitor,potsize)
        winner = hunlgame.getwinner(board,newprivatecard)
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
            curplayer = inpool[1]
            totalinvest[0] = bbvalue / 2
            totalinvest[1] = bbvalue
        else:
            curplayer = inpool[-1]

        currounddata = handsdata[roundnum]


        totalaction = []
        for idx in xrange(9):
            totalaction.append({})

        curbet = 0
        # enumerate each action
        for actioninfo in currounddata:
            curplayer = nextplayer(inpoolstate, curplayer)
            curactiondict = totalaction[curplayer - 1]
            allcuractiondict = alltotalaction[curplayer - 1]

            action = actioninfo[0]
            value = actioninfo[1]

            if action == 1:
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

            if action not in curactiondict:
                curactiondict[action] = 0
            curactiondict[action] += 1

            if action not in allcuractiondict:
                allcuractiondict[action] = 0
            allcuractiondict[action] += 1

        invest[roundnum] = totalinvest[1:]
        actiondict[roundnum] = totalaction
        if remainplayer - allinplayer == 1:
            # bet over
            if allinplayer == 0:
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

    gameinvest = [0]*10
    for investlist in invest.values():
        for idx, value in enumerate(investlist):
            gameinvest[idx + 1] += gameinvest[idx]
    invest["total"]  = gameinvest[1:]

    seppotresult = seppot(gameinvest,inpoolstate)

    showcard = calinvest(invest,inpool,anti,bbvalue,handsdata,inpoolstate)

    payofflist = calpayoff(showcard,action,seppotresult,inpoolstate,gameinvest,handsdata)
    if not payofflist:
        # cannot calculate payoff, this hand must be abandoned
        pass
        return False

    handsinfo["payoff"] = payofflist[1:]
    handsinfo["invest"] = invest
    handsinfo["action"] = action

def tongjimain():
    result = DBOperater.StoreData(Constant.HANDSDB,Constant.HANDSCLT,{})

    for rawhand in result:
        try:
            curid = rawhand["_id"]
            tongjiinfo(rawhand)

            # store history hands data
            DBOperater.StoreData(Constant.HANDSDB,Constant.TJHISHANDSCLT,rawhand)

            # store complete hands data
            DBOperater.StoreData(Constant.HANDSDB,Constant.TJHANDSCLT,rawhand)

            # remove raw hands data
            delresult = DBOperater.DeleteData(Constant.HANDSDB,Constant.HANDSCLT,{"_id":curid})
            if delresult.deleted_count == 0:
                print "error: the _id is ",curid
                break
        except KeyboardInterrupt:
            raise
        except:
            print "excepttion occur:",curid
            traceback.print_exc()
        # break

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
    main()
