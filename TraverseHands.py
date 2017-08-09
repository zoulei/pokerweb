import DBOperater
import Constant

class TraverseHands:
    # def __init__(self,db,clt,handsnum = 0):
    def __init__(self, db, clt, handsid = ""):
        self.m_db = db
        self.m_clt = clt
        self.m_handsid = handsid
        # self.m_limit = handsnum

    def traverse(self):
        if self.m_handsid:
            result = DBOperater.Find(Constant.HANDSDB, Constant.TJHANDSCLT, {"_id":self.m_handsid})
        else:
            result = DBOperater.Find(Constant.HANDSDB, Constant.TJHANDSCLT, {})
        doclen = result.count()
        print "traverse document length : ",doclen

        iternum = doclen / 10000 + 1
        for idx in xrange(iternum):
            self.traverse_(idx)

    def traverse_(self, idx):
        if not self.m_handsid:
            result = DBOperater.Find(Constant.HANDSDB, Constant.TJHANDSCLT, {})
        else:
            result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,
                                {"_id":self.m_handsid})

        doclist = []
        cnt = 0
        for handsinfo in result:
            cnt += 1
            if cnt < idx * 10000:
                continue

            if cnt >= (idx + 1) * 10000:
                break

            if cnt % 1000 == 0:
                print cnt

            # if idx * 10000 + cnt >= self.m_limit:
            #     break

            doclist.append(handsinfo)

        for handsinfo in doclist:
            self.mainfunc(handsinfo)

    def mainfunc(self, handsinfo):
        print "mainfunc of TraverseHands"
        pass