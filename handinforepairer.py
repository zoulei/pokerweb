from handsengine import HandsInfo
from TraverseHands import TraverseHands
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
            handsinfocommon.pp.pprint(self.m_handsinfo)
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
            handsinfocommon.pp.pprint(self.m_handsinfo)
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
        if StackRepairer(handsinfo,self.m_db,self.m_clt).repairStack():
            self.m_cnt += 1

if __name__ == "__main__":
    # RepaireAllStack(Constant.HANDSDB,Constant.TJHANDSCLT,handsid="35357006093039820170309212244").traverse()
    # v = RepaireAllStack(Constant.HANDSDB, Constant.TJHANDSCLT)
    # v.traverse()
    # print v.m_cnt

    v = RepaireLastAllin(Constant.HANDSDB, Constant.TJHANDSCLT)
    v.traverse()
    print v.m_cnt