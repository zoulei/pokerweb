# this file is not completed yet.
# tjafterflopstate function is not completed yet, I've copied
# the code from tongjihandsinfo and prefloprange. And I've calculated
# the realtime size of pot. But many code need to be written calfully
import Constant
import handsinfocommon
import DBOperater

from tongjihandsinfo import *
from handsengine import HandsInfo

HEADER = Constant.TAB.join(["range","relativepos","playernumber",
                            "flopattack","turnattack","riverattack",
                            "boardvalue","handsstrength","buystrength",
                            "action"])

class afterflopstate(HandsInfo):
    def __init__(self, handsdata):
        HandsInfo.__init__(self,handsdata)

    def writeheader(self):
        file = open(Constant.AFTERFLOPSTATEHEADER,"w")
        file.write(HEADER)
        file.close()

    def calpreflopstate(self):
        if self.m_cumuinfo.m_curturn > 1:
            self.reset()
        self.traversepreflop()

        preflopinfor = self.getpreflopinformation()
        playerrange = preflopinfor["range"]
        raiser = preflopinfor["raiser"]
        betlevel = preflopinfor["betlevel"]

        statistics = self.m_cumuinfo.calstatistics()
        remain = statistics["remain"]
        allin = statistics["allin"]
        pot = statistics["pot"]

        newplayerrange = [-1] * 10
        print playerrange
        for idx,state in enumerate(self.m_cumuinfo.m_inpoolstate):
            if state == 0:
                continue
            ownpos = self.m_cumuinfo.getrelativepos(idx)
            newplayerrange[ownpos] = playerrange[idx]
        print "raiser:",raiser
        self.m_preflopstate = {
            "remain"    :   remain,
            # raiser is based on the position of theß state right after preflop
            "raiser"    :   self.m_cumuinfo.getrelativepos(raiser),
            "pot"       :   pot,
            "allin"     :   allin,
            "betlevel"  :   betlevel,
            "range"     :   newplayerrange,
            "board"     :   self.getboard()[:3]
        }

        # for idx,state in enumerate(self.m_cumuinfo.m_inpoolstate):
        #     if state != 1:
        #         continue
        #     ownpos = self.m_cumuinfo.getrelativepos(idx)
        #     writeinformation = {
        #         "remain"    :   remain,
        #         "ownpos"    :   ownpos,
        #         "raiser"     :   self.m_cumuinfo.getrelativepos(raiser),
        #         # "israiser"  :   1,
        #         # "relativepos"   :   1,
        #         "pot"       :   pot,
        #         "allin"     :   allin,
        #         "betlevel"  :   betlevel,
        #         "range"     :   newplayerrange,
        #     }

    def calflopstate(self):
        self.calspecificturnstate(2)

    def calturnstate(self):
        self.calspecificturnstate(3)

    def calriverstate(self):
        self.calspecificturnstate(4)

    def calspecificturnstate(self, round):
        if self.m_cumuinfo.m_curturn > round:
            self.reset()
        self.traversespecificturn(round)
        statistics = self.m_cumuinfo.calstatistics()
        curturnstate = self.m_cumuinfo.getspecificturninformation(round)
        targetturnstate = {
            "remain"    :   statistics["remain"],
            "pot"       :   statistics["pot"],
            "allin"     :   statistics["allin"],
            "board"     :   self.getboard()[:3 + round - 1],

            # for after flop state, raiser is based on the position information of previous turn.
            "raiser"    :   self.m_cumuinfo.getrelativepos(curturnstate["raiser"]),
            "attack"    :   curturnstate["attack"],
        }
        if round == 2:
            self.m_flopstate = targetturnstate
        elif round == 3:
            self.m_turnstate = targetturnstate
        elif round == 4:
            self.m_riverstate = targetturnstate
        else:
            raise

    def calallturnstate(self):
        self.calpreflopstate()
        for idx in xrange(2,self.getturncount()+1):
            self.calspecificturnstate(idx)

    def getspecificturnstate(self, round):
        if round == 1:
            return self.m_preflopstate
        elif round == 2:
            return self.m_flopstate
        elif round == 3:
            return self.m_turnstate
        elif round == 4:
            return self.m_riverstate

def test():
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{})
    for rawdata in result:
        print rawdata["_id"]
        afterstateinformation = afterflopstate(rawdata)
        turncount = afterstateinformation.getturncount()
        afterstateinformation.calallturnstate()

        for idx in xrange(1,turncount + 1):
            handsinfocommon.pp.pprint(afterstateinformation.getspecificturnstate(idx))

        raw_input()

if __name__ == "__main__":
    test()
