from afterflopstate import Statekey
from handsengine import HandsInfo
from TraverseHands import TraverseHands
import Constant
import hunlgame
import traceback
import time
import threading
import math
import earthmover
import json
import pickle
import numpy as np
import signal
import multiprocessing
import random
import math


lock = threading.Lock()

class WinrateHistogram:
    def __init__(self, winratedata = None, winratestr = ""):
        winratedata.sort(reverse=True)
        if winratestr:
            self.m_data = json.loads(winratestr)
        else:
            self.initdata(winratedata)

    def initdata(self, winratedata):
        slotnum = math.ceil(1 / Constant.HANDSTRENGTHSLOT) + 1
        self.m_data = [0] * int(slotnum)
        for winrate in winratedata:
            self.m_data[int(math.ceil( (1 - winrate) / Constant.HANDSTRENGTHSLOT ) )] += 1

    def __sub__(self, other):
        try:
            return earthmover.EMD(self.m_data,other.m_data)
        except:
            print "WinrateHistogram error : "
            print self.m_data
            print other.m_data
            traceback.print_exc()
            raise

    def __str__(self):
        return json.dumps(self.m_data)
        # return str(self.m_data)

class BoardHistogram:
    # self.m_histogramdata is a list of object WinrateHistogram
    # self.m_winratedata is a list of float representing winrate
    #
    # self.m_histogramdata and self.m_winratedata have the same length, the elements in the same position is for the same hand
    def __init__(self, handhistogram = None, handinfo = None, objstr = ""):
        if handhistogram is not None:
            self.init(handhistogram,handinfo)
        else:
            self.loads(objstr)

    def __str__(self):
        data = {
            "handhistogram" : self.m_rawdata,
            "handinfo" : self.m_handinfo
        }

        return pickle.dumps(data)

    def init(self, handhistogram, handinfo):
        self.m_histogramdata = [v[2] for v in handhistogram]
        self.m_handsdata = [v[0] for v in handhistogram]
        self.m_winratedata = [v[1] for v in handhistogram]

        self.m_rawdata = handhistogram

        self.m_handinfo = handinfo

    def loads(self, objstr):
        data = pickle.loads(objstr)
        self.init(data["handhistogram"], data["handinfo"])

    def printhand(self):
        print "print hand"
        for hand in self.m_handsdata:
            print hand

    def __sub__(self, other):
        # print len(self.m_winratedata), len(other.m_winratedata)
        # assert len(self.m_winratedata) == len(other.m_winratedata)
        mylen = len(self.m_histogramdata)
        otlen = len(other.m_histogramdata)
        totallen = mylen + otlen
        fh = [1.0/mylen] * mylen + [0] * otlen
        sh = [0] * mylen + [1.0/otlen] * otlen
        dm = np.zeros( (totallen,totallen),dtype=float)
        for xidx in xrange(mylen):
            for yidx in xrange(mylen,totallen):
                # print len(self.m_winratedata), xidx, len(other.m_winratedata),yidx-totallen,xidx,yidx
                dm[xidx][yidx] = self.m_histogramdata[xidx] - other.m_histogramdata[yidx - mylen]
                # print "resss:",self.m_histogramdata[xidx] - other.m_histogramdata[yidx - mylen]
                # print self.m_winratedata[xidx]
                # print other.m_winratedata[yidx - mylen]
        # print "debug ======================= "
        # print "fh:",fh
        # print "sh:",sh
        # print "dm",dm
        return earthmover.EMD(fh,sh,dm)

