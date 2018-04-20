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
        self.m_actiondisdata[hp].addaction(action, rate)

    # 该方法根据统计的行为分布初始化完整行为分布数据
    def initfulldis(self, actiondis):
        raiserlen = int(actiondis[RAISE] * self.m_marker.m_length)
        callandchecklen = int( (actiondis[CALL]+actiondis[CHECK])* self.m_marker.m_length )
        for idx in xrange(raiserlen):
            self.addaction(self.m_marker.m_hplist[idx],RAISE,1.0)
        for idx in xrange(callandchecklen):
            self.addaction(self.m_marker.m_hplist[idx+raiserlen],self.m_defend,1.0)
        for idx in xrange(self.m_marker.m_length - raiserlen - callandchecklen):
            self.addaction(self.m_marker.m_hplist[idx+raiserlen+callandchecklen],FOLD,1.0)

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

    # 计算某个state的完整行为分布
    def calstrategyforspecificstate(self, state, turnidx, actionidx):
        # 统计行为分布
        actiondis = self.getactiondisofsimilarstate(state)
        # 根据统计行为分布获取一个初始完整行为分布
        fullactiondis = FullActionDis(state.ischeckavailable())
        fullactiondis.initfulldis(actiondis)

        # 根据秀牌数据进行强化学习
        result = DBOperater.Find(self.m_db,self.m_clt,self.m_querydict)
        prefloprangeengine = handsengine.prefloprangge()
        cnt1 = 0
        cnt2 = 0
        for doc in result:
            if cnt1 % 1000 == 0:
                print "cnt1:",cnt1
            if cnt2 % 1000 == 0:
                print "cnt2:",cnt2
            cnt1 += 1
            replay = stateinfocalculator.StateReaderEngine(doc)
            replay.traversepreflop()
            pvhand = replay.m_handsinfo.gethand(replay.m_nextplayer)
            if pvhand is None:
                continue
            cnt2 += 1
            oppohands = handsdistribution.HandsDisQuality(prefloprangeengine.gethandsinrange(replay.m_prefloprange[replay.m_nextplayer]))
            board = replay.m_handsinfo.getboardcard()[:3]
            targethp = handspower.HandPower(handsdistribution.RangeState(board,pvhand,oppohands))
            replay.updatecumuinfo(2,0)
            self.reinlearning(replay.getstate(2,0), targethp, replay.actiontransfer(replay.m_lastaction),fullactiondis,state)
        fullactiondis.normalize()
        return fullactiondis

    # 统计相似state下的行为分布
    def getactiondisofsimilarstate(self, state):
        actiondis = ActionDis()

        result = DBOperater.Find(HANDSDB,STATEINFOHANDSCLT,{})
        turn = state.getstateturn()
        # 首先遍历所有牌局获取相似的state, 所有的信息会更新在actiondis中
        for handdoc in result:
            statereader = stateinfocalculator.StateReaderEngine(handdoc)
            allstate = statereader.getallstate(turn)
            allaction = statereader.m_handsinfo.getspecificturnrealbetdata(turn)
            # 遍历一个牌局中的所有state
            for curstate, curaction in zip(allstate,allaction):
                actionpos, action, value = curaction
                similar = state.similar(curstate)
                actiondis.addaction(action, self.similarweightfunction(similar))
        return actiondis

    # state相似度权值计算公式
    def similarweightfunction(self, similar):
        pass
        return numpy.exp((similar - 1)*20)

    # handspower相似度权值计算公式
    def similarhpfunction(self, similar):
        pass
        return numpy.exp(-1.6 * similar)

    # 根据某一手特定的牌进行强化学习
    def reinlearning(self, targetstate, targethp, targetaction, fullactiondis, state):
        statesimilar = targetstate - state
        statesimilarweight = self.similarweightfunction(statesimilar)
        for hp in fullactiondis.m_actiondisdata.keys():
            hpsimilar = targethp - hp
            fullactiondis.addaction(hp, targetaction, self.similarhpfunction(hpsimilar) * statesimilarweight)

if __name__ == "__main__":
    import time
    start = time.time()
    print "start:",start
    ssc = StateStrategyCalculator(None)
    ssc.testcal()
    print "elapsed:",time.time() - start