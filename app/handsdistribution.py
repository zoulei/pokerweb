#-*- coding:utf-8 -*-
from math import pow
from privatecardsstrength import PrivateHandRank
from hunlgame import HandsRange
import copy
import hunlgame

class HandsDisQuality:
    def __init__(self,dis = None):
        if dis is None:
            self.m_handsdis = {}
        elif isinstance(dis, list):
            self.m_handsdis = dict(zip(dis,[1]*len(dis)))
            self.normalize()
        else:
            self.m_handsdis = dis

    def __add__(self, other):
        for key in self.m_handsdis.keys():
            self.m_handsdis[key] += other.m_handsdis.get(key,0)
        for key in other.m_handsdis.keys():
            if key in self.m_handsdis:
                continue
            self.m_handsdis[key] = other.m_handsdis[key]
        return self

    def __getitem__(self, key):
        return self.m_handsdis.get(key, 0)

    def __len__(self):
        return len(self.m_handsdis)

    def getvalidhands(self):
        return self.m_handsdis.keys()

    def gethands(self):
        return self.m_handsdis.keys()

    def items(self):
        return self.m_handsdis.items()

    def removecard(self,card):
        handslist = self.m_handsdis.keys()
        for hand in handslist:
            if card in hand.get():
                del self.m_handsdis[hand]


    # make the sum of probability be 1
    # 成功归一化反回True
    # 如果手牌分布中一手牌都没有的话,返回False
    def normalize(self):
        total = sum(self.m_handsdis.values()) * 1.0
        if total == 0:
            return False
        for key in self.m_handsdis.keys():
            self.m_handsdis[key] /= total
        return True

    def calquality(self):
        quantity = 0
        handrankengine = PrivateHandRank()
        for hand, value in self.m_handsdis.items():
            quantity += self.f(handrankengine.getrank(hand),value )
        return quantity

    def calequalquality(self):
        handrankengine = PrivateHandRank()
        handrangeobj = HandsRange()
        handrangeobj.addFullRange()
        quantity = 0
        prob = 1.0/ 1326
        for hand in handrangeobj.get():
            quantity += self.f(handrankengine.getrank(hand),prob )
        return quantity

    def f(self, rank, value):
        return pow(rank, 2) * value

    def printdata(self):
        dislist = self.m_handsdis.items()
        dislist.sort(key=lambda v:v[1],reverse=True)
        dislist = [v for v in dislist if v[1] != 0]
        print "=======start print hands distribution========="
        for hand, value in dislist:
            print hand, "\t",value
        print "=======stop print hands distribution========="

class RangeState:
    # ophands 是一个 handsdistribution.HandsDisQuality 实例 的列表或者单个该对象
    def __init__(self, board, myhands, ophands):
        self.m_myhands = myhands
        self.m_board = board
        if isinstance(ophands,list):
            self.m_ophands = ophands
        else:
            self.m_ophands = [ophands,]
        self.m_valid = True
        # self.checkparavalid()

    # 检查一下输入的数据是否有错误,主要是看我的手牌和牌面上的牌是否有重复,
    # 并检查对手的手牌中除掉牌面上的牌之后是否还有剩余的手牌,如果除掉无效的手牌之后对手的range为空胜率也没法计算
    def checkparavalid(self):
        for card in self.m_board:
            if card in self.m_myhands.get():
                # 我的手牌与牌面冲突了
                self.m_valid = False
                return False
        for card in self.m_board + self.m_myhands.get():
            for handsdis in self.m_ophands:
                handsdis.removecard(card)
        for handsdis in self.m_ophands:
            if not handsdis.normalize():
                # 有对手的range为空了
                self.m_valid = False
                return False
        return True

    # 假如再发一张牌对手的range的变化情况,
    # 如果这张牌与我的手牌冲突,返回False,如果这张牌和已有的牌面冲突,返回False,如果这张牌会导致对手的range为空,返回False
    # 否则返回假如发出这张牌,对手的新range
    def newboardcard(self,card):
        if card in self.m_myhands.get() + self.m_board:
            return False
        newophands = copy.deepcopy(self.m_ophands)
        for handsdis in newophands:
            handsdis.removecard(card)
            if not handsdis.normalize():
                return False
        return True

    def __nonzero__(self):
        # print "called"
        return self.m_valid