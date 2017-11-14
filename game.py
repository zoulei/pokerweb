from hunlgame import Poker
from handsengine import HandsInfo

class DealerFromHistory(Poker):
    def __init__(self, handsdata):
        self.m_handsengine = HandsInfo(handsdata)
        playerquantity = self.m_handsengine.getplayerquantity()
        Poker.__init__(self,playerquantity)

    def getFlop(self):
        return self.m_handsengine.getboard()[:3]

    def getTurn(self):
        return self.m_handsengine.getboard()[3]

    def getRiver(self):
        return self.m_handsengine.getboard()[4]

    def distribute(self):
        return self.m_handsengine.m_privatehands

    def distributehand(self, pos):
        return self.m_handsengine.gethand(pos)

    def updateaction(self, action , value):
        if self.m_handsengine.m_cumuinfo.m_lastaction == 12:
            return
        self.m_handsengine.executenextaction()

    def getboard(self):
        return self.m_handsengine.getcurboard()

    def getturnboard(self,turnidx):
        return self.m_handsengine.getturnboard(turnidx)

    def getcurrentturn(self):
        return self.m_handsengine.m_cumuinfo.m_curturn

    def checkavailable(self):
        if self.m_handsengine.m_cumuinfo.m_betvalue == 0:
            return True
        if self.m_handsengine.m_cumuinfo.m_betvalue == self.m_handsengine.m_cumuinfo.m_bb and \
            self.m_handsengine.m_cumuinfo.m_nextplayer == 8 and self.m_handsengine.m_cumuinfo.m_curturn == 1 and \
                self.m_handsengine.m_cumuinfo.m_curturnover == False:
            return True
        return False