# this file is not completed yet.
# tjafterflopstate function is not completed yet, I've copied
# the code from tongjihandsinfo and prefloprange. And I've calculated
# the realtime size of pot. But many code need to be written calfully
import Constant
import handsinfocommon

from tongjihandsinfo import *

HEADER = Constant.TAB.join(["range","relativepos","playernumber",
                            "flopattack","turnattack","riverattack",
                            "boardvalue","handsstrength","buystrength",
                            "action"])

class afterflopstate:
    def __init__(self, handsdata, anti, bbvalue):
        self.m_handsdata = handsdata
        self.m_anti = anti
        self.m_bbvalue = bbvalue

        self.m_playerquantitiy = 0

        self.checkvalid()

    def checkvalid(self):
        showcard = self.m_handsdata["showcard"]
        if not (showcard >= 0 or showcard == -3):
            return False
        else:
            return True

    def calplayerquantity(self):
        self.m_playerquantitiy = len(self.m_handsinfo["data"][0][2])

    def writeheader(self):
        file = open(Constant.AFTERFLOPSTATEHEADER,"w")
        file.write(HEADER)
        file.close()

    def calpreflopstate(self):
        preflopaction = self.m_handsdata["data"][1]

def tjafterflopstate(handsdata, anti, bbvalue):
# def calinvest(invest,actiondict,inpool,anti,bbvalue,handsdata,inpoolstate):
    showcard  = handsdata["showcard"]
    if not (showcard >= 0 or showcard == -3):
        return

    invest = {}
    actiondict = {}


    inpool = handsdata[0][2]
    inpoolstate = [0]*10
    for pos in inpool:
        inpoolstate[pos] = 1
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
    openraiser = 0

    playerquantitiy = len(handsdata["data"][0][2])
    if playerquantitiy < 6:
        return

    bb = bbvalue
    total = anti * playerquantitiy + bb + bb / 2

    writelinelist = []

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
                total = total + curbet - totalinvest[curplayer]
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
                    total = total + curbet - totalinvest[curplayer]
                    totalinvest[curplayer] = value
                    allinplayer += 1
                    inpoolstate[curplayer] = 2
                    action = 4.6



                    if raiser == 0:
                        raiser = curplayer
                else:
                    # raise all in
                    curbet = value
                    total = total + curbet - totalinvest[curplayer]
                    totalinvest[curplayer] = curbet
                    allinplayer += 1
                    inpoolstate[curplayer] = 2
                    action = 4.2


                    raiser = curplayer
            elif action == 6:
                # call
                total = total + curbet - totalinvest[curplayer]
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
        # enumerate action over
        if roundnum == 1:
            if curbet == bbvalue:
                # no raiser
                openraiser = 0
            else:
                openraiser = raiser
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
    # enumerate each round over
    actiondict["total"] = alltotalaction

    return showcard
