import Constant
import handsinfocommon
import copy
import DBOperater
import hunlgame
import handsinfoexception

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

    # joinrate of specific state
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

            # print "getrange : ",curturn,betlevel,ftlevelkey,stlevelkey,thlevelkey,action
            # print "result : ",targetdoc[action],targetfield,lowkey,nearestkey
            return targetdoc[action]
        except:
            print "getrange error."
            print "getrange parameter : ",curturn,betlevel,ftlevelkey,stlevelkey,thlevelkey,action
            return

    # short representation of hands in range
    def gethandsinfoinrange(self, joinrate):
        handslist = []
        if joinrate == 0:
            return handslist
        for hand, curjoinrate in self.m_handsjoinrate:
            handslist.append(hand)
            if curjoinrate >= joinrate:
                break
        return handslist

    # full representation of hands in range
    def gethandsinrange(self, joinrate):
        handsinfolist = self.gethandsinfoinrange(joinrate)
        handslist = []
        for handsstr in handsinfolist:
            handslist.extend(hunlgame.Cardsengine.shorthandstoallhands(handsstr))
        return handslist

    def gethandsjoinrate(self, hand):
        targethandstr = hand.shortstr()
        for handstr, joinrate in self.m_handsjoinrate:
            if targethandstr == handstr:
                return joinrate
        print "targethand : ",targethandstr
        raise



