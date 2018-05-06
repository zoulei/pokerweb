#-*- coding:utf-8 -*-
from hunlgame import Poker,HandsRange
import hunlgame
import copy
import handsinfocommon
from handsrank import cards2key, getengine
from handsrank import HandsRankEngine
from mytimer import Timer

timer = Timer()

class WinrateCalculator:
    # rangestate is a object of class handsdistribution.RangeState
    def __init__(self, rangestate, equalvalue = 0.5):
        self.m_rangestate = rangestate
        self.m_board = rangestate.m_board
        self.m_myhands = rangestate.m_myhands
        self.m_ophands = rangestate.m_ophands
        self.m_equalvalue = equalvalue
        timer.start("init poker")
        self.m_pokerengine = Poker()
        timer.stop("init poker")
        self.m_valid = True
        timer.start("checkparavalid")
        self.checkparavalid()
        timer.stop("checkparavalid")

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

    def calmywinrate__(self, board, myhand, ophandslist):
        if not self.m_valid:
            return -1
        totalwinrate = 1.0
        for ophands in ophandslist:
            timer.start("get valid hands")
            keylist = ophands.getvalidhands()
            timer.stop("get valid hands")
            timer.start("sort hands")
            rankengine = HandsRankEngine(myhand,keylist,board)
            timer.stop("sort hands")

            timer.start("sort hands info")
            winrate = 0
            if rankengine.getlose() != 0:
                for hand in rankengine.getwinhands():
                    winrate += ophands[hand]
                for hand in rankengine.gettiehands():
                    winrate += ophands[hand] * self.m_equalvalue
            else:
                winrate = 1
            timer.stop("sort hands info")
            totalwinrate *= winrate
        return totalwinrate

    def calmywinrate(self):
        return self.calmywinrate__(self.m_board,self.m_myhands,self.m_ophands)

    def ophandsremovecard(self,ophands,card):
        for handsdis in ophands:
            handsdis.removecard(card)
            if not handsdis.normalize():
                return False
        return True

    def calnextturnstackwinrate(self):
        timer.start("generate all card")
        handrangeobj = HandsRange()
        allcards = handrangeobj._generateallcard()
        timer.stop("generate all card")

        timer.start("clear all card")
        for card in self.m_board+list(self.m_myhands.get()):
            allcards.remove(card)
        timer.stop("clear all card")

        nextturnwinratelist = []
        for card in allcards:
            timer.start("copy hands")
            # board = copy.deepcopy(self.m_board)
            # board.append(card)
            # myhands = copy.deepcopy(self.m_myhands)
            ophands = copy.deepcopy(self.m_ophands)
            timer.stop("copy hands")
            timer.start("clear ophands")
            if not self.ophandsremovecard(ophands,card):
                continue
            timer.stop("clear ophands")
            timer.start("calwinrate")
            winrate = self.calmywinrate__(self.m_board + [card,], self.m_myhands, ophands)
            timer.stop("calwinrate")
            if winrate == -1:
                continue

            nextturnwinratelist.append([board, winrate])
        timer.start("next turn sort")
        nextturnwinratelist.sort(key = lambda v:v[1])
        timer.stop("next turn sort")
        return nextturnwinratelist
