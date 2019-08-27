# -*- coding:utf-8 -*-
from handsengine import HandsInfo, ReplayEngine
from TraverseHands import TraverseHands, TraverseMultiplayerHands
import DBOperater
import Constant
import handsinfocommon
import handsinfoexception
from handcheck import LastAllinErrorChecker

class StackRepairer(HandsInfo):
    def __init__(self, handsinfo, db, clt):
        HandsInfo.__init__(self,handsinfo)
        self.m_db = db
        self.m_clt = clt

    def repairStack(self):
        self.m_handsinfo["repairstack"] = False
        self.traversealldata()
        DBOperater.ReplaceOne(self.m_db,self.m_clt,{"_id":self.m_handsinfo["_id"]},self.m_handsinfo)
        if self.m_handsinfo["repairstack"] == True:
            # handsinfocommon.pp.pprint(self.m_handsinfo)
            return True
        return False

    # traverse bet data and repair it if needed
    def traversealldata(self):
        turncount = self.getturncount()
        for turnnumber in xrange(1,turncount + 1):
            curturndata = self.getspecificturnbetdata(turnnumber)
            for idx in xrange(len(curturndata)):
                self.updatecumuinfo(turnnumber, idx)
                value = self.m_cumuinfo.m_stacksize[self.m_cumuinfo.m_lastplayer]

                if value < 0:
                    self.m_handsinfo["data"][0][3][self.m_cumuinfo.getposmap()[self.m_cumuinfo.m_lastplayer] - 1] -= value
                    print "add : ", -value,curturndata[idx],self.m_cumuinfo.m_lastplayer
                    self.m_handsinfo["repairstack"] = True
                    self.reset()
                    self.traversealldata()
                    return
                if value == 0 and curturndata[idx][0] != 4:
                    self.m_handsinfo["data"][0][3][self.m_cumuinfo.getposmap()[self.m_cumuinfo.m_lastplayer] - 1] += self.m_cumuinfo.m_betvalue
                    print self.m_handsinfo["_id"]
                    print "add : ", self.m_cumuinfo.m_betvalue,curturndata[idx],self.m_cumuinfo.m_lastplayer
                    self.m_handsinfo["repairstack"] = True
                    self.reset()
                    self.traversealldata()
                    return

class LastAllinRepair(LastAllinErrorChecker):
    def __init__(self, handsinfo, db, clt):
        HandsInfo.__init__(self,handsinfo)
        self.m_db = db
        self.m_clt = clt

    def repair(self):
        try:
            self.traversealldata()
        except handsinfoexception.LastActionAllinError as e:
            remain = self.m_cumuinfo.m_stacksize[self.m_cumuinfo.m_nextplayer]
            turncount = self.getturncount()
            self.m_handsinfo["data"][turncount][-1][-1] += remain
            self.m_handsinfo["repairlastallin"] = True
            # handsinfocommon.pp.pprint(self.m_handsinfo)
            DBOperater.ReplaceOne(self.m_db, self.m_clt, {"_id": self.m_handsinfo["_id"]}, self.m_handsinfo)
            return True
        except:
            return False
        return False

class RepaireLastAllin(TraverseHands):
    def __init__(self,db,clt,handsid=""):
        TraverseHands.__init__(self,db,clt,handsid)
        self.m_cnt = 0

    def filter(self,handsinfo):
        showcard = handsinfo["showcard"]
        if showcard >= 0 or showcard == -3:
            return False
        return True

    def mainfunc(self,handsinfo):
        if LastAllinRepair(handsinfo,self.m_db,self.m_clt).repair():
            self.m_cnt += 1

class RepaireAllStack(TraverseHands):
    def __init__(self,db,clt,handsid=""):
        TraverseHands.__init__(self,db,clt,handsid)
        self.m_cnt = 0

    def filter(self,handsinfo):
        showcard = handsinfo["showcard"]
        if showcard >= 0 or showcard == -3:
            return False
        return True

    def mainfunc(self,handsinfo):
        try:
            if StackRepairer(handsinfo,self.m_db,self.m_clt).repairStack():
                self.m_cnt += 1
        except:
            pass