class ReplayEngine:
    def __init__(self, handsinfo):
        self.m_handsinfo = HandsInfo(handsinfo)

        self.m_playerquantity = self.m_handsinfo.getplayerquantity()
        self.m_bb = self.m_handsinfo.getbb()
        self.m_anti = self.m_handsinfo.getante()

        self.reset()

        self.m_handsrangeobj = prefloprangge()

    # this function is called after the preflop is over
    def getpreflopinfomation(self):
        return {
            "range"     :   self.m_prefloprange,
            "raiser"    :   self.m_preflopraiser,
            "betlevel"  :   self.m_preflopbetlevel,
            "remain"    :   self.m_preflopremain,
            "allin"     :   self.m_preflopallin,
            "newattack" :   self.m_preflopattack,
        }

    # this function is called after the flop is over
    def getflopinformation(self):
        return {
            "raiser"    :   self.m_flopraiser,
            "attack"    :   self.m_flopattack,
            "remain"    :   self.m_flopremain,
            "allin"     :   self.m_flopallin,
            "newattack" :   self.m_flopattack,
        }

    # this function is called after the turn is over
    def getturninformation(self):
        return {
            "raiser"    :   self.m_turnraiser,
            "attack"    :   self.m_turnattack,
            "remain"    :   self.m_turnremain,
            "allin"     :   self.m_turnallin,
            "newattack" :   self.m_turnattack,
        }

    # this function is called after the river is over
    def getriverinformation(self):
        return {
            "raiser"    :   self.m_riverraiser,
            "attack"    :   self.m_riverattack,
            "remain"    :   self.m_riverremain,
            "allin"     :   self.m_riverallin,
            "newattack" :   self.m_riverattack,
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

    def reset(self):
        self.m_initstack = copy.deepcopy(self.m_handsinfo.getStack())
        # this stack size has subtracted anti and blind
        self.m_stacksize = copy.deepcopy( self.m_handsinfo.getStack())
        for idx in xrange(len(self.m_stacksize)):
            if self.m_stacksize[idx] > 0:
                self.m_stacksize[idx] -= self.m_anti
        self.m_stacksize[8] -= self.m_bb
        self.m_stacksize[9] -= self.m_bb / 2
        # print "stack:",self.m_stacksize

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

        # invest history
        self.m_invest = [0] * 10

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
        # self.initinvest()

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

        self.m_lastupdateturn = 1
        self.m_lastupdateidx = -1

        # 1. player's range. 2. betlevel. 3. player number and relative pos. 4. raiser. 5. pot. 6. how many player all in.
        self.m_prefloprange = [0] * 10

        self.m_attack = 0
        self.m_totalattack = 0

    def initinpoolstate(self):
        self.m_inpoolstate = [0]*10
        self.m_preflopposlist = range(self.m_playerquantity - 2,0, -1) + [9,8]
        self.m_afterflopposlist = [9,8] + range(self.m_playerquantity - 2,0, -1)
        for pos in self.m_afterflopposlist:
            self.m_inpoolstate[pos] = 1

    def initinvest(self):
        for pos, state in enumerate(self.m_inpoolstate):
            if state == 1:
                self.m_invest[pos] += self.m_anti
        self.m_invest[9] += self.m_bb / 2
        self.m_invest[8] += self.m_bb

    def newturn(self):
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
        self.m_attack = 0

    def getnextplayer(self):
        if self.m_curturnover:
            if self.m_curturn + 1 > 1:
                poslist = self.m_afterflopposlist
            else:
                poslist = self.m_preflopposlist
            for pos in poslist:
                if self.m_inpoolstate[pos] == 1:
                    return pos
                    # if self.m_raiser == pos:
                    #     return pos
            else:
                # every one all in or fold
                return -1
        else:
            lastplayerindex = self.m_afterflopposlist.index(self.m_lastplayer)
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

    # 1 means good position, 0 means bad position
    def getrelativepostoopener(self,pos):
        if self.getpreflopinfomation()["raiser"] > pos:
            return 1
        else:
            return 0

    def islastactioner(self, lastplayer):
        if self.m_curturn == 1:
            poslist = self.m_preflopposlist
        else:
            poslist = self.m_afterflopposlist
        for pos in poslist[::-1]:
            if pos == lastplayer:
                return True
            if self.m_inpoolstate[pos] == 1:
                return False

    def updatecurturnstate(self):
        # print self.m_handsinfo["_id"]
        # print "raiser info : ",self.getnextplayer(),self.m_fakeraiser,self.m_raiser
        # print "stateinfo:",self.m_remainplayer, self.m_allinplayer,self.m_raiser,self.m_fakeraiser,self.getnextplayer()

        if self.m_remainplayer == 1:
            self.m_curturnover = True
            return

        if self.m_remainplayer - self.m_allinplayer == 0:
            self.m_curturnover = True
            return

        if self.m_remainplayer - self.m_allinplayer == 1 and self.m_inpoolstate[self.m_lastplayer] == 1:
            # the only one that remains is the last actioner, which means the turn over
            self.m_curturnover = True
            return
        # print "sss:",self.getlastactioner(),self.m_lastplayer,self.m_raiser,self.m_fakeraiser
        if self.m_raiser == 0 and self.m_fakeraiser == 0:
            # no raiser
            if self.islastactioner(self.m_lastplayer):
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
                # print "nextplayer : ",self.getnextplayer(),self.m_fakeraiser
                self.m_curturnover = True
            else:
                self.m_curturnover = False

    def isgameover(self):
        if self.m_curturnover == False:
            return False
        if self.m_curturnover == True and self.m_curturn == 4:
            return True

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

    def getposlist(self):
        if self.m_curturn == 1 and not self.m_curturnover:
            return self.m_preflopposlist
        return self.m_afterflopposlist

    def update(self,actionpos,action,value):
        if self.isgameover():
            print "game has over"
            raise handsinfoexception.ExtraAction()
        self.m_laststate = self.calstatistics()
        self.updatestate(actionpos,action,value)
        if actionpos != self.m_nextplayer:
            return
        self.m_lastplayer = self.m_nextplayer
        self.updatecurturnstate()
        self.m_nextplayer = self.getnextplayer()
        # print "player: ",self.m_lastplayer,self.m_nextplayer, action, value
        self.updatecircle()
        self.updateprefloprange()
        self.updateflopinformation()
        self.updateturninformation()
        self.updateriverinformation()
        if self.m_curturnover:
            self.newturn()

    def updatecircle(self):
        if self.m_nextplayer == -1:
            return

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
                # print "targetstack:",idx,targetstack
                if targetstack >= value:
                    validraisevalue = value
                    break
                else:
                    if targetstack > validraisevalue:
                        validraisevalue = targetstack
        return validraisevalue

    def updatestate(self,actionpos,action,value):
        # print "action:",action,value
        pos = self.m_nextplayer
        if pos != actionpos:
            self.m_inpoolstate[actionpos] = 0
            self.m_remainplayer -= 1
            return
        self.m_stacksize[pos] -= value
        value += self.m_bethistory.get(pos,0)
        realvalue = value

        if self.m_stacksize[pos] == 0:
            action = 4
        elif action == "fold":
            action = 1
        elif action == "check":
            action = 3
        elif action == "call":
            action = 6
        elif action == "raise":
            action = 2

        if action == 2:
            value = self.calvalidraisevalue(pos, value)
            if value <= self.m_betvalue:
                # all other has all in, invalid raiser
                action = 6
        elif action == 4 and value > self.m_betvalue:
            value = self.calvalidraisevalue(pos, value)
            # print "all in:",value, self.m_betvalue
            if value <= self.m_betvalue:
                # all other has all in, invalid raiser
                action = 6

        if value > self.m_betvalue:
            givepayoff = (value + self.m_pot - self.m_bethistory.get(pos,0)) * 1.0 / ( value - self.m_betvalue)
            givepayoff = handsinfocommon.roundhalf(givepayoff)
            self.m_lastattack = self.m_betlevel + 1 + givepayoff * 0.001
        else:
            self.m_lastattack = 0

        attackvalue = value - self.m_betvalue
        realpot = self.m_pot + self.m_betvalue - self.m_bethistory[pos]
        attackrate = attackvalue * 1.0 / realpot
        self.m_attack += attackrate
        self.m_totalattack += attackrate

        # print "action:",action,value
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
                raise handsinfoexception.RaiseValueDecrease()
            self.m_betvalue = value
            self.m_pot += value -self.m_bethistory.get(pos,0)
            self.m_raiser = pos
            self.m_fakeraiser = 0

            self.m_bethistory[pos] = value

        elif action == 3:
            self.m_lastaction = action
            if self.m_bethistory.get(pos,0) != self.m_betvalue:
                print "check when raise made : ",self.m_bethistory.get(pos,0),self.m_betvalue, action, realvalue
                raise handsinfoexception.CheckWhenRaiseMade()

        elif action == 6:
            self.m_lastaction = action
            # curstate["call"] += 1
            self.m_pot += self.m_betvalue-self.m_bethistory.get(pos,0)
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
            self.m_bethistory[pos] = realvalue
            self.m_inpoolstate[pos] = 2

        # elif action == 12:
        #     self.m_lastaction = 12
        #     for idx in xrange(len(self.m_inpoolstate)):
        #         if idx != pos:
        #             self.m_inpoolstate[idx] = 0
        #     self.m_remainplayer = 1
        #     self.m_allinplayer = 0
        #     self.m_curturnover = True

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
        self.m_preflopremain = self.m_remainplayer - self.m_allinplayer
        self.m_preflopallin = self.m_allinplayer
        self.m_preflopattack = self.m_attack

    def updateflopinformation(self):
        if self.m_laststate["round"] != 2:
            return
        self.m_flopraiser = self.m_raiser
        if self.m_lastattack > self.m_flopattack:
            self.m_flopattack = self.m_lastattack
        self.m_flopremain = self.m_remainplayer - self.m_allinplayer
        self.m_flopallin = self.m_allinplayer
        self.m_newflopattack = self.m_attack

    def updateturninformation(self):
        if self.m_laststate["round"] != 3:
            return
        self.m_turnraiser = self.m_raiser
        if self.m_lastattack > self.m_turnattack:
            self.m_turnattack = self.m_lastattack
        self.m_turnremain = self.m_remainplayer - self.m_allinplayer
        self.m_turnallin = self.m_allinplayer
        self.m_newturnattack = self.m_attack

    def updateriverinformation(self):
        if self.m_laststate["round"] != 4:
            return
        self.m_riverraiser = self.m_raiser
        if self.m_lastattack > self.m_riverattack:
            self.m_riverattack = self.m_lastattack
        self.m_riverremain = self.m_remainplayer - self.m_allinplayer
        self.m_riverallin = self.m_allinplayer
        self.m_newriverattack = self.m_attack

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

    # these function is used to calculate payoff and most of the function is
    # copied from tongjihandsinfo.py
    def calinvest(self):
        invest = [0] * 10
        for idx in xrange(10):
            invest[idx] = self.m_initstack[idx] - self.m_stacksize[idx]
        return invest

    def extractprivatecard(self,competitor, privatecard):
        newprivatecard = []
        for pos in competitor:
            newprivatecard.append(privatecard[pos])
        return newprivatecard

    def seppot(self,gameinvest,inpoolstate):
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

    def calpayoff_(self):
        if self.m_handsinfo.getshowcardquantity() > 0:
            showcard = 1
        else:
            showcard = 0
        inpoolstate = [0] * 10
        for pos,state in enumerate(self.m_inpoolstate):
            inpoolstate[pos] = state

        gameinvest = self.calinvest()
        # gameinvest = gameinvest[:self.m_playerquantity - 1] + gameinvest[8:10] + [0] * (9 - self.m_playerquantity)
        newgameinvest = [0] * 10
        for pos,vest in enumerate(gameinvest):
            newgameinvest[pos] = vest
        gameinvest = newgameinvest
        # print "gameinvest:",gameinvest
        seppotresult = self.seppot(gameinvest,inpoolstate)

        if showcard != 1:
            # donot showcard
            payofflist = [0]* 10
            for idx, value in enumerate(gameinvest):
                if inpoolstate[idx] == 0:
                    # fold
                    payofflist[idx] = - value
                else:
                    payofflist[idx] = sum(gameinvest) - value
            # self.m_payofflist = payofflist
            return [payofflist,1]
            # return [payofflist,1]

        # show card, compare card strength
        # inpoolnum = 0
        # for value in inpoolstate:
        #     if value != 0:
        #         inpoolnum += 1

        board = self.m_handsinfo.getboardcard()
        privatecard = self.m_handsinfo.getprivatehands()

        # start to compare card
        payofflist = [0]*10
        for idx,value in enumerate(gameinvest):
            payofflist[idx] = - value

        maxwinner = 0
        # print "seppot:",seppotresult
        for potinfo in seppotresult:
            competitor = potinfo[0]
            potsize = potinfo[1]
            newprivatecard = self.extractprivatecard(competitor,privatecard)
            winner = hunlgame.getwinner(board,newprivatecard)
            print "winner:",winner
            for idx in xrange(len(winner)):
                winner[idx] = competitor[winner[idx]]

            for pos in winner:
                payofflist[pos] += (potsize / len(winner))
            if len(winner) > maxwinner:
                maxwinner = len(winner)

        return [payofflist,maxwinner]

    def calpayoff(self):
        payofflist,winnerlen = self.calpayoff_()
        # print "llist:",payofflist
        # self.m_payofflist = payofflist[:self.m_playerquantity - 1] + [0] * (9 - self.m_playerquantity) + payofflist[self.m_playerquantity-1:self.m_playerquantity+1]
        self.m_payofflist = [0] * 10
        for realpos, payoff in enumerate(payofflist):
            # print "realpos:",realpos,self.m_reverseposmap.get(realpos,0), payoff
            self.m_payofflist[realpos] = payoff
        return winnerlen

    def getcurboard(self):
        realturn = self.m_curturn
        if self.m_curturnover:
            realturn += 1
        if realturn == 1:
            return []
        return self.m_handsinfo.getboardcard()[:realturn + 1]



    # traverse preflop data if preflop data has not been traversed
    def traversepreflop(self):
        self.traversespecificturn(1)

    # traverse over specific turn's data.
    # This function make sure that after this function is called,
    # the action update procedure stops right at the end of this turn.
    def traversespecificturn(self,turn):
        if self.m_lastupdateturn == turn:
            preflopdata = self.m_handsinfo.getspecificturnbetdata(turn)
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
        elif self.m_lastupdateturn == turn - 1 and self.m_lastupdateidx + 1 == len(self.m_handsinfo.getspecificturnbetdata(turn - 1)):
            specificturndata = self.m_handsinfo.getspecificturnbetdata(turn)
            for idx in xrange(len(specificturndata)):
                self.updatecumuinfo(turn,idx)
        elif self.m_lastupdateturn < turn:
            for idx in xrange(self.m_lastupdateturn,turn + 1):
                self.traversespecificturn(idx)
            return

    def traversealldata(self):
        turncount = self.m_handsinfo.getturncount()
        self.traversespecificturn(turncount)

    def islastaction(self,round,actionidx):
        turncount = self.m_handsinfo.getturncount()
        if turncount != round:
            return False
        if len(self.m_handsinfo.getspecificturnbetdata(turncount)) != actionidx + 1:
            return False
        return True

    def executenextaction(self):
        lastturndata = self.m_handsinfo.getspecificturnbetdata(self.m_lastupdateturn)
        if len(lastturndata) == self.m_lastupdateidx + 1:
            # last turn is over
            self.updatecumuinfo(self.m_lastupdateturn+1,0)
        else:
            self.updatecumuinfo(self.m_lastupdateturn,self.m_lastupdateidx+1)

    # actionidx starts from 0
    def updatecumuinfo(self,round,actionidx):
        self.update(*self.m_handsinfo.getspecificturnbetdata(round)[actionidx])
        self.m_lastupdateturn = round
        self.m_lastupdateidx = actionidx


class HandsInfo:
    TURNSTR = ["PREFLOP","FLOP","TURN","RIVER"]
    def __init__(self, handsinfo):
        self.m_handsinfo = handsinfo
        self.m_playerquantitiy = self.m_handsinfo["data"]["PLAYQUANTITY"]

        self.initprivatehand()
        self.initboard()

    def getid(self):
        return self.m_handsinfo["_id"]

    def initprivatehand(self):
        privateinfo = self.m_handsinfo["data"]["PVCARD"]
        self.m_privatehands = []
        for handstr in privateinfo:
            if handstr is not None:
                self.m_privatehands.append(hunlgame.generateHands(handstr))
            else:
                self.m_privatehands.append(None)

    def initboard(self):
        boardstr = self.m_handsinfo["data"]["BOARD"]
        self.m_board = hunlgame.generateCards(boardstr)

    def getboardcard(self):
        return self.m_board

    def getplayerquantity(self):
        return self.m_playerquantitiy

    def getbb(self):
        return self.m_handsinfo["data"]["BB"]

    def getante(self):
        return self.m_handsinfo["data"]["ante"]

    # return how far does this game go for
    # 1 - 4 means preflop to river
    def getturncount(self):
        betdata = self.m_handsinfo["data"]["BETDATA"]
        turnidx = 0
        for turnstr in self.TURNSTR:
            if turnstr in betdata:
                turnidx += 1
            else:
                break
        return turnidx

    def getaction(self,turn, actionidx):
        return self.getspecificturnbetdata(turn)[actionidx]

    def getspecificturnbetdata(self,turn):
        turnstr = self.TURNSTR[turn-1]
        return self.m_handsinfo["data"]["BETDATA"][turnstr]

    def getpreflopbetdata(self):
        return self.getspecificturnbetdata(1)

    def getflopbetdata(self):
        return self.getspecificturnbetdata(2)

    def getturnbetdata(self):
        return self.getspecificturnbetdata(3)

    def getriverbetdata(self):
        return self.getspecificturnbetdata(4)

    def getturnboard(self,turnidx):
        if turnidx == 1:
            return []
        else:
            return self.m_board[:turnidx + 1]

    # the quantity of player that show down
    def getshowcardquantity(self):
        cnt = 0
        for v in self.getprivatehands():
            if v is not None:
                cnt += 1
        return cnt

    def getprivatehands(self):
        return self.m_privatehands

    def gethand(self, pos):
        return self.m_privatehands[pos]

    def getStack(self):
        return self.m_handsinfo["data"]["STACK"]

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

    print rangeobj.getrange(1, 2, 8, 2, 45, "raise")

if __name__ == "__main__":
    testgetprefloprange()
