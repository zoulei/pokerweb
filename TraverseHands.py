import DBOperater
import Constant
import handsinfocommon
import copy

import multiprocessing
import os
import signal
import time
import handsengine

class TraverseHands:
    # def __init__(self,db,clt,handsnum = 0):
    def __init__(self, db, clt, func = None, handsid = "", step = 10000, sync = False):
        self.m_db = db
        self.m_clt = clt
        self.m_func = func
        self.m_handsid = handsid
        self.m_step = step
        self.m_sync = sync
        # self.m_limit = handsnum
        self.m_processeddata = 0

        self.m_elapsedtime = 0


    def traverse(self):
        start = time.time()

        if self.m_handsid:
            result = DBOperater.Find(Constant.HANDSDB, Constant.TJHANDSCLT, {"_id":self.m_handsid})
        else:
            result = DBOperater.Find(Constant.HANDSDB, Constant.TJHANDSCLT, {})
        doclen = result.count()
        print "traverse document length : ",doclen

        iternum = doclen / self.m_step + 1
        for idx in xrange(iternum):
            print "traverse : ",idx
            self.traverse_(idx)

        end = time.time()
        self.m_elapsedtime = end - start
        day = int(self.m_elapsedtime)/ (24 * 3600)
        hour = int(self.m_elapsedtime)% (24 * 3600)/3600
        min = int(self.m_elapsedtime)%  3600/60
        sec = int(self.m_elapsedtime)%  60
        print "processeddata : ", self.m_processeddata
        print "elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
        print "elapsedtime : ", self.m_elapsedtime

    def traverse_(self, idx):
        # DBOperater.Connect()
        if not self.m_handsid:
            result = DBOperater.Find(Constant.HANDSDB, Constant.TJHANDSCLT, {})
        else:
            result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,
                                {"_id":self.m_handsid})

        doclist = []
        cnt = 0
        for handsinfo in result:
            cnt += 1
            if cnt < idx * self.m_step:
                continue

            if cnt >= (idx + 1) * self.m_step:
                break

            if cnt % 1000 == 0:
                print cnt

            if not self.filter(handsinfo):
                doclist.append(copy.deepcopy(handsinfo))
                # doclist.append(handsinfo)
        # DBOperater.Disconnect()
        self.m_processeddata += len(doclist)

        if self.m_func and not self.m_sync:
            # print "async"
            self.asyncmain(doclist)
        else:
            # print "sync"
            self.syncmain(doclist)

    def asyncmain(self,doclist):
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = multiprocessing.Pool(Constant.THREADNUM)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            # result = self.m_pool.map_async(self.mainfunc, doclist)
            result = pool.map_async(self.m_func, doclist)
            result.get(99999999)  # Without the timeout this blocking call ignores all signals.
        except KeyboardInterrupt:
            pool.terminate()
            pool.close()
            pool.join()
            exit()
        else:
            pool.close()
        pool.join()

    def syncmain(self,doclist):
        for handsinfo in doclist:
            # if not self.filter(handsinfo):
            self.m_processeddata += 1
            try:
                if self.m_func:
                    self.m_func(handsinfo)
                else:
                    self.mainfunc(handsinfo)
            except  KeyboardInterrupt:
                exit()
            except:
                print "===============error=============="
                print "error : ", handsinfo["_id"]
                handsinfocommon.pp.pprint(handsinfo)
                raise

    def filter(self, handsinfo):
        return False

    def mainfunc(self, handsinfo):
        return "mainfunc of TraverseHands: "+handsinfo["_id"]
        pass

class TraverseValidHands(TraverseHands):
    def filter(self, handsinfo):
        return not handsengine.HandsInfo(handsinfo).isvalid()

def mainfunc( handsinfo):
    time.sleep(20)
    return "mainfunc of TraverseHands: " + handsinfo["_id"]

if __name__ == "__main__":
    TraverseHands(Constant.HANDSDB,Constant.TJHANDSCLT,func=mainfunc,handsid="").traverse()