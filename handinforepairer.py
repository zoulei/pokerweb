from handsengine import HandsInfo
from TraverseHands import TraverseHands
import DBOperater
import Constant
import handsinfocommon

class StackRepairer(HandsInfo):
    def __init__(self, handsinfo, db, clt):
        HandsInfo.__init__(self,handsinfo)
        self.m_db = db
        self.m_clt = clt

    def repairStack(self):
        self.traversealldata()
        self.m_handsinfo["repairstack"] = False
        for idx, value in self.m_cumuinfo.m_stacksize:
            if value < 0:
                self.m_handsinfo["data"][0][3][self.m_cumuinfo.getposmap()[idx] - 1] -= value * 3
                self.m_handsinfo["repairstack"] = True

        handsinfocommon.pp.pprint(self.m_handsinfo)

        # DBOperater.ReplaceOne(self.m_db,self.m_clt,{"_id":self.m_handsinfo["_id"]},self.m_handsinfo)

class RepaireAllStack(TraverseHands):
    def mainfunc(self,handsinfo):
        StackRepairer(handsinfo,self.m_db,self.m_clt).repairStack()

if __name__ == "__main__":
    RepaireAllStack(Constant.HANDSDB,Constant.TJHANDSCLT,handsid="35357006093039820170309212244").traverse()