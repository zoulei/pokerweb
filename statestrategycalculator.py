#-*- coding:utf-8 -*-
# 计算牌局数据中的state的完整行动分布
from Constant import *
import DBOperater
import stateinfocalculator
import handspower
import handsengine
import handsdistribution
import json
import numpy
import traceback
from TraverseHands import TraverseHands
from mytimer import Timer
from handsrank import getengine
import winratecalculator

# 行为分布, 包括各种行动的概率, 包括check, call, raise三种
class ActionDis:
    def __init__(self, jsonstr = None):
        if jsonstr is None:
            self.m_actiondis = {
                FOLD  :   0.0,
                CHECK :   0.0,
                CALL  :   0.0,
                RAISE :   0.0,
            }
        else:
            self.m_actiondis = json.loads(jsonstr)

    def addaction(self, action, rate):
        self.m_actiondis[action] += rate

    def normalize(self):
        total = sum(self.m_actiondis.values())
        for v in self.m_actiondis.keys():
            self.m_actiondis[v] /= total

    def __getitem__(self, item):
        return self.m_actiondis[item]

    def __str__(self):
        return json.dumps(self.m_actiondis)

# 完整行为分布
class FullActionDis:
    def __init__(self, checkavailable=False, restorestr = None):
        self.m_marker = handspower.RandomMarker()
        if restorestr is None:
            self.initcheckavailable(checkavailable)
            self.initdata()
        else:
            self.restoredata(restorestr)

    # 从存储的文本中恢愎数据
    def restoredata(self,restorestr):
        svdata = json.loads(restorestr)
        self.initcheckavailable(svdata["check"])
        self.m_actiondisdata = {}
        for k,v in svdata["data"].items():
            self.m_actiondisdata[handspower.HandPower(winratestr=k)] = ActionDis(jsonstr=v)

    def initcheckavailable(self, checkavailable):
        self.m_checkavailable = checkavailable
        if self.m_checkavailable:
            self.m_defend = CHECK
        else:
            self.m_defend = CALL

    # 该方法初始化本类的数据结构
    def initdata(self):
        self.m_actiondisdata = {}
        for v in self.m_marker.m_hplist:
            self.m_actiondisdata[v] = ActionDis()

    def addaction(self, hp, action, rate):
        try:
            self.m_actiondisdata[hp].addaction(action, rate)
        except:
            print str(hp)
            print action,rate
            print len(self.m_marker.m_hplist)
            raise

    # 该方法根据统计的行为分布初始化完整行为分布数据
    def initfulldis(self, actiondis):
        raiserlen = int(actiondis[RAISE] * self.m_marker.m_length)
        calllen = int(actiondis[CALL] * self.m_marker.m_length)
        checklen = int(actiondis[CHECK] * self.m_marker.m_length)
        for idx in xrange(raiserlen):
            self.addaction(self.m_marker.m_hplist[idx],RAISE,1.0)
        for idx in xrange(raiserlen,calllen+raiserlen):
            self.addaction(self.m_marker.m_hplist[idx],CALL,1.0)
        for idx in xrange(raiserlen+calllen,checklen+raiserlen+calllen):
            self.addaction(self.m_marker.m_hplist[idx],CHECK,1.0)
        for idx in xrange(raiserlen + calllen + checklen,self.m_marker.m_length):
            self.addaction(self.m_marker.m_hplist[idx],FOLD,1.0)

    # 该方法将完整的行为分布中每一个hp的行为分布都归一化
    def normalize(self):
        for hp in self.m_actiondisdata.keys():
            self.m_actiondisdata[hp].normalize()

    def __str__(self):
        targetdict = {}
        for k,v in self.m_actiondisdata.items():
            targetdict[str(k)] = str(v)
        svdata = {
            "check":self.m_checkavailable,
            "data":targetdict
        }
        return json.dumps(svdata)

def fullactiondiscalculatormainfunc(para):
    handsinfo, state, weightfunc = para
    statereader = stateinfocalculator.StateReaderEngine(handsinfo)
    turn = state.getstateturn()
    allstate = statereader.getallstate(turn)
    allaction = statereader.m_handsinfo.getspecificturnrealbetdata(turn)
    result = []
    # 遍历一个牌局中的所有state
    for curstate, curaction in zip(allstate,allaction):
        actionpos, action, value = curaction
        try:
            similar = state.similar(curstate)
        except:
            print "error:",handsinfo["_id"]
            traceback.print_exc()
            raise
        if similar == 0:
            break
        result.append([action, weightfunc(similar)])
    return result
        # actiondis.addaction(action, self.similarweightfunction(similar))

class FullActionDisCalculator(TraverseHands):
    def initdata(self):
        self.m_actiondis = ActionDis()

    def parttraverse(self, idx):
        result = TraverseHands.parttraverse(self, idx)
        for subresult in result:
            for action, weightedsimilar in subresult:
                self.m_actiondis.addaction(action, weightedsimilar)
        self.m_actiondis.normalize()

timer = Timer()
syncflag = SYNC

