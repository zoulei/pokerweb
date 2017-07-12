
class CumuInfo:
    def __init__(self, inpool):
        self.reset()

    def reset(self):
        self.m_pot = 0

        # 0 means no raiser
        self.m_raiser = 0

        # starts from 1, which means the first turn
        self.m_turn = 0

        # how many bets, 0 means check
        self.m_betlevel = 0

        self.m_betvalue = 0
        # how many bet pot, records the preflop information
        self.m_preflopbetlevel = 0

        self.m_bethistory = {}

        self.m_inpoolstate = {}

        # the last player that have taken action
        self.m_lastplayer = 0

        # the next player to make action
        self.m_nextplayer = 0

    def initinpoolstate(self,inpool):
        self.m_inpoolstate = [0]*10
        for pos in inpool:
            self.m_inpoolstate[pos] = 1

    def update(self,action,value):
        pass

class HandsInfo:
    def __init__(self, handsinfo):
        self.m_handsinfo = handsinfo
        self.m_playerquantitiy = 0
        self.m_showcard = 0

        self.m_cumuinfo = CumuInfo()
        self.init()

    def init(self):
        self.m_playerquantitiy = len(self.m_handsinfo["data"][0][2])


        # -3 means fail to record showcard
        # -1 or -2 means record error, this hands is not usefull
        # 0 means game over in advance
        # 1 means game over with showcard
        self.m_showcard = self.m_handsinfo["showcard"]

    def getplayerquantity(self):
        return self.m_playerquantitiy

    def isvalid(self):
        if not (self.m_showcard >= 0 or self.m_showcard == -3):
            return False
        return True

    def getpreflopbetdata(self):
        return self.m_handsinfo["data"][1]

    def getflopbetdata(self):
        return self.m_handsinfo["data"][2]

    def getturnbetdata(self):
        return self.m_handsinfo["data"][3]

    def getriverbetdata(self):
        return self.m_handsinfo["data"][4]

    def getrounddata(self, round):
        return self.m_handsinfo["data"][round + 1]

    def getboard(self):
        handsdata = self.m_handsinfo["data"]
        infolen = len(handsdata)
        if infolen < 6:
            return handsdata[-1]
        if infolen == 7:
            return handsdata[-1]
        for idx in xrange(4,0,-1):
            if handsdata[idx]!= None:
                return handsdata[idx]

    def getprivatecard(self):
        if self.m_showcard > 0 or self.m_showcard == -3:
            return self.m_handsinfo["data"][5]
        else:
            return None

    # round starts from 0, which means preflop
    # actionidx starts from 0, which means the first action
    def getcumuinfo(self,round, actionidx):
        if round == 0 and actionidx == 0:
            self.m_cumuinfo.reset()

        action, value = self.getrounddata(round)[actionidx]
        self.m_cumuinfo.update(action, value)
        return self.m_cumuinfo
