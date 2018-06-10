# -*- coding:utf-8 -*-
import DBOperater
import Constant
import handsinfocommon
import copy

import multiprocessing
import os
import signal
import time
import handsengine
import traceback


class TraverseHands:
    def __init__(self, db, clt, func = None, handsid = "", step = 10000,
                 start = 0, end = 0, sync = False, para = None, otherpara = None):
        self.m_db = db
        self.m_clt = clt
        self.m_func = func
        self.m_handsid = handsid
        self.m_step = step
        self.m_start = start
        self.m_end = end
        self.m_sync = sync
        self.m_processeddata = 0

        self.m_elapsedtime = 0

        self.m_true = 0
        self.m_false = 0

        self.m_para = para
        self.m_otherpara = otherpara
        self.initdata()

    def initdata(self):
        pass

    def traverse(self):
        start = time.time()

        if self.m_handsid:
            result = DBOperater.Find(self.m_db, self.m_clt, {"_id":self.m_handsid})
        else:
            result = DBOperater.Find(self.m_db, self.m_clt, {})
        doclen = result.count()
        print "traverse document length : ",doclen

        iternum = doclen / self.m_step + 1
        for idx in xrange(iternum):
            if self.m_end and idx >= self.m_end:
                break

            if idx >= self.m_start:
                print "traverse : ",idx
                self.parttraverse(idx)

        end = time.time()
        self.m_elapsedtime = end - start
        day = int(self.m_elapsedtime)/ (24 * 3600)
        hour = int(self.m_elapsedtime)% (24 * 3600)/3600
        min = int(self.m_elapsedtime)%  3600/60
        sec = int(self.m_elapsedtime)%  60
        print "processeddata : ", self.m_processeddata
        print "true value : ", self.m_true
        print "false value : ", self.m_false
        print "elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
        print "elapsedtime : ", self.m_elapsedtime

    def parttraverse(self, idx):
        DBOperater.Connect()
        if not self.m_handsid:
            result = DBOperater.Find(self.m_db, self.m_clt, {})
        else:
            result = DBOperater.Find(self.m_db, self.m_clt,
                                {"_id":self.m_handsid})

        doclist = []
        cnt = 0
        for handsinfo in result[idx * self.m_step:(idx + 1) * self.m_step]:
        # for handsinfo in result:
            # if cnt < idx * self.m_step:
            #     continue
            #
            # if cnt >= (idx + 1) * self.m_step:
            #     break

            if cnt % 1000 == 0:
                print cnt+(idx * self.m_step)
            cnt += 1
            try:
                if not self.filter(handsinfo):
                    doclist.append(copy.deepcopy(handsinfo))
            except:
                print "error : ",handsinfo["_id"]
        self.m_processeddata += len(doclist)

        if self.m_func and not self.m_sync:
            # print "async"
            DBOperater.Disconnect()
            return self.asyncmain(doclist)
        else:
            # print "sync"
            return self.syncmain(doclist)

    def asyncmain(self,doclist):
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = multiprocessing.Pool(Constant.THREADNUM)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            # result = self.m_pool.map_async(self.mainfunc, doclist)
            if self.m_para is None:
                result = pool.map_async(self.m_func, doclist)
            else:
                doclist = [[v,] for v in doclist]
                for v in doclist:
                    v.extend(self.m_para)
                result = pool.map_async(self.m_func, doclist)
            result = result.get(99999999)  # Without the timeout this blocking call ignores all signals.
            for v in result:
                if v is True:
                    self.m_true += 1
                else:
                    self.m_false += 1
        except KeyboardInterrupt:
            pool.terminate()
            pool.close()
            pool.join()
            exit()
        else:
            pool.close()
        pool.join()
        return result

    def syncmain(self,doclist):
        result = []
        for handsinfo in doclist:
            try:
                if self.m_func:
                    if self.m_para is None:
                        returnvalue = self.m_func(handsinfo)
                    else:
                        returnvalue = self.m_func([handsinfo,]+self.m_para)
                else:
                    returnvalue = self.mainfunc(handsinfo)
                result.append(returnvalue)
                if returnvalue is True:
                    self.m_true += 1
                else:
                    self.m_false += 1
            except  KeyboardInterrupt:
                exit()
            except:
                print "===============error=============="
                print "error : ", handsinfo["_id"]
                handsinfocommon.pp.pprint(handsinfo)
                raise
        return result

    def filter(self, handsinfo):
        return False

    def mainfunc(self, handsinfo):
        return "mainfunc of TraverseHands: "+handsinfo["_id"]
        pass

# 该遍历引擎会遍历多人的牌局, 即不会处理单挑局
class TraverseMultiplayerHands(TraverseHands):
    def filter(self, handsinfo):
        if handsinfo["data"]["PLAYQUANTITY"] == 2:
            return True
        return False

# =============================================================
# 下面这些函数都是在本文件中专用的一些测试用或者专用函数
# =============================================================

# 这个是用于验证ReplayEngine正确性的函数
class TestPayoff(TraverseHands):
    def mainfunc(self, handsinfo):
        engine = handsengine.ReplayEngine(handsinfo)
        engine.traversealldata()
        engine.calpayoff()
        handsinfocommon.pp.pprint(handsinfo)
        print "payofflist:",engine.m_payofflist
        idx = 0
        for v in engine.m_payofflist:
            if v > 0:
                idx += 1
        # if idx > 1:
        #     raw_input()

        payoffdict = {
            "2017-12-09 23:01:43 87"  :   "[0, -2, -2, 169, -52, -2, -52, 0, -52, -7]",
            "2017-12-10 22:29:02 112" :   "[0, -2, -2, -2, -2, -92, -2, 0, 109, -7]"
        }
        raw_input()

def traversemultiplayerhandsmainfunc(handsinfo):
    try:
        engine = handsengine.ReplayEngine(handsinfo)
        if engine.m_handsinfo.getplayerquantity() == 2:
            return True
        engine.traversealldata()
        # print "gameover:",engine.isgameover()
        if not engine.isgameover():
            print "=====:",handsinfo["_id"]
            handsinfocommon.pp.pprint(handsinfo)
            DBOperater.DeleteData(Constant.HANDSDB,Constant.HANDSCLT,{"_id":handsinfo["_id"]})
            return False
        return True
    except:
        print "======:",handsinfo["_id"]
        DBOperater.DeleteData(Constant.HANDSDB,Constant.HANDSCLT,{"_id":handsinfo["_id"]})
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 下面这个函数是用来检查一手牌的输赢数据,通过对比输赢数据来确定引擎的正确性
    # TestPayoff(Constant.HANDSDB,Constant.HANDSCLT,handsid="2017-12-15 00:43:13 84",step=1000).traverse()

    # 下面这个函数用于检查牌局数据是否正确,会打印出有错误的牌局数据
    TraverseHands(Constant.HANDSDB,Constant.HANDSCLT,func=traversemultiplayerhandsmainfunc,handsid="").traverse()
