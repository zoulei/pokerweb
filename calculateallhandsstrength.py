# -*- coding:utf-8 -*-
from hunlgame import HandsRange,Poker,board2str
import itertools
from multiprocessingmanager import process
import json
import time
import shelve
import Constant
import sys
from guppy import hpy

TEST = False

def calculateallhandsstrength():
    handrangeobj = HandsRange()
    allcards = handrangeobj._generateallcard()
    poker = Poker()
    fullresult = shelve.open(Constant.ALLHANDSSTRENGTH,writeback=True)
    # fullresult = {}
    cnt = 0
    paralist = []
    start = time.time()
    lasttime = start
    print hpy().heap().bytype
    print "\n"*5
    for idx in xrange(5,8):
        iterobj = itertools.combinations(allcards,idx)
        for cards in iterobj:
            cnt += 1
            paralist.append([cards,poker])
            if cnt % 1000000 == 0:
                print "cnt:",cnt
                result = process(mainfunc,paralist)
                # result = testgetresult(paralist)
                print "process elapsed:",time.time() - lasttime
                elapsedtime = time.time() - lasttime
                day = int(elapsedtime)/ (24 * 3600)
                hour = int(elapsedtime)% (24 * 3600)/3600
                min = int(elapsedtime)%  3600/60
                sec = int(elapsedtime)%  60
                print "process elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
                lasttime = time.time()
                for key,handstype in result:
                    # print key,handstype
                    fullresult[key] = handstype
                fullresult.sync()
                print "writedict elapsed:",time.time() - lasttime
                elapsedtime = time.time() - lasttime
                day = int(elapsedtime)/ (24 * 3600)
                hour = int(elapsedtime)% (24 * 3600)/3600
                min = int(elapsedtime)%  3600/60
                sec = int(elapsedtime)%  60
                print "write dict elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
                lasttime = time.time()
                print "dict size:",sys.getsizeof(fullresult)
                print "para size:",sys.getsizeof(paralist)
                print "result size:",sys.getsizeof(result)
                print "total elapsed:",time.time() - start
                elapsedtime = time.time() - start
                day = int(elapsedtime)/ (24 * 3600)
                hour = int(elapsedtime)% (24 * 3600)/3600
                min = int(elapsedtime)%  3600/60
                sec = int(elapsedtime)%  60
                print "total elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
                print hpy().heap().bytype
                print "\n"*5
                paralist = []
                if TEST:
                    break
    result = process(mainfunc,paralist)
    for key,handstype in result:
        # print key,handstype
        fullresult[key] = handstype
    print "over"
    fullresult.close()
    # json.dump(fullresult,open(Constant.ALLHANDSSTRENGTH,"w"))

def mainfunc(para):
    cards,poker = para
    result = poker.determine_score([],[list(cards),])
    result = result[0]
    handstype = [result[0],]
    kiker = result[1]
    handstype.extend(kiker)
    key = "".join(sorted([str(v) for v in cards]))
    return [key,handstype]

def testgetresult(paralist):
    result = []
    for cards,poker in paralist:
        key = "".join(sorted([str(v) for v in cards]))
        value = [1,2,3,4,5,6]
        result.append([key,value])
    return result