def reinlearningmainfunc(para):
    handsinfo, state, prefloprangeengine, actiondiskeys = para
    curturn = state.getstateturn()
    if syncflag:
        timer.start("readerengine")
    replay = stateinfocalculator.StateReaderEngine(handsinfo)
    if syncflag:
        timer.stop("readerengine")
    if replay.m_handsinfo.getturncount() < 2:
        return []
    if syncflag:
        timer.start("traverse")
    replay.traversepreflop()
    if syncflag:
        timer.stop("traverse")
    pvhand = replay.m_handsinfo.gethand(replay.m_nextplayer)
    if pvhand is None:
        return []
    if syncflag:
        timer.start("handsquality")
    oppohands = []
    for pos, inpoolstate in enumerate(replay.m_inpoolstate):
        if inpoolstate != 0 and pos != replay.m_nextplayer:
            oppohands.append(handsdistribution.HandsDisQuality(prefloprangeengine.gethandsinrange(replay.m_prefloprange[pos])))
    # oppohands = handsdistribution.HandsDisQuality(prefloprangeengine.gethandsinrange(replay.m_prefloprange[replay.m_nextplayer]))
    if syncflag:
        timer.stop("handsquality")
    board = replay.m_handsinfo.getboardcard()[:3]
    if syncflag:
        timer.start("handspower")
    try:
        targethp = handspower.HandPower(handsdistribution.RangeState(board,pvhand,oppohands))
    except:
        return []
    if syncflag:
        timer.stop("handspower")
    if syncflag:
        timer.start("statesimilar")
    statesimilar = replay.getstate(curturn,0) - state
    if syncflag:
        timer.stop("statesimilar")
    if syncflag:
        timer.start("weightfunc")
    statesimilarweight = similarweightfunction(statesimilar)
    if syncflag:
        timer.stop("weightfunc")
    result = []
    for hp in actiondiskeys:
        if syncflag:
            timer.start("hpsimilar")
        hpsimilar = targethp - hp
        if syncflag:
            timer.stop("hpsimilar")
        if syncflag:
            timer.start("hpweightfunc")
        result.append([hp, replay.m_handsinfo.getspecificturnrealbetdata(curturn)[0][1], similarhpfunction(hpsimilar) * statesimilarweight])
        if syncflag:
            timer.stop("hpweightfunc")
    return result

class ReinLearning(TraverseHands):
    def initdata(self):
        # 根据统计行为分布获取一个初始完整行为分布
        state, actiondis = self.m_otherpara
        self.m_fullactiondis = FullActionDis(state.ischeckavailable())
        # self.m_fullactiondis.initfulldis(actiondis)
        self.m_timer = Timer()
        getengine()

    def parttraverse(self, idx):
        self.m_timer.start("calculate result")
        result = TraverseHands.parttraverse(self, idx)
        self.m_timer.stop("calculate result")
        self.m_timer.start("deal with result")
        for subresult in result:
            for hp, targetaction, weight in subresult:
                self.m_fullactiondis.addaction(hp, targetaction, weight)
        open("tmpresult/actiondis","w").write(str(self.m_fullactiondis))
        self.m_timer.stop("deal with result")
        print "m_timer:======================================================="
        self.m_timer.printdata()
        print "----------------------------"
        self.m_timer.printpcgdata()
        print "public_timer:==========================="
        timer.printdata()
        print "----------------------------"
        timer.printpcgdata()
        print "handspower:============================"
        handspower.timer.printdata()
        print "----------------------------"
        handspower.timer.printpcgdata()
        print "winrate calculator:============================"
        winratecalculator.timer.printdata()
        print "----------------------------"
        winratecalculator.timer.printpcgdata()

# state相似度权值计算公式
def similarweightfunction(similar):
    return numpy.exp((similar - 1)*20)

# handspower相似度权值计算公式
def similarhpfunction(similar):
    return numpy.exp(-1.6 * similar)

# 该类基于一个牌局库来计算给定牌局的所有state的完整行动分布
class StateStrategyCalculator:
    def __init__(self,targetdoc,db=HANDSDB,clt=STATEINFOHANDSCLT,querydict=None):
        self.m_targetdoc = targetdoc
        self.m_db = db
        self.m_clt = clt
        if querydict is None:
            self.m_querydict = {}
        else:
            self.m_querydict = querydict

    def testcal(self):
        result = DBOperater.Find(self.m_db,self.m_clt,{"_id":"2017-12-11 00:59:25 203"})
        doc = result.next()
        replay = stateinfocalculator.StateReaderEngine(doc)
        state = replay.getstate(2,0)
        actiondis = self.calstrategyforspecificstate(state,2,0)
        # 这里需要把这个actiondis存起来
        open("tmpresult/actiondis","w").write(str(actiondis))
        import handsinfocommon
        handsinfocommon.pp.pprint(self.getactiondisofsimilarstate(state))

    # 计算某个state的完整行为分布
    def calstrategyforspecificstate(self, state, turnidx, actionidx):
        # 统计行为分布
        # actiondis = self.getactiondisofsimilarstate(state)

        # 根据秀牌数据进行强化学习
        prefloprangeengine = handsengine.prefloprangge()
        fullactiondis = FullActionDis(state.ischeckavailable())
        reinlearningengine = ReinLearning(self.m_db,self.m_clt,func=reinlearningmainfunc,sync=True,step=10000,
                para=[state,prefloprangeengine, fullactiondis.m_marker.m_hplist], otherpara=[state, None])
        reinlearningengine.traverse()
        return reinlearningengine.m_fullactiondis

    # 统计相似state下的行为分布
    def getactiondisofsimilarstate(self, state):
        actiondistraverseengine = FullActionDisCalculator(self.m_db,self.m_clt,
            func=fullactiondiscalculatormainfunc,para=[state,similarweightfunction])
        actiondistraverseengine.traverse()
        actiondis = actiondistraverseengine.m_actiondis
        return actiondis

if __name__ == "__main__":
    # testprinthandpower()

    import time
    start = time.time()
    print "start:",start
    ssc = StateStrategyCalculator(None)
    ssc.testcal()
    print "elapsed:",time.time() - start