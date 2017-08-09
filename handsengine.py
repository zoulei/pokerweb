import Constant
import handsinfocommon
import copy
import DBOperater
import hunlgame


# the function that calculate preflop information is problematic, need to be rectified

class prefloprangge:
    def __init__(self):
        result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPREPAIRJOINRATEDOC})
        if result.count() > 0:
            self.m_rawdata = result.next()

        self.m_handsjoinrate = []
        self.readjoinratedata()

    def readjoinratedata(self):
        f = open("data/handsrank")
        handsnum = 0
        for line in f:
            if line[0] == line[1]:
                handsnum += 6
            elif line[2] == "s":
                handsnum += 4
            else:
                handsnum += 12
            self.m_handsjoinrate.append([line.strip(), handsnum * 1.0 / 1326])

        f.close()

    def getrange(self,curturn,betlevel,ftlevelkey,stlevelkey,thlevelkey,action):
        try:
            if not action:
                return
            targetfield = Constant.getprefloprangefield(curturn,betlevel)
            targetdoc = self.m_rawdata[targetfield]

            targetdoc = targetdoc[str(ftlevelkey)]
            lowkey = handsinfocommon.getnearestlowkey(stlevelkey,targetdoc.keys())
            targetdoc = targetdoc[str(lowkey)]
            nearestkey = handsinfocommon.getnearestkey(thlevelkey,targetdoc.keys())
            targetdoc = targetdoc[str(nearestkey)]

            return targetdoc[action]
        except:
            print "getrange error."
            print "getrange parameter : ",curturn,betlevel,ftlevelkey,stlevelkey,thlevelkey,action
            return

    def gethandsinfoinrange(self, joinrate):
        handslist = []
        for hand, curjoinrate in self.m_handsjoinrate:
            handslist.append(hand)
            if curjoinrate > joinrate:
                break
        return handslist

    def gethandsinrange(self, joinrate):
        handsinfolist = self.gethandsinfoinrange(joinrate)
        handslist = []
        for handsstr in handsinfolist:
            handslist.extend(hunlgame.Cardsengine.shorthandstoallhands(handsstr))
        return handslist

