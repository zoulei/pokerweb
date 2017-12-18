from handsengine import ReplayEngine
from TraverseHands import TraverseHands
import DBOperater
import Constant
import numpy

class AfterflopState:
    def __init__(self,stateinfo):
        self.m_stateinfo = stateinfo

    def similar(self, other):
        for attr in [Constant.ISOPENER,Constant.HASOPENER,Constant.RELATIVETOOPENER]:
            if self.m_stateinfo[attr] != other.m_stateinfo[attr]:
                return 0
        attrsimilar = []
        for attr,weight in [[Constant.RELATIVEPOS,200],]:
            cursimilar = 1 - (self.m_stateinfo[attr] - other.m_stateinfo[attr])
            attrsimilar.append([cursimilar,weight])
        for attr,maxima,weight in [[Constant.REMAINTOACT,0,50],[Constant.REMAINRAISER,0,50],[Constant.ODDS,10,100],
                            [Constant.POTSIZE,200,100],[Constant.INITIALPLAYERQUANTITY,0,100],
                            [Constant.RAISERSTACKVALUE,[7,3,3,2][self.m_stateinfo[Constant.TURN]-1],50],
                            [Constant.REMAINSTACKVALUE,[7,3,3,2][self.m_stateinfo[Constant.TURN]-1],50]]:
            maxvalue = max(self.m_stateinfo[attr],other.m_stateinfo[attr])
            if maxima == 0:
                maxima = maxvalue
            minvalue = min(self.m_stateinfo[attr],other.m_stateinfo[attr],maxima)
            maxvalue = min(maxvalue,maxima)
            cursimilar = (minvalue+1)/(maxvalue+1)
            attrsimilar.append([cursimilar,weight])
        for attr,k,maxima,weight in [[Constant.PREFLOPATTACKVALUE,4,3,200],[Constant.CURRENTATTACKVALUE,4,3,200],
                              [Constant.AFTERFLOPATTACKVALUE,4,3,200]]:
            myvalue = min(self.m_stateinfo[attr],3)
            othervalue = min(self.m_stateinfo[attr],3)
            cursimilar = numpy.exp(-1 * k * abs(myvalue-othervalue))
            attrsimilar.append([cursimilar,weight])
        similar = 1.0 * sum([v[0]*v[1] for v in attrsimilar]) / sum([v[1] for v in attrsimilar])
        return similar