class WinrateEngine(HandsInfo):
    def __init__(self,handsinfo):
        HandsInfo.__init__(self,handsinfo)
        self.m_statekeys = self.m_handsinfo["statekeys"]

        self.m_range = []

    def initprefloprange(self):
        prefloprange = self.m_cumuinfo.m_prefloprange
        for pos, rangenum in enumerate(prefloprange):
            if self.m_cumuinfo.m_inpoolstate[pos] != 0:
                self.m_range.append(self.m_cumuinfo.m_handsrangeobj.gethandsinrange(rangenum) )
            else:
                self.m_range.append(self.m_cumuinfo.m_handsrangeobj.gethandsinrange(0))

    # test function
    def getbasehistogram(self, ophands):
        board = []
        board.append(hunlgame.Card(3, 5))
        board.append(hunlgame.Card(2, 7))
        board.append(hunlgame.Card(1, 8))

        hand = hunlgame.generateHands("ASJS")
        winratecalculator = hunlgame.SoloWinrateCalculator(board, [hand,], ophands[0], debug=False)
        curwinrate = winratecalculator.calmywinrate()
        # nextturnwinrate = winratecalculator.calnextturnwinrate()
        nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
        winratehistogram = [v[1] for v in nextturnstackwinrate]
        f = open(Constant.CACHEDIR + "tmp","w")
        for board, wr in nextturnstackwinrate:
            writestr = ""
            for card in board:
                writestr += str(card) + " "
            writestr += " " + str(wr) + "\n"
            f.write(writestr)
        f.close()
        return [hand,curwinrate,WinrateHistogram(winratehistogram)]

    # test function
    def printdebuginfo(self,pos,myhands,ophands):
        curboard = self.getcurboard()
        print "board : "
        for v in curboard:
            print v
        print "pos : ", pos
        # print "myhand : ",tmphands[0]
        print "hand len : ", len(myhands),len(ophands[0])
        print "range : ", self.m_cumuinfo.m_prefloprange
        print "inpool : ", self.m_cumuinfo.m_inpoolstate

    # test function
    def printhistogramdiff(self,handhistogram):
        myhandlen = len(handhistogram)
        for i in xrange(myhandlen):
            printdata = []
            for j in xrange(i + 1, myhandlen):
                handi,winratei,hisi = handhistogram[i]
                handj,winratej,hisj = handhistogram[j]
                printdata.append([handi,winratei,handj,winratej,hisi-hisj])
                # print handi," : ",handj,"      ",hisi-hisj
            printdata.sort(key=lambda v:v[4])
            for handi,winratei,handj,winratej,similarity in printdata:
                print handi," : ",handj,"   --   ",winratei," : ",winratej,"      ",similarity
            raw_input("=================================")

    def getophands(self,pos):
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)
        return ophands

    def calrealwinrate(self, pos):
        curhand = self.gethand(pos)
        if not curhand:
            # myhands = self.m_range[pos]
            return
        else:
            myhands = [curhand,]
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)

        curboard = self.getcurboard()

        # self.printdebuginfo(pos,myhands,ophands)
        if not curboard[-1]:
            return

        # handhistogram = [self.getbasehistogram(ophands)]
        handhistogram = []
        for hand in myhands:
            tmphands = [hand,]

            if len(ophands) == 1:
                winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
                curwinrate = winratecalculator.calmywinrate()
                nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
                winratehistogram = [v[1] for v in nextturnstackwinrate]
                if winratehistogram:
                    handhistogram.append([hand,curwinrate,WinrateHistogram(winratehistogram)])
            else:
                # not wrriten yet
                print "oplen : ",len(ophands)
                return

        return handhistogram
        # baseline

        # self.printhistogramdiff(handhistogram)

    def updatecumuinfo(self,round1,actionidx):
        global lock
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 > 1:
            result = self.calrealwinrate(self.m_cumuinfo.m_lastplayer)

            statekey = self.getstatekey(round1,actionidx)
            statekey = statekey.replace(";","___")
            statekey = statekey.replace(",","_")

            # lock.acquire()
            f = open(Constant.CACHEDIR + statekey, "a")
            if result and len(result) == 1:
                hand, curwinrate, winratehisobj = result[0]
                f.write(Constant.TAB.join([str(v) for v in [round(curwinrate,3), self.m_cumuinfo.m_lastattack,self.getid(),winratehisobj]])+"\n")
            else:
                f.write(Constant.TAB.join([str(v) for v in [-1, self.m_cumuinfo.m_lastattack,self.getid(), -1]]) + "\n")
            f.close()
            # lock.release()

    def test(self):
        self.traversepreflop()
        self.updatecumuinfo(2,0)

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

def mainfunc( handsinfo):
    engine = WinrateEngine(handsinfo)
    try:
        engine.test()
    except KeyboardInterrupt:
        raise
    except:
        print handsinfo["_id"]
        traceback.print_exc()

class BoardIdentifierEngine(WinrateEngine):
    def calrealwinrate1(self, pos):
        myhands = self.m_range[pos]
        ophands = self.getophands(pos)

        curboard = self.getcurboard()

        self.printdebuginfo(pos,myhands,ophands)
        if not curboard[-1]:
            return

        handhistogram = []
        for hand in myhands:
            tmphands = [hand,]

            if len(ophands) == 1:
                winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
                curwinrate = winratecalculator.calmywinrate()
                nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
                winratehistogram = [v[1] for v in nextturnstackwinrate]
                if winratehistogram:
                    handhistogram.append([hand,curwinrate,WinrateHistogram(winratehistogram)])
            else:
                # not wrriten yet
                print "oplen : ",len(ophands)
                return

        handinfo = {
            "id" : self.getid(),
            "board" : curboard,
            "pos" : pos,
            "range" : self.m_cumuinfo.m_prefloprange,
            "inpool" : self.m_cumuinfo.m_inpoolstate
        }

        basehis = self.getbasehistogram(ophands)
        print "diff:",basehis[1] - BoardHistogram(handhistogram, handinfo)
        return
        return BoardHistogram(handhistogram, handinfo)

    def updatecumuinfo(self,round1,actionidx):
        global lock
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 > 1:
            boardhistogram = self.calrealwinrate(self.m_cumuinfo.m_lastplayer)

            statekey = self.getstatekey(round1,actionidx)
            statekey = statekey.replace(";","___")
            statekey = statekey.replace(",","_")
            statekey += ".board"

            lock.acquire()
            if boardhistogram:
                f = open(Constant.CACHEDIR + statekey, "a")
                f.write(str(boardhistogram)+"\n")
                f.close()
            lock.release()

