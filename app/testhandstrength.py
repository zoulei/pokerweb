import hunlgame
from afterflopwinrate import WinrateEngine
from handsengine import HandsInfo
from TraverseHands import TraverseHands
import Constant

class Handstrength(WinrateEngine):

    def calhandswinrate(self, pos):
        myhands = self.m_range[pos]
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)

        curboard = self.getcurboard()
        curboard[0] = hunlgame.Card(3, 5)
        curboard[1] = hunlgame.Card(2, 14)
        curboard[2] = hunlgame.Card(1, 8)
        curboard.append(hunlgame.Card(1, 9))

        self.printdebuginfo(pos,myhands,ophands,curboard)
        if not curboard[-1]:
            return

        printdata = []
        for curhand in myhands:
            tmphands = [curhand,]

            if len(ophands) == 1:
                winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
                curwinrate = winratecalculator.calmywinrate()

                printdata.append([curhand,curwinrate])
            else:
                # not wrriten yet
                print "oplen : ",len(ophands)
                return
        printdata.sort(key=lambda v:v[1],reverse=True)
        for curhand, curwinrate in printdata:
            print curhand,"\t", curwinrate

    def updatecumuinfo(self,round1,actionidx):
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 > 1:
            result = self.calhandswinrate(self.m_cumuinfo.m_lastplayer)

def mainfunc(handsinfo):
    Handstrength(handsinfo).test()

if __name__ == "__main__":
    TraverseHands(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="35357006093039820170322202148",sync=False).traverse()