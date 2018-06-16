# -*- coding: utf-8 -*-
import TraverseHands
from Constant import *
import DBOperater
from purehandsreader import *
import time

# 存在内存中的牌局数据
inmemoryhands = None

def loadhandsintomemory():
    global inmemoryhands
    inmemoryhands = []
    result = DBOperater.Find(HANDSDB,STATEINFOHANDSCLT,{})
    # for doc in result[:10000]:
    for doc in result:
        docreader = PureHandsReader(doc)
        docreader.initboard()
        docreader.initprivatehand()
        inmemoryhands.append(docreader)

def getinmemoryhands():
    global inmemoryhands
    if inmemoryhands is None:
        loadhandsintomemory()
    return inmemoryhands

# 该类会使用内存中的牌局数据，而不会再从数据库读牌局数据
class InMemoryTraverse(TraverseHands.TraverseHands):
    def traverse(self):
        doclist = getinmemoryhands()
        start = time.time()
        if self.m_end:
            doclist = doclist[self.m_start*self.m_step:self.m_end*self.m_step]
        doclen = len(doclist)
        print "traverse document length : ",doclen

        if self.m_func and not self.m_sync:
            # print "async"
            # 异步功能还没有测试过
            result = self.asyncmain(doclist)
        else:
            # print "sync"
            result = self.syncmain(doclist)

        for v in result:
            if v is True:
                self.m_true += 1
            else:
                self.m_false += 1

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