# =============================== below are test methods ================================
    # this is used for test
    def getbasehistogram(self, ophands):
        curboard = []
        curboard.append(hunlgame.Card(2, 3))
        curboard.append(hunlgame.Card(1, 8))
        curboard.append(hunlgame.Card(2, 8))

        # hand = hunlgame.generateHands("ASJS")
        import threadpool
        handhistogram = []
        for result in threadpool.ThreadPool(calhistogramforbaseboard,[[v,ophands,curboard] for v in  self.m_range[self.m_cumuinfo.m_lastplayer]]).getresult():
            if result:
                handhistogram.append(result)

        return [curboard,BoardHistogram(handhistogram)]

    # this is used for test
    def getbasehistogram1(self, ophands):
        curboard = []
        curboard.append(hunlgame.Card(3, 4))
        curboard.append(hunlgame.Card(2, 4))
        curboard.append(hunlgame.Card(2, 9))

        # hand = hunlgame.generateHands("ASJS")
        handhistogram = []
        import threadpool
        handhistogram = []
        for result in threadpool.ThreadPool(calhistogramforbaseboard,[[v,ophands,curboard] for v in  self.m_range[self.m_cumuinfo.m_lastplayer]]).getresult():
            if result:
                handhistogram.append(result)
        return [curboard,BoardHistogram(handhistogram)]

    # this is also used for test
    def calrealwinrate(self, pos):
        myhands = self.m_range[pos]
        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == pos:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)
        self.printdebuginfo(pos,myhands,ophands)
        boardhistogram = [self.getbasehistogram(ophands),self.getbasehistogram1(ophands)]
        print "getbasehistogram"
        # boardhistogram = [self.getbasehistogram(ophands),]
        print "getbasehistogram"

        paralist = []
        for curboard in hunlgame.Cardsengine().generateallflop():
            if random.random() < 0.99:
            # if random.random() <= 1:
                continue
            paralist.append([curboard,myhands,ophands])

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = multiprocessing.Pool(Constant.THREADNUM)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            # result = self.m_pool.map_async(self.mainfunc, doclist)
            result = pool.map_async(calhistogramforboard, paralist)
            result.get(99999999)  # Without the timeout this blocking call ignores all signals.
        except KeyboardInterrupt:
            pool.terminate()
            pool.close()
            pool.join()
            exit()
        else:
            pool.close()
        pool.join()

        for curboard, handhistogram in result.get():
            boardhistogram.append([curboard, BoardHistogram(handhistogram )])
        print "len:",len(boardhistogram)
        for fboard, fboardhis in boardhistogram:
            printdata = []
            for sboard, sboardhis in boardhistogram:
                if sboard == fboard:
                    continue
                printdata.append([sboard,fboardhis - sboardhis])
                # fboardhis.printhand()
                # sboardhis.printhand()
            printdata.sort(key=lambda v:v[1])
            print "="*10,hunlgame.Board(fboard),"="*10
            for board, diff in printdata:
                print hunlgame.Board(board), "\t",diff
            print "-----------------------------------"
            # raw_input("----------------")

# this is method for test
def calhistogramforboard(para):
    curboard, myhands, ophands = para
    handhistogram = []
    for hand in myhands:
        tmphands = [hand,]

        if len(ophands) == 1:
            winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
            curwinrate = winratecalculator.calmywinrate()
            nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
            winratehistogram = [v[1] for v in nextturnstackwinrate]
            if winratehistogram:
                handhistogram.append([hand,curwinrate,WinrateHistogram(winratehistogram)])
        else:
            # not wrriten yet
            print "oplen : ",len(ophands)
            return
    return [curboard,handhistogram]

# this is method for test
def calhistogramforbaseboard(para):
    hand,ophands,curboard  = para
    tmphands = [hand,]

    if len(ophands) == 1:
        winratecalculator = hunlgame.SoloWinrateCalculator(curboard, tmphands, ophands[0],debug=False)
        curwinrate = winratecalculator.calmywinrate()
        nextturnstackwinrate = winratecalculator.calnextturnstackwinrate()
        winratehistogram = [v[1] for v in nextturnstackwinrate]
        if winratehistogram:
            return [hand,curwinrate,WinrateHistogram(winratehistogram)]
    else:
        # not wrriten yet
        print "oplen : ",len(ophands)
        return

class TestBoardIdentifier(TraverseHands):
    def mainfunc(self, handsinfo):
        BoardIdentifierEngine(handsinfo).test()

if __name__ == "__main__":
    # WinrateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="35357006093039820170311203722",sync=False).traverse()
    TestBoardIdentifier(Constant.HANDSDB,Constant.TJHANDSCLT,func=None,handsid="35357006093039820170308194049",sync=False).traverse()