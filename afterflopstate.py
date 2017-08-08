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

class statekey:
    def __init__(self):
        self.m_key = ""

    def addpreflopstate(self, preflopstate):
        pass

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

        newplayerrange = [0] * 10
        # print playerrange
        for idx,state in enumerate(self.m_cumuinfo.m_inpoolstate):
            if state == 0:
                continue
            ownpos = self.m_cumuinfo.getrelativepos(idx)
            newplayerrange[ownpos] = playerrange[idx]
        # print "raiser:",raiser
        self.m_preflopstate = {
            "remain"    :   remain,
            # raiser is based on the position of the state right after preflop
            "raiser"    :   self.m_cumuinfo.getrelativepos(raiser),
            "pot"       :   pot,
            "allin"     :   allin,
            "betlevel"  :   betlevel,
            "range"     :   newplayerrange,
            "board"     :   self.getboard()[:3]
        }

    def calflopstate(self):
        self.calspecificturnstate(2)

    def calturnstate(self):
        self.calspecificturnstate(3)

    def calriverstate(self):
        self.calspecificturnstate(4)

    def calspecificturnstate(self, round):
        if round == 1:
            self.calpreflopstate()
            return

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

            # attack is only used for after flop's state
            "attack"    :   curturnstate.get("attack",0),
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

    def getcurrentstatekey(self):
        if self.m_cumuinfo.m_curturn == 1 and not self.m_cumuinfo.m_curturnover:
            # preflop
            return


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

def calpreflopgeneralstatemain():
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{})
    doclen =  result.count()

    iternum = doclen / 10000 + 1
    for idx in xrange(iternum):
        calpreflopgeneralstatemain_(idx)

def calpreflopgeneralstatemain_(idx):
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{})
    # result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,
    #                         {"_id":"35357006093039820170308221515"})
    # idx = 0

    doclist = []
    cnt = 0
    for handsinfo in result:
        cnt  += 1
        if cnt < idx * 10000:
            continue

        if cnt >= (idx+1) * 10000:
            break

        if cnt % 1000 == 0:
            print cnt
        doclist.append(handsinfo)

    for handsinfo in doclist:
        try:
            afterstateinformation = afterflopstate(handsinfo)
            afterstateinformation.calspecificturnstate(1)
            handsinfo[Constant.PREFLOPGENERALSTATE] = afterstateinformation.getspecificturnstate(1)

            DBOperater.ReplaceOne(Constant.HANDSDB,Constant.TJHANDSCLT,{"_id":handsinfo["_id"]},handsinfo)
        except:
            print handsinfo["_id"]
            raise

def tongjipreflopgeneralstate():
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{})

    prefloptjinfo = {}
    prefloptjinfoallin = {}
    solotjinfo = {}
    sumhands = 0
    for handsinfo in result:
        preflopgeneralstate = handsinfo[Constant.PREFLOPGENERALSTATE]
        remain = preflopgeneralstate["remain"]
        raiser = preflopgeneralstate["raiser"]
        betlevel = preflopgeneralstate["betlevel"]
        allin = preflopgeneralstate["allin"]
        total = remain + allin
        sumhands += 1
        if allin > 0:
            continue
        if remain not in prefloptjinfo:
            prefloptjinfo[remain] = 0
        prefloptjinfo[remain] += 1

        if total not in prefloptjinfoallin:
            prefloptjinfoallin[total] = 0
        prefloptjinfoallin[total] += 1

        if total == 2 and allin == 0:
            if raiser not in solotjinfo:
                solotjinfo[raiser] = set()
            if betlevel == 5:
                print handsinfo["_id"]
            solotjinfo[raiser].add(betlevel)
    print "total : ",sumhands

    print "preflop allin : ", (sumhands - sum(prefloptjinfo.values()) ) * 1.0 / sumhands

    print "remain : ",sum(prefloptjinfo.values())
    handsinfocommon.pp.pprint(prefloptjinfo)

    for key in prefloptjinfoallin.keys():
        prefloptjinfoallin[key] = prefloptjinfoallin[key] * 1.0 / sumhands
    print "remain all : "
    handsinfocommon.pp.pprint(prefloptjinfoallin)

    print "solo : "
    handsinfocommon.pp.pprint(solotjinfo)

if __name__ == "__main__":
    # test()
    # calpreflopgeneralstatemain()
    tongjipreflopgeneralstate()