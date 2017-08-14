from afterflopstate import Statekey
from handsengine import HandsInfo
from TraverseHands import TraverseHands
import Constant
import hunlgame

class WinrateEngine(HandsInfo):
    def __init__(self,handsinfo):
        HandsInfo.__init__(self,handsinfo)
        self.m_statekeys = self.m_handsinfo["statekeys"]
        self.m_preflopgeneralstate = self.m_handsinfo[Constant.PREFLOPGENERALSTATE]

        self.m_range = []

    def initprefloprange(self):
        prefloprange = self.m_preflopgeneralstate["range"]
        for rangenum in prefloprange:
            self.m_range.append( self.m_cumuinfo.m_handsrangeobj.gethandsinrange(rangenum) )

    # pos is relativepos
    def calwinrate(self, pos):
        myhands = self.m_range[pos]
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)
        if len(ophands) == 1:
            winratecalculator = hunlgame.SoloWinrateCalculator(self.getcurboard(), myhands, ophands[0])
            curwinrate = winratecalculator.calmywinrate()
            nextturnwinrate = winratecalculator.calnextturnwinrate()
            return [curwinrate, nextturnwinrate]

    def calnextwinrate(self):
        return self.calwinrate(self.m_cumuinfo.m_nextplayer)

    def calrealwinrate(self, pos):
        curhand = self.gethand(self.m_cumuinfo.getrealpos(pos))
        if not curhand:
            return
        myhands = [curhand,]
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)
        if len(ophands) == 1:
            winratecalculator = hunlgame.SoloWinrateCalculator(self.getcurboard(), myhands, ophands[0])
            curwinrate = winratecalculator.calmywinrate()
            nextturnwinrate = winratecalculator.calnextturnwinrate()
            return [curwinrate, nextturnwinrate]

    def updatecumuinfo(self,round,actionidx):
        if round > 1:
            curstatestr = self.m_statekeys[round - 2][actionidx]
            print "curstatestr : ", curstatestr
            print "joinrate: ", self.m_preflopgeneralstate["range"]
            print "round-actionidx:",round,actionidx,self.calrealwinrate(self.m_cumuinfo.m_nextplayer)

        HandsInfo.updatecumuinfo(self,round,actionidx)
        if round == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

    def test(self):
        self.traversepreflop()
        self.updatecumuinfo(2,0)
        raw_input()
        print "\n\n\n"

class WinrateCalculater(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not showcard > 0:
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        return False

    def mainfunc(self, handsinfo):
        engine = WinrateEngine(handsinfo)
        engine.test()

if __name__ == "__main__":
    WinrateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()