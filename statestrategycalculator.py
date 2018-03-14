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
            "fold"  :   0.0,
            "check" :   0.0,
            "call"  :   0.0,
            "raise" :   0.0,
        }

    def addaction(self, action, rate):
        self.m_actiondis[action] += rate

    def normalize(self):
        total = sum(self.m_actiondis.values())
        for v in self.m_actiondis.keys():
            self.m_actiondis[v] /= total

# 完整行为分布
class FullActionDis:
    def __init__(self):
        self.m_marker = handspower.RandomMarker()

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
        actiondis = self.getactiondisofsimilarstate(state)
        initialdis = self.getinitialdis(actiondis)

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

    # 根据行为分布获取一个初始分布
    def getinitialdis(self, actiondis):
        pass

    # 根据某一手特定的牌进行强化学习
    def reinlearning(self, state, rangeobj, action):
        pass

