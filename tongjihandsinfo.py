import DBOperater
import Constant

def nextplayer(inpoolstate,curplayer):
    for i in xrange(curplayer - 1,0,-1):
        if inpoolstate(i) == 1:
            return i
    for i in xrange(len(inpoolstate),curplayer ,-1):
        if inpoolstate(i) == 1:
            return i
    return 0

def tongjiinfo(handsinfo):
    handsdata = handsinfo["data"]

    # read info
    bbvalue = handsdata[0][0]
    inpool = handsdata[0][2]
    anti = handsdata[0][1] / len(inpool)

    # initialize temp var
    curplayer = 0
    remainplayer = len(inpool)
    allinplayer = 0
    # start from index 1, value 0 means fold, value 1 means in pool, value 2 means all in
    inpoolstate = [0]*10
    for pos in inpool:
        inpoolstate[pos] = 1

    invest = { 0:{}  }
    for pos in inpool:
        invest[0][pos] = anti

    showcard = 1
    # enumerate each round
    for roundnum in xrange(1,5):
        if roundnum == 1:
            curplayer = inpool[1]
        else:
            curplayer = inpool[-1]

        currounddata = handsdata[roundnum]
        totalinvest = [0] * 10

        curbet = 0
        # enumerate each action
        for actioninfo in currounddata:
            curplayer = nextplayer(inpoolstate, curplayer)
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
                else:
                    # raise all in
                    curbet = value
                    totalinvest[curplayer] = curbet
                    allinplayer += 1
                    inpoolstate[curplayer] = 2
            elif action == 6:
                # call
                totalinvest[curplayer] = curbet
        invest[roundnum] = totalinvest
        if remainplayer - allinplayer == 1:
            # bet over
            if allinplayer == 0:
                # game over
                showcard = 0
                break
            else:
                # all in
                break

    winner = []
    if showcard == 1:
        # compare hands
        pass
    else:
        for pos,state in enumerate(inpoolstate):
            if state == 1 or state == 2:
                winner.append(pos)

