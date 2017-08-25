from afterflopstate import Statekey
from handsengine import HandsInfo
from TraverseHands import TraverseHands
import Constant
import hunlgame
import traceback
import time
import threading

lock = threading.Lock()

class WinrateEngine(HandsInfo):
    def __init__(self,handsinfo):
        HandsInfo.__init__(self,handsinfo)
        self.m_statekeys = self.m_handsinfo["statekeys"]
        # self.m_preflopgeneralstate = self.m_handsinfo[Constant.PREFLOPGENERALSTATE]

        self.m_range = []

    def initprefloprange(self):
        prefloprange = self.m_cumuinfo.m_prefloprange
        # print "prefloprange : ", prefloprange
        # print "inpoolstate : ", self.m_cumuinfo.m_inpoolstate
        for pos, rangenum in enumerate(prefloprange):
            if self.m_cumuinfo.m_inpoolstate[pos] != 0:
                self.m_range.append(self.m_cumuinfo.m_handsrangeobj.gethandsinrange(rangenum) )
                print "range : ", rangenum
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

        curboard = self.getcurboard()

        curboard[-1] = hunlgame.Card(2, 4)
        curboard[0] = hunlgame.Card(2, 11)
        curboard[1] = hunlgame.Card(1, 8)

        print "board : "
        for v in curboard:
            print v
        print "pos : ", pos
        # print "myhand : ",tmphands[0]
        print "hand len : ", len(myhands),len(ophands[0])
        print "range : ", self.m_cumuinfo.m_prefloprange

        if not curboard[-1]:
            return

        printdata = []

        for hand in myhands:
            tmphands = [hand,]

            if len(ophands) == 1:
                winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
                curwinrate = winratecalculator.calmywinrate()
                nextturnwinrate = winratecalculator.calnextturnwinrate()
                printstr = Constant.TAB.join([str(v) for v in [hand, round(curwinrate,3), round(nextturnwinrate - curwinrate, 3)]])
                printdata.append([printstr, curwinrate, nextturnwinrate])
                # f = open(Constant.CACHEDIR + "winrate448","a")
                # f.write(Constant.TAB.join([str(v) for v in [hand, round(curwinrate,3), round(nextturnwinrate - curwinrate, 3)]]) + "\n")
                # print hand, round(curwinrate, 3), round(nextturnwinrate - curwinrate, 3)
                # nextturnwinrate = 0
                # return [curwinrate, nextturnwinrate]
            else:
                # not wrriten yet
                print "oplen : ",len(ophands)
                return

        printdata.sort(key=lambda v:v[1],reverse=True)
        for data in printdata:
            print data[0]

    def updatecumuinfo(self,round1,actionidx):
        global lock
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 > 1:
            # print "curstatestr : ", curstatestr
            # print "joinrate: ", self.m_cumuinfo.m_prefloprange
            # print "round-actionidx:",round1,actionidx
            result = self.calrealwinrate(self.m_cumuinfo.m_lastplayer)
            # if not result:
            #     return
            # if result:

            # print "result: ",result
            # return
                # print "---------",[curwinrate,nextwinrate]
                # print "---------diff : ",  nextwinrate - curwinrate

        # if round1 > 1:
            statekey = self.getstatekey(round1,actionidx)
            statekey = statekey.replace(";","___")
            statekey = statekey.replace(",","_")

            lock.acquire()
            f = open(Constant.CACHEDIR + statekey, "a")
            # f1 = open(Constant.CACHEDIR + statekey + "_showcard", "a")
            if result:
            # if self.gethand(self.m_cumuinfo.m_lastplayer):
                curwinrate, nextwinrate = result
                # f1.write(Constant.TAB.join([str(v) for v in [round(curwinrate,3), round(nextwinrate,3), self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
                f.write(Constant.TAB.join([str(v) for v in [round(curwinrate,3), round(nextwinrate-curwinrate,3), self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
            else:
                f.write(Constant.TAB.join([str(v) for v in [-1, -1, self.m_cumuinfo.m_lastattack,self.getid()]]) + "\n")
            # else:
            #     f.write(Constant.TAB.join([str(v) for v in [-1, -1, self.m_cumuinfo.m_lastattack,self.getid()]])+"\n")
            f.close()
            # f1.close()
            lock.release()

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
    WinrateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="35357006093039820170307202741",sync=True).traverse()