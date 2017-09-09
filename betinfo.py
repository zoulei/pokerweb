from handsengine import HandsInfo
from TraverseHands import TraverseHands

class FirstTurnBetData:
    def __init__(self, winrate, attack, iswin):
        self.m_winrate = winrate
        self.m_attack = attack
        self.m_iswin = iswin

class FTBetdataEngine(HandsInfo):
    def updatecumuinfo(self,round,actionidx):
        HandsInfo.updatecumuinfo(self,round,actionidx)

        if round == 1:
            return
        if self.m_cumuinfo.m_lastaction
        myhand = self.gethand(self.m_cumuinfo.m_lastplayer)



class TraverseFTBetdata(TraverseHands):
    def filter(self, handsinfo):
        if handsinfo["showcard"] != 1:
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        return False