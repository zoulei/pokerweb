#-*- coding:utf-8 -*-
import hunlgame
import json
import math
import Constant
import earthmover
import traceback
import random
import copy
import winratecalculator
import handsdistribution
import shelve
import DBOperater
import handsengine
from TraverseHands import TraverseHands
import time
import signal
import multiprocessing

# this is the composite hand power
class HandPower:
    # rangestate is a object of class handsdistribution.RangeState
    def __init__(self, rangestate = None, winratestr = ""):
        self.m_myhand = None
        self.m_ophands = None
        self.m_board = None
        self.m_rangestate = rangestate
        if rangestate is not None:
            self.m_myhand = rangestate.m_myhands
            self.m_ophands = rangestate.m_ophands
            self.m_board = rangestate.m_board
        self.m_winratestr = winratestr
        self.calculatewinrate()

    def calculatewinrate(self):
        if self.m_winratestr:
            data = json.loads(self.m_winratestr)
            self.m_curwinrate = data["curwinrate"]
            self.m_data = data["winratehis"]
            return
        winratecal = winratecalculator.WinrateCalculator(self.m_rangestate)
        self.m_curwinrate = winratecal.calmywinrate()
        nextturnstackwinrate = winratecal.calnextturnstackwinrate()
        winratehistogram = [v[1] for v in nextturnstackwinrate]

        winratehistogram.sort(reverse=True)
        slotnum = math.ceil(1 / Constant.HANDSTRENGTHSLOT) + 1
        self.m_data = [0] * int(slotnum)
        if len(winratehistogram) == 0:
            print "winratehistogram's length is zero."
            print "myhand:",hunlgame.board2str(self.m_myhand.get())
            print "board:",hunlgame.board2str(self.m_board)
            print "ophands:"
            print self.m_ophands[0].normalize()
            self.m_ophands[0].printdata()
            print "winrate valid:",winratecal.m_valid
            raise
        for winrate in winratehistogram:
            self.m_data[int(math.ceil( (1 - winrate) / Constant.HANDSTRENGTHSLOT ) )] += 1

    def __sub__(self, other):
        try:
            return earthmover.EMD(self.m_data,other.m_data) + \
                   Constant.CURWINRATEDIFFRATE * abs(self.m_curwinrate - other.m_curwinrate) * max(self.m_curwinrate,other.m_curwinrate)
        except:
            print "WinrateHistogram error : "
            print self.m_data
            print other.m_data
            traceback.print_exc()
            raise

    def __hash__(self):
        return hash(self.__str__())

    # 该方法生成的str可以用作构造函数中的winratestr参数用于恢愎Handpower对象
    def __str__(self):
        doc = {
            "curwinrate"    :   self.m_curwinrate,
            "winratehis"    :   self.m_data,
        }
        return json.dumps(doc)

def testcurwinrate():
    import handsengine
    rangenum = 0.3
    handsrangeobj = handsengine.prefloprangge()
    ophandsrange = handsrangeobj.gethandsinrange(rangenum)
    board =  hunlgame.generateCards("ASTS4H")
    winratedata = []
    for hand in ophandsrange:
        rangestate = handsdistribution.RangeState(board,hand,handsdistribution.HandsDisQuality(ophandsrange))
        if not rangestate:
            continue
        curwinrate = winratecalculator.WinrateCalculator(rangestate).calmywinrate()
        winratedata.append([hand,curwinrate])
    winratedata.sort(key=lambda v:v[1],reverse=True)
    winratedata = [v for v in winratedata if v[1] != -1]
    # for hand,winrate in winratedata:
    #     print hand,winrate
    # return
    for hand, winrate in winratedata:
        print "===========",rangenum,hunlgame.board2str(board),"==============="
        for hand1, winrate1 in winratedata:
            print hand,"\t",hand1,"\t",abs(winrate-winrate1)*max(winrate,winrate1)*100
        raw_input()

def testwinratestack():
    import handsengine
    boardlist = ["ASTS4H","ASKS4H","AS7S4H","ASTC4H","ASTS4S","ASKCJH","AS7C6H","AS7H6H","8S6C3H","8S7C6H","KSJC4H",
                 "JSTC5H","JSTS5H","ASACJH","8S8C4H","8S8C8H","8S8C7C"]
    boardlist = [hunlgame.generateCards(v) for v in boardlist]
    rangenum = 0.3
    handsrangeobj = handsengine.prefloprangge()
    ophandsrange = handsrangeobj.gethandsinrange(rangenum)
    myhand = hunlgame.generateHands("AD5D")
    hplist = []
    for board in boardlist:
        rangestate = handsdistribution.RangeState(board,myhand,handsdistribution.HandsDisQuality(ophandsrange))
        if not rangestate:
            continue
        hplist.append(HandPower(handsdistribution.RangeState(board,myhand,handsdistribution.HandsDisQuality(ophandsrange))))
    for board, hp in zip(boardlist,hplist):
        diflist = []
        for board1, hp1 in zip(boardlist,hplist):
            diflist.append([board1,board,hp-hp1])
        diflist.sort(key=lambda v:v[2])
        for a,b,c in diflist:
            print hunlgame.board2str(a),"\t",hunlgame.board2str(b),"\t",c