# this class do not consider the real seat number
class CumuInfo:
    # def __init__(self, playerquantity, bbvalue, anti, stacksize):
    def __init__(self, handsinfo):
        self.m_handsinfo = handsinfo
        self.m_playerquantity = len(self.m_handsinfo["data"][0][2])
        self.m_bb = Constant.BB
        self.m_anti = Constant.ANTI

        self.reset()

        self.m_handsrangeobj = prefloprangge()

    # this function is called after the preflop is over
    def getpreflopinfomation(self):
        return {
            "range"     :   self.m_prefloprange,
            "raiser"    :   self.m_preflopraiser,
            "betlevel"  :   self.m_preflopbetlevel,
        }

    # this function is called after the flop is over
    def getflopinformation(self):
        return {
            "raiser"    :   self.m_flopraiser,
            "attack"    :   self.m_flopattack,
        }

    # this function is called after the turn is over
    def getturninformation(self):
        return {
            "raiser"    :   self.m_turnraiser,
            "attack"    :   self.m_turnattack,
        }

    # this function is called after the river is over
    def getriverinformation(self):
        return {
            "raiser"    :   self.m_riverraiser,
            "attack"    :   self.m_riverattack,
        }

    # this function is called after the specific round is over
    def getspecificturninformation(self, round):
        if round == 1:
            return self.getpreflopinfomation()
        elif round == 2:
            return self.getflopinformation()
        elif round == 3:
            return self.getturninformation()
        elif round == 4:
            return self.getriverinformation()

    # this function is called after the action is updated
    def getlastaction(self):
        return [self.m_lastaction,self.m_lastattack]

    # this fucntion is called after the action is updated to get the state before the last action is updated
    def getlaststate(self):
        return self.m_laststate
    #           {
    #             "pos":pos,
    #             "relativepos":relativepos,
    #             "remain":self.m_remainplayer-self.m_allinplayer,
    #             "normalneedtobet":normalneedtobet,
    #             "normalpayoff":normalpayoff,
    #             "betbb":betbb,
    #             "circle":self.m_circle
    #             }

    # the relative pos of specific pos when all-iner and folder is ignored
    def getrelativepos(self,pos):
        if pos == 0:
            return 0
        relativepos = 0
        # print pos, self.m_afterflopposlist,self.m_inpoolstate
        if self.m_inpoolstate[pos] == 2:
            # all in, no relativepos
            return 0
        for idx in self.m_afterflopposlist[::-1]:
            if idx == pos:
                return relativepos + 1
            if self.m_inpoolstate[idx] == 1:
                relativepos += 1
        return 0

    def reset(self):
        # stack of each player
        stacksize = self.m_handsinfo["data"][0][3]
        realinpoolplayer = self.m_handsinfo["data"][0][2]

        sbpos = realinpoolplayer[0]
        bbpos = realinpoolplayer[1]

        self.m_stacksize = [0] * 10
        self.m_stacksize[9] = stacksize[sbpos - 1]
        self.m_stacksize[8] = stacksize[bbpos - 1]
        for idx, realpos in enumerate(realinpoolplayer[::-1][:-2]):
            self.m_stacksize[idx + 1] = stacksize[realpos - 1]


        # pot size
        self.m_pot = self.m_bb + self.m_bb/2 + self.m_anti * self.m_playerquantity

        # raiser of the current turn
        # 0 means no raiser
        self.m_raiser = 0
        self.m_fakeraiser = 0

        # raiser of the preflop
        # 0 means no raiser
        self.m_preflopraiser = 0
        self.m_flopraiser = 0
        self.m_turnraiser = 0
        self.m_riverraiser = 0

        # how many bets, 0 means check
        self.m_betlevel = 1

        # how many bet pot, records the preflop information
        self.m_preflopbetlevel = 0
        self.m_flopattack = 0
        self.m_turnattack = 0
        self.m_riverattack = 0

        # how many stake the raiser bet
        self.m_betvalue = self.m_bb

        # how many stake does the raiser raise
        self.m_raisevalue = self.m_bb

        # the betting circle of the current turn
        self.m_circle = 1

        # bet history of the current turn
        self.m_bethistory = {Constant.BBPOS:self.m_bb, Constant.SBPOS:self.m_bb / 2}

        # real time state of every player
        # 0 means fold or not in game,
        # 1 means playing
        # 2 means all in
        self.m_inpoolstate = {}

        # action sequence of after flop
        self.m_afterflopposlist = []
        # action sequence of pre flop
        self.m_preflopposlist = []
        self.initinpoolstate()

        # the last player that have taken action
        self.m_lastplayer = 0

        # the next player to take action
        # this value doesnot necessary means anything when the game has finished
        # -1 means game over
        self.m_nextplayer = self.m_preflopposlist[0]

        # 1 means preflop
        self.m_curturn = 1

        # if current turn has finished
        self.m_curturnover = False

        # remaining player, including those all in
        self.m_remainplayer = self.m_playerquantity

        # all in player
        self.m_allinplayer = 0

        self.m_lastaction = 0
        self.m_lastattack = 0

        self.m_laststate = {}

        # 1. player's range. 2. betlevel. 3. player number and relative pos. 4. raiser. 5. pot. 6. how many player all in.
        self.m_prefloprange = [0] * 10


    def initinpoolstate(self):
        self.m_inpoolstate = [0]*10
        self.m_preflopposlist = range(self.m_playerquantity - 2,0, -1) + [9,8]
        self.m_afterflopposlist = [9,8] + range(self.m_playerquantity - 2,0, -1)
        for pos in self.m_afterflopposlist:
            self.m_inpoolstate[pos] = 1

    def newturn(self):

        # if self.m_curturn == 1:
        #     self.m_preflopraiser = self.m_raiser
        #     self.m_preflopbetlevel = self.m_betlevel

        self.m_curturn += 1
        self.m_curturnover = False
        self.m_raiser = 0
        self.m_fakeraiser = 0
        self.m_betlevel = 0
        self.m_circle = 1
        self.m_betvalue = 0
        self.m_bethistory = {}
        self.m_needtobet = 0
        self.m_lastplayer = 0

        self.m_lastattack = 0


    def getnextplayer(self):
        if self.m_curturnover:
            if self.m_curturn + 1 > 1:
                poslist = self.m_afterflopposlist
            else:
                poslist = self.m_preflopposlist
            for pos in poslist:
                if self.m_inpoolstate[pos] == 1:
                    return pos
                if self.m_raiser == pos:
                    return pos
            else:
                # every one all in or fold
                return -1
        else:
            lastplayerindex = self.m_afterflopposlist.index(self.m_lastplayer)
            # print "---",self.m_fakeraiser,self.m_raiser
            # print self.m_inpoolstate
            for pos in self.m_afterflopposlist[lastplayerindex + 1:] + self.m_afterflopposlist[:lastplayerindex + 1]:
                if self.m_inpoolstate[pos] == 1:
                    return pos
                if self.m_fakeraiser:
                    if self.m_fakeraiser == pos:
                        return pos
                elif self.m_raiser == pos:
                    return pos
            else:
                # every one all in or fold
                return -1

    # the last player to action in the current turn and the current round
    def getlastactioner(self):
        if self.m_curturn == 1:
            poslist = self.m_preflopposlist
        else:
            poslist = self.m_afterflopposlist
        for pos in poslist[::-1]:
            if self.m_inpoolstate[pos] == 1:
                return pos

    def updatecurturnstate(self):
        if self.m_raiser == 0:
            # no raiser
            if self.getlastactioner() == self.m_lastplayer:
                self.m_curturnover = True
            else:
                self.m_curturnover = False
        elif self.m_fakeraiser == 0:
            # has raiser and no invalid raise
            if self.getnextplayer() == self.m_raiser:
                self.m_curturnover = True
            else:
                self.m_curturnover = False
        else:
            # has invalid raise
            if self.getnextplayer() == self.m_fakeraiser:
                self.m_curturnover = True
            else:
                self.m_curturnover = False
    def isgameover(self):
        if self.m_curturnover == False:
            return False

        remain = self.m_remainplayer - self.m_allinplayer
        if remain > 1:
            return False
        elif remain == 1:
            return True
        elif remain == 0:
            return True
        else:
            print "remain small than 0"
            raise

    def update(self,action,value):
        if self.isgameover():
            print "game has over"
            raise
        if self.m_curturnover:
            self.newturn()
        self.m_laststate = self.calstatistics()
        self.updatestate(action,value)
        self.m_lastplayer = self.m_nextplayer
        self.updatecurturnstate()
        self.m_nextplayer = self.getnextplayer()
        self.updatecircle()
        self.updateprefloprange()
        self.updateflopinformation()
        self.updateturninformation()
        self.updateriverinformation()
        # print "===========]"
        # print action,value
        # print self.m_inpoolstate
        # if not self.isgameover() and self.m_curturnover:
        #     self.newturn()

    def updatecircle(self):
        if self.m_lastplayer == 0:
            self.m_circle = 1
            return
        if self.m_curturn == 1:
            poslist = self.m_preflopposlist
        else:
            poslist = self.m_afterflopposlist
        lastidx = poslist.index(self.m_lastplayer)
        nextidx = poslist.index(self.m_nextplayer)
        if lastidx > nextidx:
            self.m_circle += 1

    # 0 means raiser is totally invalid, since all other has all in
    def calvalidraisevalue(self, pos, value):
        validraisevalue = 0
        for idx in self.m_afterflopposlist:
            if idx == pos:
                continue
            if self.m_inpoolstate[idx] == 1:
                targetstack = self.m_bethistory.get(idx,0) + self.m_stacksize[idx]
                if targetstack >= value:
                    validraisevalue = value
                    break
                else:
                    if targetstack > validraisevalue:
                        validraisevalue = targetstack
        return validraisevalue

    def updatestate(self,action,value):
        pos = self.m_nextplayer

        if action == 2:
            value = self.calvalidraisevalue(pos, value)
            if value <= self.m_betvalue:
                # all other has all in, invalid raiser
                action = 3
        elif action == 4 and value > self.m_betvalue:
            value = self.calvalidraisevalue(pos, value)
            if value <= self.m_betvalue:
                # all other has all in, invalid raiser
                action = 3

        if value > self.m_betvalue:
            givepayoff = (value + self.m_pot - self.m_bethistory.get(pos,0)) * 1.0 / ( value - self.m_betvalue)
            givepayoff = handsinfocommon.roundhalf(givepayoff)
            self.m_lastattack = self.m_betlevel + 1 + givepayoff * 0.001
        else:
            self.m_lastattack = 0

        if action == 1 or action == -1:
            # curstate["fold"] += 1
            self.m_inpoolstate[pos] = 0
            self.m_remainplayer -= 1
            self.m_lastaction = 1

        elif action == 2:
            self.m_lastaction = 2
            # curstate["raise"] += 1
            self.m_betlevel += 1
            self.m_raisevalue = value - self.m_betvalue
            if (self.m_betvalue >= value):
                print "betvalue >= value"
                raise
            self.m_betvalue = value
            self.m_pot += value -self.m_bethistory.get(pos,0)
            self.m_stacksize[pos] -= value -self.m_bethistory.get(pos,0)
            self.m_raiser = pos
            self.m_fakeraiser = 0

            self.m_bethistory[pos] = value

        elif action == 3 or action == 6:
            self.m_lastaction = action
            # curstate["call"] += 1
            self.m_pot += self.m_betvalue-self.m_bethistory.get(pos,0)
            self.m_stacksize[pos] -= self.m_betvalue-self.m_bethistory.get(pos,0)
            self.m_bethistory[pos] = self.m_betvalue

        elif action == 4:
            self.m_allinplayer += 1
            if value <= self.m_betvalue:
                # curstate["call"] += 1
                self.m_lastaction = 4.3

            else:
                if value - self.m_betvalue < self.m_raisevalue:
                    # invalid raise
                    self.m_fakeraiser = pos
                    # self.m_betvalue = value
                else:
                    # valid raise
                    self.m_raiser = pos
                    self.m_fakeraiser = 0
                    self.m_raisevalue = value - self.m_betvalue

                givepayoff = (value + self.m_pot - self.m_bethistory.get(pos,0)) * 1.0 / ( value - self.m_betvalue)
                givepayoff = handsinfocommon.roundhalf(givepayoff)
                if givepayoff <= 4:
                    # curstate["raise"] += 1
                    self.m_lastaction = 4.2
                    self.m_betlevel += 1
                else:
                    self.m_lastaction = 4.3
                    # curstate["call"] += 1
                self.m_betvalue = value
            self.m_pot += value-self.m_bethistory.get(pos,0)
            self.m_stacksize[pos] -= value-self.m_bethistory.get(pos,0)
            self.m_bethistory[pos] = value
            self.m_inpoolstate[pos] = 2
        elif action == 12:
            self.m_lastaction = 12
            for idx in xrange(len(self.m_inpoolstate)):
                if idx != pos:
                    self.m_inpoolstate[idx] = 0
            self.m_remainplayer = 1
            self.m_allinplayer = 0
            self.m_curturnover = True

    # this function is called before the action is updated
    def calstatistics(self):
        bb = self.m_bb
        pos = self.m_nextplayer

        # needtobet, payoffrate, pos, relativepos,
        if self.m_bethistory.get(self.m_nextplayer,0) + self.m_stacksize[self.m_nextplayer] < self.m_betvalue:
            # need to call all in
            needtobet = self.m_stacksize[self.m_nextplayer]
            curturnstack = needtobet + self.m_bethistory.get(pos,0)
            if needtobet < bb:
                needtobet = bb

            if needtobet != 0:
                # seppot = self.m_anti * self.m_playerquantitiy + bb + bb / 2
                seppot = self.m_pot
                for hispos,hisbetvalue in self.m_bethistory.items():
                    if hisbetvalue > curturnstack:
                        seppot -= hisbetvalue - curturnstack

                payoffrate = seppot * 1.0 / needtobet
            else:
                payoffrate = 10000

            # since call all in, betbb depends on his remaining stack, NOT the real betbb
            if curturnstack < bb:
                betbb = int((bb + 0.5 * bb) / bb)
            else:
                betbb = int((curturnstack + 0.5 * bb) / bb)

        else:
            needtobet = self.m_betvalue - self.m_bethistory.get(pos,0)
            if needtobet != 0:
                payoffrate = self.m_pot * 1.0 / needtobet
            else:
                payoffrate = 10000

            betbb = int((self.m_betvalue + 0.5 * bb) / bb)

        normalpayoff = int(round(payoffrate * 2)) * 5
        normalneedtobet = int( (needtobet + 0.5 * bb) / bb )

        if self.m_curturn == 1:
            if pos > self.m_raiser:
                relativepos = 0
            else:
                relativepos = 1
        else:
            if pos > self.m_raiser:
                relativepos = 0
            elif pos < self.m_raiser:
                relativepos = 1
            else:
                # raiser
                relativepos = 2

        realpos = 0
        for idx in self.m_inpoolstate:
            if self.m_inpoolstate[idx] == 1:
                realpos += 1
            if idx == pos:
                break

        return {
                "pos":pos,
                "pot":self.m_pot,
                "relativepos":relativepos,
                "remain":self.m_remainplayer-self.m_allinplayer,
                "allin":self.m_allinplayer,
                "normalneedtobet":normalneedtobet,
                "normalpayoff":normalpayoff,
                "betbb":betbb,
                "circle":self.m_circle,
                "betlevel":self.m_betlevel,
                "round":self.m_curturn,
                "raiser":self.m_raiser,
                }

    # update preflop state
    # preflop state include :
    # 1. player's range. 2. betlevel. 3. player number and relative pos. 4. raiser. 5. pot. 6. how many player all in.
    def updateprefloprange(self):
        if self.m_laststate["round"] != 1:
            return
        if self.m_laststate["circle"] == 1 and self.m_laststate["betlevel"] < 3:
            newrange = self.m_handsrangeobj.getrange(self.m_laststate["circle"],self.m_laststate["betlevel"],
                                          self.m_laststate["pos"],self.m_laststate["betbb"],self.m_laststate["normalpayoff"],
                                          self.actiontransfer(self.m_lastaction) )
        else: # > 1
            newrange = self.m_handsrangeobj.getrange(self.m_laststate["circle"],self.m_laststate["betlevel"],
                                          self.m_laststate["relativepos"],self.m_laststate["normalneedtobet"],self.m_laststate["normalpayoff"],
                                          self.actiontransfer(self.m_lastaction) )

        if newrange:
            if not self.m_prefloprange[self.m_laststate["pos"]]:
                self.m_prefloprange[self.m_laststate["pos"]] = 1
            self.m_prefloprange[self.m_laststate["pos"]] *= newrange

        self.m_preflopraiser = self.m_raiser
        self.m_preflopbetlevel = self.m_betlevel

    def updateflopinformation(self):
        if self.m_laststate["round"] != 2:
            return
        self.m_flopraiser = self.getrelativepos(self.m_raiser)
        if self.m_lastattack > self.m_flopattack:
            self.m_flopattack = self.m_lastattack

    def updateturninformation(self):
        if self.m_laststate["round"] != 3:
            return
        self.m_turnraiser = self.getrelativepos(self.m_raiser)
        if self.m_lastattack > self.m_turnattack:
            self.m_turnattack = self.m_lastattack

    def updateriverinformation(self):
        if self.m_laststate["round"] != 4:
            return
        self.m_riverraiser = self.getrelativepos(self.m_raiser)
        if self.m_lastattack > self.m_riverattack:
            self.m_riverattack = self.m_lastattack

    # self.m_preflopstate = {
    #         "range" :   [-1]*10,
    #         "betlevel"  :   1,
    #         "playernum"    :   self.m_playerquantity,
    #         "relativepos"   :   2,  # 2 means no raiser,
    #         "raiser"    :   0,
    #         "pot"   :   self.m_pot,
    #         "allin"    :   0,
    #     }

    def actiontransfer(self,action):
        if action == 1:
            return "fold"
        elif action == 12:
            return
        elif action in [2,4.2]:
            return "raise"
        elif action in [3,6,4.3]:
            return "call"



















