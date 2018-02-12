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
    boardlist = ["ASTS4H","ASTC4H","ASTS4S","ASKCJH","AS7C6H","AS7H6H","8S6C3H","8S7C6H","KSJC4H",
                 "JSTC5H","JSTS5H","ASACJH","8S8C4H","8S8C8H","8S8C7C"]
    boardlist = [hunlgame.generateCards(v) for v in boardlist]
    rangenum = 0.3
    handsrangeobj = handsengine.prefloprangge()
    ophandsrange = handsrangeobj.gethandsinrange(rangenum)
    myhand = hunlgame.generateHands("2S5S")
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

# 这个方法的作用是测试随机生成的路标的质量
# 测试的方法为查看牌例中的各种手牌是否都有与其相近的路标,
# 将所有的牌例与路标都测一下距离,然后计算一下每个牌例与所有路标之间的最小距离,输出一个最小距离的list
# 然后针对这个最小距离的list又可以进行各种操作
def testrandompowerquality():
    hplist = [HandPower(winratestr=v) for v in json.load(open("tmpresult/randompower"))]
    import DBOperater, handsengine
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
    for key in disdata:
        print key ,"\t:\t",disdata[key]
    disdata.close()

if __name__ == "__main__":
    # testrandompower()
    testrandompowerquality()
    # readrandompowerquanlity()
    # testcurwinrate()
    # testwinratestack()