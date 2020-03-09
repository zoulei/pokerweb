from hunlgame import HandsRange
from privatecardsstrength import PrivateHandRank
import handsinfocommon
import hunlgame
from math import pow

class HonestAgent:
    # game acts like a dealer
    # pos is from 1-9, 9 is sb, 8 is bb
    def __init__(self, dealer, pos = 0, myhand=None):
        self.m_dealer = dealer
        self.m_pos = pos
        self.m_myhand = myhand

        self.m_checkavailable = False
        self.m_winrateengine = None
        self.m_distribution = {}

        self.m_lastactionturn = 0
        self.initdistribution()

    # init my hands distribution based on my strategy
    # this distribution can be used to determine my hand
    # based on my strategy and action.
    def initdistribution(self):
        handrangeobj = HandsRange()
        handrangeobj.addFullRange()
        handslist = handrangeobj.get()
        self.m_distribution = dict(zip(handslist, [1.0/len(handslist)]*len(handslist)))
        # avg prob is 0.00075414

    # update my hands distribution based on new public card
    def updatedistributionbyboard(self):
        # print "updatedisby board:",self.m_pos
        board = self.m_dealer.getboard()
        # print "curturn:",self.m_dealer.getcurrentturn()
        # print "board:"
        # for card in board:
        #     print card
        # eliminate hands that is impossible according to public card
        if self.m_lastactionturn != self.m_dealer.getcurrentturn():
            if self.m_dealer.getcurrentturn() == 2:
                # flop
                for hand in self.m_distribution.keys():
                    for publiccard in board:
                        if publiccard in hand.get():
                            self.m_distribution[hand] = 0
                            break
            elif self.m_dealer.getcurrentturn() > 2:
                # turn and river
                for hand in self.m_distribution.keys():
                    if board[-1] in hand.get():
                        self.m_distribution[hand] = 0

        # normalize probability
        rate = 1.0 / sum(self.m_distribution.values())
        for hand in self.m_distribution.keys():
            self.m_distribution[hand] *= rate
        # if self.m_pos == 1:
        #     self.printdata()
        #     raw_input()

    # update distribution based on my action
    # action is 0 : fold, 1 : call, 2 : raise
    def updatedistributionbyaction(self, action, value):
        # print "updatedisby action:",self.m_pos
        if action in [2,4.2]:
            action = 2
        elif action == 1:
            action = 0
        elif action in [3,6,4.3]:
            action = 1
        elif action == 12:
            return
        mother = 0
        responsedata = {}
        # print "dis:"
        # handsinfocommon.pp.pprint(self.m_distribution)
        for hand,prob in self.m_distribution.items():
            if prob == 0:
                continue
            responsedata[hand] = self.getresponse(hand)
            mother += responsedata[hand][action] * prob

        for hand,prob in self.m_distribution.items():
            if prob == 0:
                continue
            self.m_distribution[hand] = prob * responsedata[hand][action] / mother
            # print hand,self.m_distribution[hand]
            # print responsedata[hand],prob,mother
            # raw_input()
        # if self.m_pos == 1:
        #     self.printdata()
        #     raw_input()

    # make action
    def act(self, action, value):
        self.updatedistributionbyboard()
        self.m_lastactionturn = self.m_dealer.getcurrentturn()
        self.m_checkavaible = self.m_dealer.checkavailable()
        self.m_dealer.updateaction(action,value)
        # print "action, value:",action,value
        # print self.m_dealer.m_handsengine.m_cumuinfo.m_curturn
        self.updatedistributionbyaction(self.m_dealer.m_handsengine.m_cumuinfo.m_lastaction, value)

    # ask dealer for hand
    def askforhand(self):
        hand = self.m_dealer.distributehand(self.m_pos)
        self.sethand(hand)

    # set my hand
    def sethand(self,hand):
        self.m_myhand = hand

    # my response under current game state if my hand is virtualhand
    # if virtualhand is not given, then use my real hand
    # return tuple, represents (fold, call or check, raise)
    def getresponse(self, virtualhand = None):
        if virtualhand is None:
            virtualhand = self.m_myhand

        if self.m_dealer.getcurrentturn() > 1:
            # try:
            self.m_winrateengine = hunlgame.FPWinrateEngine(self.m_dealer.getturnboard(self.m_dealer.m_handsengine.m_cumuinfo.m_curturn), virtualhand)
            winrate = self.m_winrateengine.calmywinrate()
            isnuts = self.m_winrateengine.isnuts()
        else:
            handrankengine = PrivateHandRank()
            rank = handrankengine.getrank(virtualhand)
            winhand = rank - 1
            if virtualhand.suti():
                tiehand = 3
            elif virtualhand.pair():
                tiehand = 5
            else:
                tiehand = 11
            losehand = 1326 - winhand - tiehand - 1
            winrate = (tiehand * 0.5 + winhand) / 1325
            if rank > 1320:
                isnuts = True
            else:
                isnuts = False

        if isnuts:
            return (0,0,1)
        raiserate = pow(winrate,3)
        callrate = winrate - raiserate
        foldrate = 1 - winrate
        if self.m_checkavailable:
            return (0, foldrate + callrate, raiserate)
        else:
            return (foldrate,callrate, raiserate)