class RandomHandPower(HandPower):
    def __init__(self, turn = 2, opponentqt = 1):
        cardlist = []
        for i in xrange(turn + 1 + 2):
            cardlist.append(hunlgame.Cardsengine.randomcard(cardlist))
        self.m_myhand = hunlgame.Hands(cardlist[:2])
        self.m_board = cardlist[2:]
        self.m_ophands = []
        for idx in xrange(opponentqt):
            self.generaterandomrange(cardlist)
            self.m_ophands.append(handsdistribution.HandsDisQuality(copy.deepcopy(self.m_handsdis)))
        rangestate = handsdistribution.RangeState(self.m_board,self.m_myhand,self.m_ophands)
        if not rangestate:
            print "random hand power not valid, this situation happens rare."
            raise
        HandPower.__init__(self,rangestate)

    def generaterandomrange(self, removecardlist):
        handsrangeobj = hunlgame.HandsRange()
        handsrangeobj.addFullRange()
        for card in removecardlist:
            handsrangeobj.eliminateCard(card)
        handsdata = handsrangeobj.get()
        sortresult = hunlgame.sorthands_(self.m_board, [v.get() for v in handsdata])
        resultkeys = sortresult.keys()
        resultkeys.sort()
        sortedhandsdata = []
        for key in resultkeys:
            for handidx in sortresult[key]:
                sortedhandsdata.append(handsdata[handidx])
        self.m_handsdis = {}
        self.randomrange(sortedhandsdata,1)

    def randomrange(self,handslist,probability):
        handslen = len(handslist)
        if handslen == 1:
            self.m_handsdis[handslist[0]] = probability
            return
        p1 = random.uniform(0,probability)
        p2 = probability - p1
        self.randomrange(handslist[:handslen/ 2],p1)
        self.randomrange(handslist[handslen/ 2:],p2)

def testrandompower():
    hplist = []
    while True:
        tmprhp = RandomHandPower()
        for hp in hplist:
            print tmprhp - hp
            if tmprhp - hp < 0.5:
                break
        else:
            hplist.append(tmprhp)
            json.dump([str(v) for v in hplist],open("tmpresult/randompower","w"))
        print "===============\t",len(hplist)
        # if len(hplist) == 150:
        #     break
        # raw_input()
    return

def randompowerlength():
    hplist = [HandPower(winratestr=v) for v in json.load(open("tmpresult/randompower"))]
    print len(hplist)

# 这个方法的作用是测试随机生成的路标的质量
# 测试的方法为查看牌例中的各种手牌是否都有与其相近的路标,
# 将所有的牌例与路标都测一下距离,然后计算一下每个牌例与所有路标之间的最小距离,输出一个最小距离的list
# 然后针对这个最小距离的list又可以进行各种操作
def testrandompowerquality():
    hplist = [HandPower(winratestr=v) for v in json.load(open("tmpresult/randompower"))]
    # import DBOperater, handsengine
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})
    disdata = shelve.open("data/disdata","c")
    idx = 0
    for doc in result:
        try:
            replay = handsengine.ReplayEngine(doc)
            if replay.m_handsinfo.getturncount() == 1:
                continue
            replay.traversepreflop()
            preflopinfo = replay.getpreflopinfomation()
            if preflopinfo["remain"] != 2 or preflopinfo["allin"] != 0:
                continue
            playerrange = preflopinfo["range"]
            rangelist = []
            for state, rangenum in zip(replay.m_inpoolstate, playerrange):
                if state == 1:
                    rangelist.append(replay.m_handsrangeobj.gethandsinrange(rangenum))
                # else:
                #     rangelist.append(None)
            myhanddis = dict(zip(rangelist[0],[1] * len(rangelist[0])))
            myhanddis = handsdistribution.HandsDisQuality(myhanddis)
            myhanddis.normalize()
            ophanddis = dict(zip(rangelist[1],[1] * len(rangelist[1])))
            ophanddis = handsdistribution.HandsDisQuality(ophanddis)
            ophanddis.normalize()
            for hand in rangelist[0]:
                rangestate = handsdistribution.RangeState(replay.getcurboard(),hand,[ophanddis])
                # if rangestate:
                #     print "True"
                # else:
                #     print "False"
                # print "bool:",bool(rangestate)
                if not rangestate:
                    continue
                curhp = HandPower(rangestate)
                dislist = [curhp - v for v in hplist]
                mindisstr = str(round(min(dislist),1))
                if mindisstr not in disdata:
                    disdata[mindisstr] = 0
                disdata[mindisstr] += 1
            for hand in rangelist[1]:
                rangestate = handsdistribution.RangeState(replay.getcurboard(),hand,[myhanddis])
                if not rangestate:
                    continue
                curhp = HandPower(rangestate)
                dislist = [curhp - v for v in hplist]
                # dislist.sort()
                # print dislist[:10]
                mindisstr = str(round(min(dislist),1))
                if mindisstr not in disdata:
                    disdata[mindisstr] = 0
                disdata[mindisstr] += 1
            idx += 1
            if idx % 2000 == 0:
                print "idx",idx
        except:
            print "=========================="
            print doc["_id"]
            # traceback.print_exc()
            print "=========================="
            raise

    disdata.close()