class SortAllHands:
    def loaddata(self):
        self.m_handsstrength = shelve.open(Constant.ALLHANDSSTRENGTH)

    def init(self):
        self.m_dictindex = {}
        for idx in xrange(10):
            self.m_dictindex[idx] = {}
        # 5个踢脚
        for idx in [0,5]:
            for firstlvkey in xrange(2,15):
                self.m_dictindex[idx][firstlvkey] = {}
                for secondlvkey in xrange(2, firstlvkey):
                    self.m_dictindex[idx][firstlvkey][secondlvkey] = {}
                    for thirdlvkey in xrange(2, secondlvkey):
                        self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey] = {}
                        for fourthlvkey in xrange(2,thirdlvkey):
                            self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey][fourthlvkey] =\
                            shelve.open(Constant.CACHEDIR +"_".join([str(v) for v in [idx,firstlvkey,secondlvkey,thirdlvkey,fourthlvkey]]),writeback=True)
        # 4个踢脚
        for idx in [1,]:
            for firstlvkey in xrange(2,15):
                self.m_dictindex[idx][firstlvkey] = {}
                for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                    self.m_dictindex[idx][firstlvkey][secondlvkey] = {}
                    for thirdlvkey in xrange(2, secondlvkey):
                        self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey] =\
                    shelve.open(Constant.CACHEDIR +"_".join([str(v) for v in [idx,firstlvkey,secondlvkey,thirdlvkey]]),writeback=True)
        # 3个踢脚
        for idx in [2,]:
            for firstlvkey in xrange(2,15):
                self.m_dictindex[idx][firstlvkey] = {}
                for secondlvkey in xrange(2, firstlvkey):
                    self.m_dictindex[idx][firstlvkey][secondlvkey] =\
                    shelve.open(Constant.CACHEDIR + "_".join([str(v) for v in [idx,firstlvkey,secondlvkey]]),writeback=True)
        # 3个踢脚,set
        for idx in [3,]:
            for firstlvkey in xrange(2,15):
                self.m_dictindex[idx][firstlvkey] = {}
                for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                    self.m_dictindex[idx][firstlvkey][secondlvkey] =\
                    shelve.open(Constant.CACHEDIR + "_".join([str(v) for v in [idx,firstlvkey,secondlvkey]]),writeback=True)
        # 2个踢脚
        # for idx in [4,6,7,8,9]:
        for idx in [6,7]:
            for firstlvkey in xrange(2,15):
                self.m_dictindex[idx][firstlvkey] =\
                    shelve.open(Constant.CACHEDIR + "_".join([str(v) for v in [idx,firstlvkey]]),writeback=True)
        # 1个踢脚或者没有踢脚
        for idx in [4,8, 9]:
            self.m_dictindex[idx] = shelve.open(Constant.CACHEDIR + str(idx),writeback=True)


    def closeall(self):
        # 5个踢脚
        for idx in [0,5]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in xrange(2, firstlvkey):
                    for thirdlvkey in xrange(2, secondlvkey):
                        for fourthlvkey in xrange(2,thirdlvkey):
                            self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey][fourthlvkey].close()
        # 4个踢脚
        for idx in [1,]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                    for thirdlvkey in xrange(2, secondlvkey):
                        self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey].close()
        # 3个踢脚
        for idx in [2,]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in xrange(2, firstlvkey):
                    self.m_dictindex[idx][firstlvkey][secondlvkey].close()
        # 3个踢脚,set
        for idx in [3,]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                    self.m_dictindex[idx][firstlvkey][secondlvkey].close()
        # 2个踢脚
        # for idx in [4,6,7,8,9]:
        for idx in [6,7]:
            for firstlvkey in xrange(2,15):
                self.m_dictindex[idx][firstlvkey].close()
        # 1个踢脚或者没有踢脚
        for idx in [4,8, 9]:
            self.m_dictindex[idx].close()

    def sync(self):
        # 5个踢脚
        for idx in [0,5]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in xrange(2, firstlvkey):
                    for thirdlvkey in xrange(2, secondlvkey):
                        for fourthlvkey in xrange(2,thirdlvkey):
                            self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey][fourthlvkey].sync()
        # 4个踢脚
        for idx in [1,]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                    for thirdlvkey in xrange(2, secondlvkey):
                        self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey].sync()
        # 3个踢脚
        for idx in [2,]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in xrange(2, firstlvkey):
                    self.m_dictindex[idx][firstlvkey][secondlvkey].sync()
        # 3个踢脚,set
        for idx in [3,]:
            for firstlvkey in xrange(2,15):
                for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                    self.m_dictindex[idx][firstlvkey][secondlvkey].sync()
        # 2个踢脚
        # for idx in [4,6,7,8,9]:
        for idx in [6,7]:
            for firstlvkey in xrange(2,15):
                self.m_dictindex[idx][firstlvkey].sync()
        # 1个踢脚或者没有踢脚
        for idx in [4,8, 9]:
            self.m_dictindex[idx].sync()

    def distributehands(self):
        self.loaddata()
        self.init()
        start = time.time()
        lasttime = start
        cnt = 0
        for hand in self.m_handsstrength:
            strength = self.m_handsstrength[hand]
            handtype = strength[0]
            if handtype in [0,5]:
                self.m_dictindex[handtype][strength[1]][strength[2]][strength[3]][strength[4]][hand] = strength[5]
            elif handtype in [1,]:
                try:
                    self.m_dictindex[handtype][strength[1]][strength[2]][strength[3]][hand] = strength[4]
                except:
                    print "strength[1]:",type(strength[1]),strength[1],strength[2],strength[3],hand
                    print "flkey:",self.m_dictindex[handtype].keys()
                    print "sckey:",self.m_dictindex[handtype][strength[1]].keys()
                    print "thkey;",self.m_dictindex[handtype][strength[1]][strength[2]].keys()
                    raise
                    # print "thkey;",self.m_dictindex[handtype][strength[1]][strength[2]][strength[3]].keys()
            elif handtype in [2,3]:
                self.m_dictindex[handtype][strength[1]][strength[2]][hand] = strength[3]
            elif handtype in [6,7]:
                self.m_dictindex[handtype][strength[1]][hand] = strength[2]
            elif handtype in [4,8]:
                self.m_dictindex[handtype][hand] = strength[1]
            elif handtype in [9,]:
                self.m_dictindex[handtype][hand] = 14
            cnt += 1
            if cnt % 10000000 == 0:
                self.sync()
                print "cnt:",cnt
                print "process elapsed:",time.time() - lasttime
                elapsedtime = time.time() - lasttime
                day = int(elapsedtime)/ (24 * 3600)
                hour = int(elapsedtime)% (24 * 3600)/3600
                min = int(elapsedtime)%  3600/60
                sec = int(elapsedtime)%  60
                print "process elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
                lasttime = time.time()
        self.sync()
        self.closeall()
        del self.m_handsstrength
        print "over"

    def sorthands(self):
        self.init()
        # self.m_handsrank = {}
        self.m_handsrank = shelve.open(Constant.ALLHANDSRANK,writeback=True)
        self.m_laskrank = 0
        start = time.time()
        lasttime = start
        for idx in xrange(0,10):
            print "idx:==================================",idx
            print "process elapsed:",time.time() - lasttime
            elapsedtime = time.time() - lasttime
            day = int(elapsedtime)/ (24 * 3600)
            hour = int(elapsedtime)% (24 * 3600)/3600
            min = int(elapsedtime)%  3600/60
            sec = int(elapsedtime)%  60
            print "process elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
            lasttime = time.time()
            # 5个踢脚
            if idx in [0,5]:
                for firstlvkey in xrange(2,15):
                    for secondlvkey in xrange(2, firstlvkey):
                        print "idx:",idx
                        print "firstlvkey:",firstlvkey
                        print "secondlvkey:",secondlvkey
                        print "process elapsed:",time.time() - lasttime
                        elapsedtime = time.time() - lasttime
                        day = int(elapsedtime)/ (24 * 3600)
                        hour = int(elapsedtime)% (24 * 3600)/3600
                        min = int(elapsedtime)%  3600/60
                        sec = int(elapsedtime)%  60
                        print "process elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
                        lasttime = time.time()
                        for thirdlvkey in xrange(2, secondlvkey):
                            for fourthlvkey in xrange(2,thirdlvkey):
                                subdict = self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey][fourthlvkey]
                                self.sorthandssubdict(subdict)
            # 4个踢脚
            elif idx in [1,]:
                for firstlvkey in xrange(2,15):
                    print "idx:",idx
                    print "firstlvkey:",firstlvkey
                    print "process elapsed:",time.time() - lasttime
                    elapsedtime = time.time() - lasttime
                    day = int(elapsedtime)/ (24 * 3600)
                    hour = int(elapsedtime)% (24 * 3600)/3600
                    min = int(elapsedtime)%  3600/60
                    sec = int(elapsedtime)%  60
                    print "process elapsedtime : ", day, "D", hour,"H", min, "M", sec, "S"
                    lasttime = time.time()
                    for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                        for thirdlvkey in xrange(2, secondlvkey):
                            subdict = self.m_dictindex[idx][firstlvkey][secondlvkey][thirdlvkey]
                            self.sorthandssubdict(subdict)
            # 3个踢脚
            elif idx in [2,]:
                for firstlvkey in xrange(2,15):
                    for secondlvkey in xrange(2, firstlvkey):
                        subdict = self.m_dictindex[idx][firstlvkey][secondlvkey]
                        self.sorthandssubdict(subdict)
            # 3个踢脚
            elif idx in [3,]:
                for firstlvkey in xrange(2,15):
                    for secondlvkey in range(2, firstlvkey)+range(firstlvkey+1,15):
                        subdict = self.m_dictindex[idx][firstlvkey][secondlvkey]
                        self.sorthandssubdict(subdict)
            # 2个踢脚
            elif idx in [6,7]:
                for firstlvkey in xrange(2,15):
                    subdict = self.m_dictindex[idx][firstlvkey]
                    self.sorthandssubdict(subdict)
            # 1个踢脚或者没有踢脚
            elif idx in [4,8, 9]:
                subdict = self.m_dictindex[idx]
                self.sorthandssubdict(subdict)
        self.closeall()
        self.m_handsrank.close()
        # json.dump(self.m_handsrank, open(Constant.ALLHANDSRANK,"w"))
        print "over"

    def sorthandssubdict(self,subdict):
        if not len(subdict):
            return
        keyvaluelist = subdict.items()
        keyvaluelist.sort(key=lambda v:v[1])
        self.m_laskrank += 1
        self.m_handsrank[keyvaluelist[0][0]] = self.m_laskrank
        for idx in xrange(1,len(keyvaluelist)):
            if keyvaluelist[idx][1] != keyvaluelist[idx - 1][1]:
                self.m_laskrank += 1
            self.m_handsrank[keyvaluelist[idx][0]] = self.m_laskrank
        self.m_handsrank.sync()
        return keyvaluelist

    def writedicttomemory(self):
        handsrank = shelve.open(Constant.ALLHANDSRANK)
        handsrankinmemory = {}
        cnt = 0
        for key in handsrank:
            cnt += 1
            if cnt % 10000000 == 0:
                print "cnt:",cnt
            handsrankinmemory[key] = handsrank[key]
        print "dumpjson"
        json.dump(handsrankinmemory,open(Constant.ALLHANDSRANKINMEMORYJSON,"w"))
        print "writestr"
        open(Constant.ALLHANDSRANKINMEMORYSTR,"w").write(str(handsrankinmemory))
        print "writeover"

def testhandsstrength():
    hs = shelve.open(Constant.ALLHANDSSTRENGTH)
    from hunlgame import generateCards
    cards = generateCards("AHKHJHTHTS8S2S")
    print hs["".join(sorted([str(v) for v in cards]))]
    cards = generateCards("AHKHJHTHTS8S8C")
    print hs["".join(sorted([str(v) for v in cards]))]
    cards = generateCards("AHKHJHTHTS8S2H")
    print hs["".join(sorted([str(v) for v in cards]))]
    cards = generateCards("AHKHJHTHTS8S2S")
    print hs["".join(sorted([str(v) for v in cards]))]
    cards = generateCards("AHKHJHTHTS8SQS")
    print hs["".join(sorted([str(v) for v in cards]))]
    cards = generateCards("AHKHJHTHTS8SQH")
    print hs["".join(sorted([str(v) for v in cards]))]

def testdistribute():
    pass

if __name__ == "__main__":
    # calculateallhandsstrength()
    # testhandsstrength()

    sortengine = SortAllHands()
    # sortengine.distributehands()

    # sortengine.sorthands()
    sortengine.writedicttomemory()