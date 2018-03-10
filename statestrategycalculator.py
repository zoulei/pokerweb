#-*- coding:utf-8 -*-
# 计算牌局数据中的state的完整行动分布
from Constant import *
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
        pass

    # 统计相似state下的行为分布
    def getactiondisofsimilarstate(self, state):
        pass

