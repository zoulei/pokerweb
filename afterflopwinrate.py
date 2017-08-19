from afterflopstate import Statekey
from handsengine import HandsInfo
from TraverseHands import TraverseHands
import Constant
import hunlgame
import traceback

class WinrateEngine(HandsInfo):
    def __init__(self,handsinfo):
        HandsInfo.__init__(self,handsinfo)
        self.m_statekeys = self.m_handsinfo["statekeys"]
        self.m_preflopgeneralstate = self.m_handsinfo[Constant.PREFLOPGENERALSTATE]

        self.m_range = []

    def initprefloprange(self):
        prefloprange = self.m_cumuinfo.m_prefloprange
        # print "prefloprange : ", prefloprange
        # print "inpoolstate : ", self.m_cumuinfo.m_inpoolstate
        for pos, rangenum in enumerate(prefloprange):
            if self.m_cumuinfo.m_inpoolstate[pos] != 0:
                self.m_range.append(self.m_cumuinfo.m_handsrangeobj.gethandsinrange(rangenum) )
            else:
                self.m_range.append(self.m_cumuinfo.m_handsrangeobj.gethandsinrange(0))

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
        # realpos = self.m_cumuinfo.getrealpos(pos)
        curhand = self.gethand(pos)
        # print "hand : ",self.gethand(self.m_cumuinfo.getrealpos(pos))
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

        # print "handsid : ",self.m_handsinfo["_id"]
        # print "handslen : ",len(myhands),len(ophands)

        if len(ophands) == 1:
            curboard = self.getcurboard()
            # curboard[1] = hunlgame.Card(0, 3)
            # print "board : "
            # for v in curboard:
            #     print v
            # print "pos : ", pos
            # print "myhand : ",myhands[0]
            # print "hand len : ", len(myhands),len(ophands[0])

            winratecalculator = hunlgame.SoloWinrateCalculator(curboard, myhands, ophands[0],debug=False)
            curwinrate = winratecalculator.calmywinrate()
            nextturnwinrate = winratecalculator.calnextturnwinrate()
            # nextturnwinrate = 0
            return [curwinrate, nextturnwinrate]
        else:
            # not wrriten yet
            print "oplen : ",len(ophands)
            raise

    def updatecumuinfo(self,round1,actionidx):
        if round1 > 1:
            curstatestr = self.m_statekeys[round1 - 2][actionidx]
            # print "curstatestr : ", curstatestr
            # print "joinrate: ", self.m_cumuinfo.m_prefloprange
            # print "round-actionidx:",round1,actionidx
            result = self.calrealwinrate(self.m_cumuinfo.m_nextplayer)
            if result:
                curwinrate,nextwinrate = result
                # print "---------",[curwinrate,nextwinrate]
                # print "---------diff : ",  nextwinrate - curwinrate

        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 > 1:
            statekey = self.getstatekey(round1,actionidx)
            statekey = statekey.replace(";","___")
            statekey = statekey.replace(",","_")
            f = open(Constant.CACHEDIR + statekey, "a")
            if result:
                f.write(Constant.TAB.join([str(v) for v in [round(curwinrate,3), round(nextwinrate,3), self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
            else:
                f.write(Constant.TAB.join([str(v) for v in [-1, -1, self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
            f.close()

    def test(self):
        self.traversepreflop()
        self.updatecumuinfo(2,0)
        # self.updatecumuinfo(2, 1)
        # raw_input()
        # print "\n\n\n"

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
        # if handsinfo[Constant.STATEKEY][0][0] != "2;;2,1,2":
        #     return True
        return False

    def mainfunc(self, handsinfo):
        engine = WinrateEngine(handsinfo)
        try:
            engine.test()
        except:
            print handsinfo["_id"]
            traceback.print_exc()
            print "123"


if __name__ == "__main__":
    WinrateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT,handsid="").traverse()