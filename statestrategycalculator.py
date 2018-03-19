#-*- coding:utf-8 -*-
# 计算牌局数据中的state的完整行动分布
from Constant import *
import DBOperater
import stateinfocalculator
import handspower

# 行为分布, 包括各种行动的概率, 包括check, call, raise三种
class ActionDis:
    def __init__(self):
        self.m_actiondis = {
            FOLD  :   0.0,
            CHECK :   0.0,
            CALL  :   0.0,
            RAISE :   0.0,
        }

    def addaction(self, action, rate):
        self.m_actiondis[action] += rate

    def normalize(self):
        total = sum(self.m_actiondis.values())
        for v in self.m_actiondis.keys():
            self.m_actiondis[v] /= total

    def __getitem__(self, item):
        return self.m_actiondis[item]

# 完整行为分布
class FullActionDis:
    def __init__(self, checkavailable=False):
        self.m_marker = handspower.RandomMarker()
        self.m_checkavailable = checkavailable
        if self.m_checkavailable:
            self.m_defend = CHECK
        else:
            self.m_defend = CALL
        self.initdata()

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

# 该类基于一个牌局库来计算给定牌局的所有state的完整行动分布
class StateStrategyCalculator:
    def __init__(self,targetdoc,db=HANDSDB,clt=HANDSCLT,querystr=None):
        self.m_targetdoc = targetdoc
        self.m_db = db
        self.m_clt = clt
        if querystr is None:
            self.m_querystr = {}
        else:
            self.m_querystr = querystr

    # 计算某个state的完整行为分布
    def calstrategyforspecificstate(self, state):
        # 统计行为分布
        actiondis = self.getactiondisofsimilarstate(state)
        # 根据统计行为分布获取一个初始完整行为分布
        fullactiondis = FullActionDis(state.ischeckavailable())
        fullactiondis.initfulldis(actiondis)

        # 根据秀牌数据进行强化学习


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

    # 根据某一手特定的牌进行强化学习
    def reinlearning(self, state, rangeobj, action):
        pass