class StateCalculator(ReplayEngine):
    def __init__(self,handsinfo):
        ReplayEngine.__init__(self,handsinfo)
        self.initstaterecorder()

    def initstaterecorder(self):
        self.m_preflopstate = []
        self.m_flopstate = []
        self.m_turnstate = []
        self.m_riverstate = []

    #True is, False not
    def isopener(self,pos):
        if self.getpreflopinfomation()["raiser"] == pos:
            return True
        return False

    # True has, False not
    def hasopener(self):
        if self.getpreflopinfomation()["raiser"] != 0:
            return True
        return False

    # 1 means the best position, 0 means the worst position
    def relativepos(self,pos):
        total = self.m_remainplayer - self.m_allinplayer
        step = 1.0 / (total - 1)
        initial = - step
        for inpoolpos,state in enumerate(self.m_inpoolstate):
            if state == 1:
                initial += step
            if inpoolpos == pos:
                return 1 - initial

    # player quantity that still need to act
    def playerquantitytoact(self):
        total = 0
        poslist = self.getposlist()
        playeridx = poslist.index(self.m_nextplayer)
        if self.m_raiser == 0:
            for pos in poslist[playeridx + 1:]:
                if self.m_inpoolstate[pos] == 1:
                    total += 1
            return total
        for pos in poslist[playeridx + 1:] + poslist[:playeridx]:
            if pos == self.m_raiser:
                return total
            elif pos == self.m_fakeraiser:
                return 0
            if self.m_inpoolstate[pos] == 1:
                total += 1
        return total
        # 1 2 3 4(r) 5 6 7(f) 8 9

    # player quantitiy that has made action
    def playerquantityacted(self):
        if self.m_circle > 1:
            return self.m_remainplayer - self.m_allinplayer - 1
        poslist= self.getposlist()
        playeridx = poslist.index(self.m_nextplayer)
        total = 0
        for pos in poslist[:playeridx]:
            if self.m_inpoolstate[pos] == 1:
                total += 1
        return total

    # player quantity that make raise or call raise
    def raiserquantity(self):
        total = 0
        if self.m_raiser != 0:
            poslist = range(self.m_raiser,0,-1) + range(9, self.m_raiser,-1)
        else:
            poslist = self.getposlist()
        for pos in poslist:
            if pos == self.m_nextplayer:
                break
            if self.m_inpoolstate[pos] == 0:
                continue
            total += 1
        return total

    # raiser's stack pot ratio
    def getraiserstackpotratio(self):
        myneedtobet = self.m_betvalue - self.m_bethistory.get(self.m_nextplayer,0)
        raisermaxstack = 0
        realpot = self.m_pot + myneedtobet
        if self.m_raiser != 0:
            poslist = range(self.m_raiser,0,-1) + range(9, self.m_raiser,-1)
        else:
            poslist = self.getposlist()
        for pos in poslist:
            if pos == self.m_nextplayer:
                break
            if self.m_inpoolstate[pos] == 0:
                continue
            if self.m_stacksize[pos] > raisermaxstack:
                raisermaxstack = self.m_stacksize[pos]
        if self.m_stacksize[self.m_nextplayer] - myneedtobet < raisermaxstack:
            raisermaxstack = self.m_stacksize[self.m_nextplayer] - myneedtobet
        if raisermaxstack < 0:
            raisermaxstack = 0
        return raisermaxstack * 1.0 / realpot

    # players need to bet stack pot ratio
    def getneedtobetstackratio(self):
        myneedtobet = self.m_betvalue - self.m_bethistory.get(self.m_nextplayer,0)
        realpot = self.m_pot + myneedtobet
        targetmaxstack = []
        if self.m_raiser != 0:
            poslist = range(self.m_nextplayer -1,0,-1) + range(9, self.m_nextplayer - 1,-1)
            posidx = poslist.index(self.m_raiser)
        else:
            poslist = self.getposlist()[::-1]
            posidx = poslist.index(self.m_nextplayer)
        for pos in poslist[:posidx]:
            if self.m_inpoolstate[pos] != 1:
                continue
            targetneedtobet = self.m_betvalue - self.m_bethistory.get(pos,0)
            targetrealpot = realpot + targetneedtobet
            targetstacksize = min(self.m_stacksize[pos]-targetneedtobet,self.m_stacksize[self.m_nextplayer]-myneedtobet)
            if targetstacksize < 0:
                targetstacksize = 0
            targetmaxstack.append(targetstacksize * 1.0 / targetrealpot)
        targetmaxstack.sort()
        return targetmaxstack

    def initalplayerquantity(self,turn):
        if turn == 1:
            return self.m_handsinfo.getplayerquantity()
        if turn == 2:
            info = self.getpreflopinfomation()
        elif turn == 3:
            info = self.getflopinformation()
        elif turn == 4:
            info = self.getturninformation()
        return info["remain"] + info["allin"]

    def updatecumuinfo(self,round,actionidx):
        statedata = {}
        statedata[Constant.ISOPENER] = self.getpreflopinfomation()["raiser"] == self.m_nextplayer
        statedata[Constant.HASOPENER] = self.getpreflopinfomation()["raiser"] != 0
        statedata[Constant.RELATIVETOOPENER] = self.getrelativepostoopener(self.m_nextplayer)
        statedata[Constant.TURN] = self.m_curturn
        statedata[Constant.RELATIVEPOS] = self.relativepos(self.m_nextplayer)
        statedata[Constant.REMAINTOACT] = self.playerquantitytoact()
        statedata[Constant.REMAINRAISER] = self.raiserquantity()
        statedata[Constant.POTSIZE] = self.m_pot
        statedata[Constant.INITIALPLAYERQUANTITY] = self.initalplayerquantity(round)
        statedata[Constant.RAISERSTACKVALUE] = self.getraiserstackpotratio()
        statedata[Constant.REMAINSTACKVALUE] = self.getneedtobetstackratio()
        statedata[Constant.CURRENTATTACKVALUE] = self.m_attack
        if round > 1:
            statedata[Constant.PREFLOPATTACKVALUE] = self.getpreflopinfomation()["newattack"]
            statedata[Constant.AFTERFLOPATTACKVALUE] = self.m_totalattack - self.getpreflopinfomation()["newattack"]
        ReplayEngine.updatecumuinfo(self,round,actionidx)
        statedata[Constant.ODDS] = self.m_laststate["odds"]
        [self.m_preflopstate,self.m_flopstate,self.m_turnstate,self.m_riverstate][round-1].append(statedata)

    def savestatedata(self):
        targetdoc = self.m_handsinfo.m_handsinfo["data"]
        targetdoc["STATEINFO"] = {}
        targetdoc = targetdoc["STATEINFO"]
        targetdoc["PREFLOPSTATE"] = self.m_preflopstate
        if self.m_flopstate:
            targetdoc["FLOPSTATE"] = self.m_flopstate
        if self.m_turnstate:
            targetdoc["TURNSTATE"] = self.m_turnstate
        if self.m_riverstate:
            targetdoc["RIVERSTATE"] = self.m_riverstate
        DBOperater.ReplaceOne(Constant.HANDSDB,Constant.STATEINFOHANDSCLT,{"_id":self.m_handsinfo.getid()},self.m_handsinfo.m_handsinfo,True)

def mainfunc(handsinfo):
    cal = StateCalculator(handsinfo)
    cal.traversealldata()
    cal.savestatedata()

if __name__ == "__main__":
    TraverseHands(Constant.HANDSDB,Constant.HANDSCLT,sync=True,func=mainfunc,handsid="2017-12-09 23:02:37 88").traverse()