def readrandompowerquanlity():
    disdata = shelve.open("data/disdata","c")
    keylist = []
    for key in disdata:
        keylist.append(key)
    keylist.sort(key=lambda v:float(v))
    for key in keylist:
        print key ,"\t:\t",disdata[key]
    disdata.close()

def gethandpowerfunc(rangestate):
    return HandPower(rangestate)

# 该类用于生成随机路标以及读取随机路标
class RandomMarker:
    def __init__(self):
        self.m_hplist = [HandPower(winratestr=v) for v in json.load(open("tmpresult/randompower"))]
        self.m_hplist.sort(key=lambda v:v.m_curwinrate,reverse=True)
        self.m_length = len(self.m_hplist)

    # 此方法用于生成随机路标,生成的方式为向已有的路标库中进行添加
    # 此方法会一直运行下去,除非手动结束程序
    def generaterandompower(self,mindis=0.5):
        hplist = self.m_hplist
        while True:
            tmprhp = RandomHandPower()
            for hp in hplist:
                print tmprhp - hp
                if tmprhp - hp < mindis:
                    break
            else:
                hplist.append(tmprhp)
                json.dump([str(v) for v in hplist],open("tmpresult/randompower","w"))
            print "===============\t",len(hplist)
        return

# 这个方法的功能是从牌例中学习路标
# 这个结果可以用于与随机生成的路标进行质量对比
class MarkerGeneraterTraverser(TraverseHands):
    def initdata(self):
        self.m_hplist = []

    def mainfunc(self, handsinfo):
        now = time.time()
        replay = handsengine.ReplayEngine(handsinfo)
        if replay.m_handsinfo.getturncount() == 1:
            return
        replay.traversepreflop()
        preflopinfo = replay.getpreflopinfomation()
        if preflopinfo["remain"] != 2 or preflopinfo["allin"] != 0:
            return
        playerrange = preflopinfo["range"]
        rangelist = []
        for state, rangenum in zip(replay.m_inpoolstate, playerrange):
            if state == 1:
                rangelist.append(replay.m_handsrangeobj.gethandsinrange(rangenum))
        print hunlgame.board2str(replay.getcurboard())
        print replay.m_handsinfo.getid()
        print playerrange
        print replay.m_inpoolstate
        myhanddis = dict(zip(rangelist[0],[1] * len(rangelist[0])))
        myhanddis = handsdistribution.HandsDisQuality(myhanddis)
        myhanddis.normalize()
        ophanddis = dict(zip(rangelist[1],[1] * len(rangelist[1])))
        ophanddis = handsdistribution.HandsDisQuality(ophanddis)
        ophanddis.normalize()
        rangestatelist = []
        for hand in rangelist[0]:
            rangestate = handsdistribution.RangeState(copy.deepcopy(replay.getcurboard()),copy.deepcopy(hand),copy.deepcopy(ophanddis))
            if not rangestate:
                continue
            rangestatelist.append(rangestate)
        for hand in rangelist[1]:
            rangestate = handsdistribution.RangeState(copy.deepcopy(replay.getcurboard()),copy.deepcopy(hand),copy.deepcopy(myhanddis))
            if not rangestate:
                continue
            rangestatelist.append(rangestate)
        # for rangestate in rangestatelist:
        #     hp = HandPower(rangestate)

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = multiprocessing.Pool(Constant.THREADNUM)
        # pool = multiprocessing.Pool(1)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            # result = self.m_pool.map_async(self.mainfunc, doclist)
            result = pool.map_async(gethandpowerfunc, rangestatelist)
            hplist = result.get(99999999)  # Without the timeout this blocking call ignores all signals.
            for curhp in hplist:
                for markerhp in self.m_hplist:
                    if curhp - markerhp < Constant.HANDSPOWERGRANULARITY:
                        break
                else:
                    self.m_hplist.append(curhp)
            json.dump([str(v) for v in self.m_hplist],open(Constant.HANDSPOWERMARKER,"w"))
        except KeyboardInterrupt:
            pool.terminate()
            pool.close()
            pool.join()
            exit()
        else:
            pool.close()
        pool.join()
        print "spend:",time.time() - now

if __name__ == "__main__":
    # testrandompower()
    # testrandompowerquality()
    # readrandompowerquanlity()
    # testcurwinrate()
    # testwinratestack()
    # MarkerGeneraterTraverser(Constant.HANDSDB,Constant.HANDSCLT,step=1000).traverse()
    testwinratestack()