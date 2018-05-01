#-*- coding:utf-8 -*-
from hunlgame import Poker,HandsRange
import hunlgame
import copy
import handsinfocommon
from handsrank import cards2key, getengine
from handsrank import HandsRankEngine

class WinrateCalculator:
    # rangestate is a object of class handsdistribution.RangeState
    def __init__(self, rangestate, equalvalue = 0.5):
        self.m_rangestate = rangestate
        self.m_board = rangestate.m_board
        self.m_myhands = rangestate.m_myhands
        self.m_ophands = rangestate.m_ophands
        self.m_equalvalue = equalvalue
        self.m_pokerengine = Poker()
        self.m_valid = True
        self.checkparavalid()

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
            keylist = ophands.getvalidhands()
            rankengine = HandsRankEngine(myhand,keylist,board)
            winrate = 0
            if rankengine.getlose() == 0:
                winrate = 1
            else:
                for hand in rankengine.getwinhands():
                    winrate += ophands[hand]
                for hand in rankengine.gettiehands():
                    winrate += ophands[hand] * self.m_equalvalue
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
        handrangeobj = HandsRange()
        allcards = handrangeobj._generateallcard()
        for card in self.m_board+list(self.m_myhands.get()):
            try:
                allcards.remove(card)
            except:
                print "my hands conflict with the board cards"
                print hunlgame.board2str(self.m_board)
                print hunlgame.board2str(self.m_myhands.get())
                raise

        nextturnwinratelist = []
        for card in allcards:
            board = copy.deepcopy(self.m_board)
            board.append(card)
            myhands = copy.deepcopy(self.m_myhands)
            ophands = copy.deepcopy(self.m_ophands)
            if not self.ophandsremovecard(ophands,card):
                continue
            # winrate = self.calmywinrate_(board,myhands,ophands)
            winrate = self.calmywinrate__(board, myhands, ophands)
            if winrate == -1:
                continue

            nextturnwinratelist.append([board, winrate])

        nextturnwinratelist.sort(key = lambda v:v[1])
        return nextturnwinratelist
