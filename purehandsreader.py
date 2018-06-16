# -*- coding:utf-8 -*-
from stateinfocalculator import *
import hunlgame

# 该类仅读取牌局doc中的数据，不主动进行计算，计算的部分需要用户主动调用
class PureHandsReader:
    TURNSTR = ["PREFLOP", "FLOP", "TURN", "RIVER"]
    def __init__(self, handsinfo):
        self.m_handsinfo = handsinfo

    # 读取指定轮的所有state原始信息
    def getspecificturnstatedata(self,turn):
        return self.m_handsinfo["data"]["STATEINFO"].get(self.getturnstr(turn),[])

    # 读取指定轮第指定次行动时的state
    def getstate(self,turn, actionidx):
        return StateByExpert(self.getspecificturnstatedata(turn)[actionidx])

    # 读取指定轮的所有state
    def getallstate(self, turn):
        staterawinfo = self.m_handsinfo["data"]["STATEINFO"].get(self.getturnstr(turn),[])
        return [StateByExpert(v) for v in staterawinfo]

    def getprefloprange(self):
        return self.m_handsinfo["data"][Constant.PREFLOPRANGEDOC]

    def getpreflopinpoolstate(self):
        return self.m_handsinfo["data"][Constant.PREFLOPINPOOLSTATE]

    def getturncount(self):
        betdata = self.m_handsinfo["data"]["BETDATA"]
        turnidx = 0
        for turnstr in self.TURNSTR:
            if turnstr in betdata:
                turnidx += 1
            else:
                break
        return turnidx

    def getspecificturnrealbetdata(self, turnidx):
        turnstr = self.TURNSTR[turnidx - 1]
        return self.m_handsinfo["data"][Constant.REALBETDATA].get(turnstr,[])

    def initprivatehand(self):
        privateinfo = self.m_handsinfo["data"]["PVCARD"]
        self.m_privatehands = []
        for handstr in privateinfo:
            if handstr is not None:
                self.m_privatehands.append(hunlgame.generateHands(handstr))
            else:
                self.m_privatehands.append(None)

    def gethand(self, pos):
        return self.m_privatehands[pos]

    def initboard(self):
        boardstr = self.m_handsinfo["data"]["BOARD"]
        self.m_board = hunlgame.generateCards(boardstr)

    def getboardcard(self):
        return self.m_board

    def getturnstr(self,turn):
        return self.TURNSTR[turn - 1]

    def __getitem__(self, item):
        if item == "_id":
            return self.m_handsinfo["_id"]