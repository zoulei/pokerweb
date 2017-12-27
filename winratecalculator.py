from hunlgame import Poker,HandsRange
import hunlgame
import copy
import handsinfocommon

class WinrateCalculator:
    def __init__(self, board, myhand, ophands, equalvalue = 0.5):
        self.m_board = board
        self.m_myhands = myhand
        if isinstance(ophands,list):
            self.m_ophands = ophands
        else:
            self.m_ophands = [ophands,]
        self.m_equalvalue = equalvalue
        self.m_pokerengine = Poker()

    def calmywinrate__(self, board, myhand, ophandslist):
        totalwinrate = 1.0
        for ophands in ophandslist:
            keylist = ophands.getvalidhands()
            fullhand = [myhand,] + list(keylist)
            # handinfo = []
            # for hand in fullhand:
            #     handinfo.append(hand.get())
            results = hunlgame.sorthands_(board, [v.get() for v in fullhand])
            resultkeylist = results.keys()
            resultkeylist.sort()
            maxkey = resultkeylist[-1]
            if 0 in results[maxkey]:
                return 1
            winrate = 0
            for idx in resultkeylist:
                curhandidxlist = results[idx]
                if 0 in curhandidxlist:
                    for handidx in curhandidxlist:
                        if handidx == 0:
                            continue
                        winrate += ophands[fullhand[handidx]] * self.m_equalvalue
                    break
                else:
                    for handidx in curhandidxlist:
                        winrate += ophands[fullhand[handidx]]
            totalwinrate *= winrate
        return totalwinrate

    def calmywinrate_(self, board, myhand, ophands):
        for card in board:
            if card in myhand.get():
                return -1
            for handdis in ophands:
                handdis.removecard(card)
        for card in myhand.get():
            for handdis in ophands:
                handdis.removecard(card)
        for handdis in ophands:
            handdis.normalize()

        curwinrate = self.calmywinrate__(board, myhand, copy.deepcopy(ophands))
        return curwinrate

    def calmywinrate(self):
        myhands = copy.deepcopy(self.m_myhands)
        ophands = copy.deepcopy(self.m_ophands)
        board = copy.deepcopy(self.m_board)
        return self.calmywinrate_(board,myhands,ophands)

    def calnextturnstackwinrate(self):
        handrangeobj = HandsRange()
        allcards = handrangeobj._generateallcard()
        for card in self.m_board+list(self.m_myhands.get()):
            allcards.remove(card)

        nextturnwinratelist = []
        for card in allcards:
            board = copy.deepcopy(self.m_board)
            board.append(card)
            myhands = copy.deepcopy(self.m_myhands)
            ophands = copy.deepcopy(self.m_ophands)
            winrate = self.calmywinrate_(board,myhands,ophands)
            if winrate == -1:
                continue

            nextturnwinratelist.append([board, winrate])

        nextturnwinratelist.sort(key = lambda v:v[1])
        return nextturnwinratelist
