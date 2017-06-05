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

# no matter if some one all in
def virtualnextplayer(inpoolstate,curplayer):
    for i in xrange(curplayer - 1,0,-1):
        if inpoolstate[i] != 0:
            return i
    for i in xrange(len(inpoolstate) - 1,curplayer ,-1):
        if inpoolstate[i] != 0:
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
            if not winner:
                # read winner fail
                return []

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

    isactionvalid = True

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

        # if not isactionvalid:
        #     # not valid last round
        #     pass
        # else:
        isactionvalid = False
        raiser = 0

        # enumerate each action
        for actioninfo in currounddata:
            if virtualnextplayer(inpoolstate, curplayer) == raiser:
                #error, should have end this turn, this checks the case when extra actin is recorded
                print "extra action"
                return -1
                pass


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
                if curbet >= value:
                    # record wrong
                    print "error, raise value smaller than bet value"
                    return -1

                curbet = value
                totalinvest[curplayer] = curbet

                raiser = curplayer
            elif action == 3:
                # check
                pass

                if raiser == 0:
                    raiser = curplayer
            elif action == 4:
                # all in
                if value <= curbet:
                    # call all in
                    totalinvest[curplayer] = value
                    allinplayer += 1
                    inpoolstate[curplayer] = 2
                    action = 4.6



                    if raiser == 0:
                        raiser = curplayer
                else:
                    # raise all in
                    curbet = value
                    totalinvest[curplayer] = curbet
                    allinplayer += 1
                    inpoolstate[curplayer] = 2
                    action = 4.2


                    raiser = curplayer
            elif action == 6:
                # call
                totalinvest[curplayer] = curbet


                if curbet == 0:
                    # error, call bet 0
                    print "call bet 0"
                    return -1

                if raiser == 0:
                    raiser = curplayer
            elif action == 12:
                # win pot
                for iiidx in xrange(len(inpoolstate)):
                    inpoolstate[iiidx] = 0
                inpoolstate[curplayer] = 1
                remainplayer = 1
                allinplayer= 0


                isactionvalid = True

            if virtualnextplayer(inpoolstate, curplayer) == raiser:
                # this turn end
                pass

                isactionvalid = True

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

        if not isactionvalid:
            # this checks when not enough action is recorded
            print "not enough action"
            return -1

    actiondict["total"] = alltotalaction

    return showcard

# return the result of basic info statistical, such as if the hands is valid
def tongjiinfo(handsinfo,bbvalue,anti):
    handsdata = handsinfo["data"]

    # read info
    if bbvalue != handsdata[0][0]:
        return -2
    inpool = handsdata[0][2]
    #anti = handsdata[0][1] / len(inpool)

    # start from index 1, value 0 means fold, value 1 means in pool, value 2 means all in
    inpoolstate = [0]*10
    for pos in inpool:
        inpoolstate[pos] = 1

    invest = {  }
    action = {  }

    showcard = calinvest(invest,action,inpool,anti,bbvalue,handsdata,inpoolstate)

    if showcard == -1:
        # action record error
        print "action error:",handsinfo ["_id"]
        return -2

    gameinvest = [0]*10
    for investlist in invest.values():
        for idx, value in enumerate(investlist):
            gameinvest[idx + 1] += value

    invest["total"]  = gameinvest[1:]

    seppotresult = seppot(gameinvest,inpoolstate)

    payofflist = calpayoff(showcard,seppotresult,inpoolstate,gameinvest,handsdata)
    if not payofflist:
        # cannot calculate payoff, this hand must be abandoned, mainly because fail to record show card
        print "empty payoff:",handsinfo["_id"]
        pass
        return -3

    if sum(payofflist) != 0:
        # cannot calculate payoff, this hand must be abandoned, check specific reason
        pass
        print "sum not zero:",handsinfo ["_id"]

        return -1

    handsinfo["payoff"] = json.dumps(payofflist[1:])
    handsinfo["invest"] = json.dumps(invest)
    handsinfo["action"] = json.dumps(action)
    handsinfo["showcard"] = showcard

    #return True
    return showcard

    # if len(seppotresult) == 5:
    #     import pprint
    #     pp = pprint.PrettyPrinter(indent=4)
    #     pp.pprint(handsinfo)
    #     print "="*100
    #     pp.pprint(seppotresult)
    #     abc

def removecumuinfo():
    DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})

def removetjinfo():
    DBOperater.DeleteData(Constant.HANDSDB,Constant.TJHANDSCLT,{})

# tongji total wins, and total hands
def tongjicumuinfo(handsinfo):
    # update all player
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})
    if result.count() == 0:
        playerdoc = {"_id":"player","name":{}}
    else:
        playerdoc = result.next()

    playerinfo = playerdoc["name"]

    for playername in handsinfo["playername"]:
        playername = playername.replace(".","_dot_")
        playername = playername.replace("$","_dollar_")
        if playername not in playerinfo:
            playerinfo[playername] = {"payoff":0,"hands":0}

        playerinfo[playername]["hands"] += 1

    payoff = json.loads(handsinfo["payoff"])

    inpool = handsinfo["data"][0][2]

    inpoolcopy = copy.deepcopy(inpool)
    inpoolcopy.sort()

    for idx,pos in enumerate(inpool):
        playername = handsinfo["playername"][idx]
        playername = playername.replace(".","_dot_")
        playername = playername.replace("$","_dollar_")
        playerpayoff = payoff[pos - 1]

        playerinfo[playername]["payoff"] += playerpayoff

    if result.count() != 0:
        DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"})

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"},playerdoc,True)

    # update total win
def tongjimain():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})
    doclen =  result.count()

    iternum = doclen / 10000 + 1
    for idx in xrange(iternum):
        tongjimain_(idx)

def tongjimain_(idx):
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})

    wronghands  = 0
    cnt = 0
    showcardinfo = {}

    for rawhand in result:
        cnt  += 1
        if cnt < idx * 10000:
            continue

        if cnt >= (idx+1) * 10000:
            break

        if cnt % 1000 == 0:
            print "="*100,cnt,"   --wrong--   :",wronghands

        if cnt % 10000 == 0:
            print "-"*100
            print showcardinfo

        try:
            curid = rawhand["_id"]

            # store history hands data
            DBOperater.ReplaceOne(Constant.HANDSDB,Constant.TJHANDSCLT,{"_id":curid},rawhand,True)

            showcard = tongjiinfo(rawhand,Constant.BB,Constant.ANTI)

            if showcard not in showcardinfo:
                showcardinfo[showcard] = 0
            showcardinfo[showcard] += 1

            if showcard < 0:
                #print "ID:",rawhand["_id"]
                wronghands += 1
                rawhand["showcard"] = showcard
                # continue
            else:
                tongjicumuinfo(rawhand)

            # store complete hands data
            DBOperater.ReplaceOne(Constant.HANDSDB,Constant.TJHANDSCLT,{"_id":curid},rawhand,True)

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
    print "wronghands:",wronghands
    print showcardinfo

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
    #DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":"player"},{"_id":"player","ts":12},True)
    removecumuinfo()
    removetjinfo()
    tongjimain()
    #tongjicumuinfo(0)
