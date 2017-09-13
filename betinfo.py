from handsengine import HandsInfo
from afterflopwinrate import WinrateEngine, FnameManager
from TraverseHands import TraverseHands
import hunlgame
import math
from pickleengine import PickleEngine
import Constant
import traceback

class FirstTurnBetData:
    def __init__(self, winrate, attack, iswin):
        self.m_winrate = winrate
        self.m_attack = attack
        self.m_iswin = iswin
        if attack == 1 and self.m_iswin == 1:
            self.m_attack = 0
            self.m_iswin = 1
        elif attack == 1 and self.m_iswin == 0:
            self.m_attack = -1
            self.m_iswin = 1

    def __str__(self):
        return "\t".join([str(v) for v in  [self.m_winrate,self.m_attack,self.m_iswin]])

class FTBetdataEngine(WinrateEngine):
    def __init__(self,handsinfo):
        WinrateEngine.__init__(self,handsinfo)
        self.m_attack = 1

        # print handsinfo["_id"]

    def calbetdata(self):
        curboard = self.getcurboard()

        if not curboard[-1]:
            return

        myhands = [self.gethand(self.m_cumuinfo.m_lastplayer),]
        ophands = []
        for pos,inpool in enumerate(self.m_cumuinfo.m_inpoolstate):
            if inpool == 1 and pos != self.m_cumuinfo.m_lastplayer:
                ophands.append(self.gethand(pos))

        winratecalculator = hunlgame.SoloWinrateCalculator(curboard, myhands, ophands,debug=False)
        iswin = winratecalculator.calmywinrate()

        ophands = []
        for idx in xrange(len(self.m_range)):
            if idx == self.m_cumuinfo.m_lastplayer:
                continue
            handsinrange = self.m_range[idx]
            if handsinrange:
                ophands.append(handsinrange)

        if len(ophands) == 1:
            winratecalculator = hunlgame.SoloWinrateCalculator(curboard, myhands, ophands[0],debug=False)
            curwinrate = winratecalculator.calmywinrate()

            if self.m_attack == 1 and iswin == 0:
                return [FirstTurnBetData(curwinrate,0 ,iswin),FirstTurnBetData(curwinrate,-1 ,1 - iswin)]

            return [FirstTurnBetData(curwinrate,self.m_attack ,iswin),]

    def updateattackinfo(self):
        tmpattack = self.m_cumuinfo.m_lastattack
        while tmpattack > 1:
            tmpattack -= 1
        if tmpattack:
            self.m_attack = math.ceil(self.m_attack) + tmpattack

    def updatecumuinfo(self,round1,actionidx):
        HandsInfo.updatecumuinfo(self,round1,actionidx)
        if round1 == 1 and self.m_cumuinfo.m_curturnover:
            self.initprefloprange()

        if round1 == 1:
            return
        if self.m_cumuinfo.m_lastaction not in [2,3,4.2]:
            return
        if self.m_cumuinfo.m_lastaction == 3 and self.m_attack != 1:
            return

        self.updateattackinfo()
        betdata = self.calbetdata()
        if betdata is None:
            return
        # print betdata
        for idx,v in enumerate(betdata):
            PickleEngine.tempdump(v,  FnameManager().generateftbetdatatempfname(self.getpreflopstatekey(), self.getid(),round1+idx*10000,actionidx))

class TraverseFTBetdata(TraverseHands):
    def filter(self, handsinfo):
        if handsinfo["showcard"] != 1:
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        if HandsInfo(handsinfo).getshowcardquantity() != 2:
            return True
        return False

    def traverse(self):
        TraverseHands.traverse(self)

        fnamemanagerobj = FnameManager()
        PickleEngine.combine(fnamemanagerobj.getftbetdatatempfnamerawstatekey, fnamemanagerobj.generateftebetdatafname )

def mainfunc(handsinfo):
    try:
        FTBetdataEngine(handsinfo).traversealldata()
    except KeyboardInterrupt:
        exit()
    except:
        print handsinfo["_id"]
        traceback.print_exc()


def testbetinfo():
    betinfolist = PickleEngine.load(Constant.CACHEDIR + "2______2_1_2.ftbetdata")
    zerolist = []
    for v in betinfolist:
        if v.m_attack == 0:
            zerolist.append(v)
    zerolist.sort(key=lambda v:v.m_winrate)
    for v in zerolist:
        print v
    print len(betinfolist)

class BetinfoClassifier:
    def __init__(self, datafname):
        self.m_datafname = datafname
        # self.initbetvaluerange()
        self.m_betvaluerange = [-1, 0,1,2,3,4]
        self.m_classifyvalue = [0] * len(self.m_betvaluerange)

    def initbetvaluerange(self):
        self.m_data = PickleEngine.load(self.m_datafname)
        betvalueset = set()
        for v in self.m_data:
            betvalueset.add(round(v.m_attack,4))

        print betvalueset
        betvalueset = list(betvalueset)
        betvalueset.sort()
        print betvalueset
        self.m_betvaluerange = betvalueset


    def classify(self):
        self.m_data = PickleEngine.load(self.m_datafname)

        for idx, betvalue in enumerate(self.m_betvaluerange[:-1]):
            start = self.m_classifyvalue[idx]
            leasterror = len(self.m_data)
            leastvalue = start
            classifyvalue = start
            while classifyvalue < 1:
            # for classifyvalue in xrange(start, 1, 0.01):
                curerror = self.geterror(classifyvalue, betvalue)
                if curerror < leasterror:
                    leasterror = curerror
                    leastvalue = classifyvalue
                print idx, curerror ,classifyvalue
                classifyvalue += 0.01

            self.m_classifyvalue[idx + 1] = leastvalue
            print idx, leasterror, leastvalue

        return self.m_classifyvalue

    def geterror(self, classifyvalue, betvalue):
        error = 0
        e1 = 0
        e2 = 0
        e3 = 0
        for data in self.m_data:
            curattack = int(data.m_attack)
            if curattack > 4:
                curattack = 4
            # if curattack != betvalue:
            #     continue
            if curattack == betvalue:
                if data.m_winrate <= classifyvalue and data.m_iswin == 0:
                    # include invalid data, classifyvalue too big
                    error += 1
                    e1 += 1
                elif data.m_winrate > classifyvalue and data.m_iswin == 1:
                    # did not include valid data, classifyvalue too small
                    error += 1
                    e2 += 1
            elif curattack > betvalue:
                if data.m_winrate <= classifyvalue and data.m_iswin == 1:
                    # include higher betvalue valid data, classifyvalue too big
                    error += 1
                    e3 += 1
        print "e value : ",e1,e2,e3

        return error

if __name__ == "__main__":
    TraverseFTBetdata(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="",sync=False,step=10000).traverse()
    testbetinfo()
    print BetinfoClassifier(Constant.CACHEDIR + "2______2_1_2.ftbetdata").classify()