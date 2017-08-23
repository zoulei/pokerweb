from afterflopstate import Statekey
from handsengine import HandsInfo
from TraverseHands import TraverseHands
import Constant
import hunlgame
import traceback
import time

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
            myhands = self.m_range[pos]
            # return
        else:
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
            #
            # curboard[-1] = hunlgame.Card(2, 12)
            # curboard[0] = hunlgame.Card(3, 13)
            # curboard[1] = hunlgame.Card(1, 8)
            #
            # print "board : "
            # for v in curboard:
            #     print v
            # print "pos : ", pos
            # print "myhand : ",myhands[0]
            # print "hand len : ", len(myhands),len(ophands[0])

            if not curboard[-1]:
                return
            winratecalculator = hunlgame.SoloWinrateCalculator(curboard, myhands, ophands[0],debug=False)
            curwinrate = winratecalculator.calmywinrate()
            nextturnwinrate = winratecalculator.calnextturnwinrate()
            # nextturnwinrate = 0
            return [curwinrate, nextturnwinrate]
        else:
            # not wrriten yet
            print "oplen : ",len(ophands)
            return

    def updatecumuinfo(self,round1,actionidx):
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 > 1:
            # print "curstatestr : ", curstatestr
            # print "joinrate: ", self.m_cumuinfo.m_prefloprange
            # print "round-actionidx:",round1,actionidx
            result = self.calrealwinrate(self.m_cumuinfo.m_nextplayer)
            if not result:
                return
            # if result:
            curwinrate,nextwinrate = result
            # print "result: ",result
            # return
                # print "---------",[curwinrate,nextwinrate]
                # print "---------diff : ",  nextwinrate - curwinrate

        # if round1 > 1:
            statekey = self.getstatekey(round1,actionidx)
            statekey = statekey.replace(";","___")
            statekey = statekey.replace(",","_")
            f = open(Constant.CACHEDIR + statekey, "a")
            f1 = open(Constant.CACHEDIR + statekey + "_showcard", "a")
            # if result:
            if self.gethand(self.m_cumuinfo.m_nextplayer):
                f1.write(Constant.TAB.join([str(v) for v in [round(curwinrate,3), round(nextwinrate,3), self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
            f.write(Constant.TAB.join([str(v) for v in [round(curwinrate,3), round(nextwinrate,3), self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
            # else:
            #     f.write(Constant.TAB.join([str(v) for v in [-1, -1, self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
            f.close()
            f1.close()

    def test(self):
        self.traversepreflop()
        self.updatecumuinfo(2,0)
        # self.updatecumuinfo(2, 1)
        # raw_input()
        # print "\n\n\n"

class WinrateCalculater(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard >= 0 or showcard == -3):
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        # if handsinfo[Constant.STATEKEY][0][0] != "2;;2,1,2":
        #     return True
        return False

    def traverse(self):
        start = time.time()
        self.traverse_(0)
        end = time.time()
        self.m_elapsedtime = end - start
        day = int(self.m_elapsedtime)/ (24 * 3600)
        hour = int(self.m_elapsedtime)% (24 * 3600)/3600
        min = int(self.m_elapsedtime)%  3600/60
        sec = int(self.m_elapsedtime)%  60
        print "processeddata : ", self.m_processeddata
        print "elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
        print "elapsedtime : ", self.m_elapsedtime
        # self.traverse_(1)
        # self.traverse_(2)

    def mainfunc(self,handsinfo):
        engine = WinrateEngine(handsinfo)
        try:
            engine.test()
        except KeyboardInterrupt:
            raise
        except:
            print handsinfo["_id"]
            traceback.print_exc()

def mainfunc( handsinfo):
    engine = WinrateEngine(handsinfo)
    try:
        engine.test()
    except KeyboardInterrupt:
        raise
    except:
        print handsinfo["_id"]
        traceback.print_exc()



if __name__ == "__main__":
    WinrateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="").traverse()