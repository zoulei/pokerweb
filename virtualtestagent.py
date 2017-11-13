from game import DealerFromHistory
from handsengine import HandsInfo
import Constant
import copy
from handsdistribution import HandsDisQuality
from rullbasedagent import HonestAgent
from TraverseHands import TraverseValidHands

class VirtualTestAgent:
    def __init__(self, dealer, pokeragentlist):
        self.m_dealer = dealer
        self.m_pokeragentlist = pokeragentlist
        self.m_handsengine = self.m_dealer.m_handsengine

        self.m_testdis = HandsDisQuality()
        self.m_testEV = 0

    def test(self):
        # execute all history action
        turncount = self.m_handsengine.getturncount()
        for turnidx in xrange(1, turncount+1):
            curturndata = self.m_handsengine.getspecificturnbetdata(turnidx)
            for action, value in curturndata:
                self.m_pokeragentlist[self.m_handsengine.m_cumuinfo.m_nextplayer].act(action, value)

        # get real payoff
        self.m_handsengine.m_cumuinfo.calpayoff()
        self.m_realpayoff = copy.deepcopy(self.m_handsengine.m_payofflist)

        # remove winner information
        privatecardinfo = self.m_handsengine.getprivatecardinfo()
        for idx in xrange(len(privatecardinfo)):
            privatecardinfo[idx][1] = 0

        # test each agent, the result for each agent is a distribution of hand and EV
        for agent in self.m_pokeragentlist:
            self.testagent(agent)

    def testposhand(self, pos, hand):
        realpos = self.m_handsengine.getrealpos(pos)
        privatecardinfo = self.m_handsengine.getprivatecardinfo()
        realhand = copy.deepcopy(privatecardinfo[realpos - 1][0])

        # replace hands with virtual hands and calculate payoff
        cards = hand.get()
        privatecardinfo[realpos - 1][0] = [[cards[0].symbol + 1,cards[0].value],[cards[1].symbol + 1,cards[1].value]]
        self.m_handsengine.m_cumuinfo.calpayoff()
        payoff = self.m_handsengine.m_cumuinfo.m_payofflist[pos]

        # get back private hand data
        privatecardinfo[realpos - 1][0] = realhand

        return payoff

    def testagent(self,agent):
        self.m_testdis += HandsDisQuality(agent.m_distribution)
        if self.m_handsengine.m_inpoolstate[agent.m_pos] == 0:
            # this player has fold
            self.m_testEV += self.m_realpayoff[agent.m_pos]
        else:
            for hand, value in agent.m_distribution.items():
                if value == 0:
                    continue
                self.m_testEV += self.testposhand(agent.m_pos, hand) * value

class TestPayoff(TraverseValidHands):
    def filter(self, handsinfo):
        if handsinfo.get("payoff",None) is None:
            return True
        return TraverseValidHands.filter(self,handsinfo)

    def mainfunc(self, handsinfo):
        dealer = DealerFromHistory(handsinfo)
        agentlist = [None] * 10
        quantity = HandsInfo(handsinfo).getplayerquantity()
        for pos in range(1,quantity - 2 + 1) + [8,9]:
            agentlist[pos] = HonestAgent(dealer,pos)
        testagent = VirtualTestAgent(dealer, agentlist)
        testagent.test()
        print handsinfo["_id"]
        print testagent.m_testEV
        print testagent.m_testdis.calequalquality()
        print testagent.m_testdis.calquality()
        raise

if __name__ == "__main__":
    TestPayoff(Constant.HANDSDB,Constant.TJHANDSCLT,handsid="",step=1000).traverse()