class HandsInfo:
    def __init__(self, handsinfo):
        self.m_handsinfo = handsinfo
        self.m_playerquantitiy = len(self.m_handsinfo["data"][0][2])

        # -3 means fail to record showcard
        # -1 or -2 means record error, this hands is not usefull
        # 0 means game over in advance
        # 1 means game over with showcard
        self.m_showcard = self.m_handsinfo["showcard"]

        self.reset()

    def reset(self):
        self.m_cumuinfo = CumuInfo(self.m_handsinfo)

        self.m_lastupdateturn = 1
        self.m_lastupdateidx = -1

    def getplayerquantity(self):
        return self.m_playerquantitiy

    def isvalid(self):
        if not (self.m_showcard >= 0 or self.m_showcard == -3):
            return False
        return True

    # return how far does this game go for
    # 1 - 4 means preflop to river
    def getturncount(self):
        handsdata = self.m_handsinfo["data"]
        infolen = len(handsdata)
        if infolen < 6:
            # over before river
            return infolen - 2
        elif infolen == 7:
            # play to river or all in at turn
            if handsdata[4]==None:
                # all in at turn
                return 3
            else:
                # play to river
                return 4
        else:
            # infolen == 6
            # may be play to river and not show card
            # may be all in before river
            if not isinstance(handsdata[5][0][0],list):
                # play to river and not show card
                return 4

            for idx in xrange(4,0,-1):
                # all in before river
                if handsdata[idx]!= None:
                    return idx - 1

    def getspecificturnbetdata(self,turn):
        return self.m_handsinfo["data"][turn]

    def getpreflopbetdata(self):
        return self.m_handsinfo["data"][1]

    def getflopbetdata(self):
        return self.m_handsinfo["data"][2]

    def getturnbetdata(self):
        return self.m_handsinfo["data"][3]

    def getriverbetdata(self):
        return self.m_handsinfo["data"][4]

    def getrounddata(self, round):
        return self.m_handsinfo["data"][round]

    def getboard(self):
        handsdata = self.m_handsinfo["data"]
        infolen = len(handsdata)
        if infolen < 6:
            # over before river
            return handsdata[-1]
        elif infolen == 7:
            # play to river or all in at turn
            return handsdata[-1]

        else:
            # infolen == 6
            # may be play to river and not show card
            # may be all in before river
            if not isinstance(handsdata[5][0][0],list):
                # play to river and not show card
                return handsdata[-1]

            for idx in xrange(4,0,-1):
                # all in before river
                if handsdata[idx]!= None:
                    return handsdata[idx]

    def getprivatecard(self):
        if self.m_showcard > 0 or self.m_showcard == -3:
            return self.m_handsinfo["data"][5]
        else:
            return None

    def getpreflopinformation(self):
        self.traversepreflop()
        return self.m_cumuinfo.getpreflopinfomation()

    # traverse preflop data if preflop data has not been traversed
    def traversepreflop(self):
        self.traversespecificturn(1)

    # traverse over specific turn's data.
    # This function make sure that after this function is called,
    # the action update procedure stops right at the end of this turn.
    def traversespecificturn(self,turn):
        # raw_input()
        # print self.m_lastupdateturn,turn
        # print self.m_lastupdateidx
        if self.m_lastupdateturn == turn:
            preflopdata = self.getspecificturnbetdata(turn)
            if self.m_lastupdateidx + 1 == len(preflopdata):
                # now is at the end of preflop
                return
            for idx in xrange(self.m_lastupdateidx + 1, len(preflopdata)):
                # self.m_cumuinfo.update(*preflopdata[idx])
                self.updatecumuinfo(turn, idx)
        elif self.m_lastupdateturn > turn:
            # now is after the turn
            self.reset()
            self.traversespecificturn(turn)
            return
        elif self.m_lastupdateturn == turn - 1 and self.m_lastupdateidx + 1 == len(self.getspecificturnbetdata(turn - 1)):
            specificturndata = self.getspecificturnbetdata(turn)
            for idx in xrange(len(specificturndata)):
                self.updatecumuinfo(turn,idx)
        elif self.m_lastupdateturn < turn:
            for idx in xrange(self.m_lastupdateturn,turn + 1):
                self.traversespecificturn(idx)
            return

    # def traversespecificturn(self,turn):
    #     if self.m_lastupdateturn == turn:
    #         preflopdata = self.getspecificturnbetdata(turn)
    #         for idx in xrange(self.m_lastupdateidx + 1, len(preflopdata)):
    #             # self.m_cumuinfo.update(*preflopdata[idx])
    #             self.updatecumuinfo(turn, idx)
    #     elif self.m_lastupdateturn == turn - 1 and self.m_lastupdateidx + 1 == len(self.getspecificturnbetdata(turn - 1)):
    #         pass

    # actionidx starts from 0
    def updatecumuinfo(self,round,actionidx):
        self.m_cumuinfo.update(*self.getspecificturnbetdata(round)[actionidx])
        self.m_lastupdateturn = round
        self.m_lastupdateidx = actionidx
        # handsinfocommon.pp.pprint(self.m_cumuinfo.getlaststate())

    # round starts from 0, which means preflop
    # actionidx starts from 0, which means the first action
    def getcumuinfo(self):
        return self.m_cumuinfo


def testgetprefloprange():
    rangeobj = prefloprangge()
    print rangeobj.getrange(1,2,9,1,65,"call")
    print rangeobj.getrange(1,2,9,1,65,"raise")
    print rangeobj.getrange(1,2,9,1,145,"call")

    print rangeobj.gethandsinfoinrange(0.1)
    for hand in rangeobj.gethandsinrange(0.01):
        print hand

    joinrate = rangeobj.getrange(1,1,3,1,30,"raise")
    print "joinrate:    ",joinrate
    print rangeobj.gethandsinfoinrange(joinrate)

    joinrate = rangeobj.getrange(1,1,3,1,30,"call")
    print rangeobj.gethandsinfoinrange(joinrate)
    print "joinrate:    ",joinrate

if __name__ == "__main__":
    testgetprefloprange()