class FoldInAdvanceRepair(ReplayEngine):
    def __init__(self,handsinfo):
        ReplayEngine.__init__(self,handsinfo)
        self.m_repairedbetdata = {
            Constant.TURNPREFLOP:[],
            Constant.TURNFLOP:[],
            Constant.TURNTURN:[],
            Constant.TURNRIVER:[]
        }
        self.m_cachebetdata = []
        self.m_repaired = False

    def updatecumuinfo(self,round,actionidx):
        print "updatecumuinfo from FoldInAdvanceRepair:", round, actionidx

        actionpos,action,value = self.m_handsinfo.getspecificturnbetdata(round)[actionidx]
        print "actionpos:", actionpos, self.m_nextplayer
        if actionpos != self.m_nextplayer:
            self.m_repaired = True
            for idx in xrange(len(self.m_cachebetdata)):
                acp,ac,va = self.m_cachebetdata[idx]
                if acp == self.m_nextplayer:
                    self.update(acp,ac,va)
                    self.m_repairedbetdata[self.m_handsinfo.getturnstr(round)].append([acp,ac,va])
                    del self.m_cachebetdata[idx]
                    self.updatecumuinfo(round,actionidx)
                    return
            self.m_cachebetdata.append([actionpos,action,value])
            self.m_lastupdateturn = round
            self.m_lastupdateidx = actionidx
            return
        self.update(actionpos,action,value)
        self.m_repairedbetdata[self.m_handsinfo.getturnstr(round)].append([actionpos,action,value])
        self.m_lastupdateturn = round
        self.m_lastupdateidx = actionidx
        while len(self.m_cachebetdata) and len(self.m_handsinfo.getspecificturnbetdata(round)) == actionidx + 1:
            for idx in xrange(len(self.m_cachebetdata)):
                acp,ac,va = self.m_cachebetdata[idx]
                if acp == self.m_nextplayer:
                    self.update(acp,ac,va)
                    self.m_repairedbetdata[self.m_handsinfo.getturnstr(round)].append([acp,ac,va])
                    del self.m_cachebetdata[idx]
                    break
            else:
                break

    def savedata(self):
        if not self.m_repaired:
            return
        for k in self.m_repairedbetdata.keys():
            if not len(self.m_repairedbetdata[k]):
                del self.m_repairedbetdata[k]
        # handsinfocommon.pp.pprint(self.m_handsinfo.m_handsinfo["data"]["BETDATA"])
        self.m_handsinfo.m_handsinfo["data"]["BETDATA"] = self.m_repairedbetdata
        DBOperater.ReplaceOne(Constant.HANDSDB,Constant.HANDSCLT,{"_id":self.m_handsinfo.getid()},self.m_handsinfo.m_handsinfo)
        # handsinfocommon.pp.pprint(self.m_handsinfo.m_handsinfo["data"]["BETDATA"])

def foldinadvancerepairmainfunc(handsinfo):
    repair = FoldInAdvanceRepair(handsinfo)
    repair.traversealldata()
    repair.savedata()
    return repair.m_repaired

class RemoveInvalidHands(ReplayEngine):
    def updatecumuinfo(self,round,actionidx):
        if self.m_curturn != round:
            raise
        ReplayEngine.updatecumuinfo(self,round,actionidx)

def removeinvalidmain(handsinfo):
    replay = RemoveInvalidHands(handsinfo)
    try:
        replay.traversealldata()
    except:
        DBOperater.DeleteData(Constant.HANDSDB,Constant.HANDSCLT,{"_id":handsinfo["_id"]})
        return True

if __name__ == "__main__":
    # RepaireAllStack(Constant.HANDSDB,Constant.TJHANDSCLT,handsid="35357006093039820170309212244").traverse()
    # v = RepaireAllStack(Constant.HANDSDB, Constant.TJHANDSCLT)
    # v.traverse()
    # print v.m_cnt
    #
    # v = RepaireLastAllin(Constant.HANDSDB, Constant.TJHANDSCLT)
    # v.traverse()
    # print v.m_cnt

    # 下面这个代码用于修复牌局数据库中那些有人还没轮到他行动就提前fold牌的情况,
    # 并会将结果存回牌局数据库中
    TraverseMultiplayerHands(Constant.HANDSDB,Constant.HANDSCLT,func=foldinadvancerepairmainfunc,handsid="",sync=True).traverse()

    # 下面这个代码用于删除牌局数据中有问题的牌局
    TraverseMultiplayerHands(Constant.HANDSDB, Constant.HANDSCLT, func=removeinvalidmain, handsid="",sync=False).traverse()