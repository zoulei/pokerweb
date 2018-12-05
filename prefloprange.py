# -*- coding:utf-8 -*-
import Constant
import DBOperater
import handsinfocommon
import copy
import believeinterval
import math
import tongjihandsinfo
from handsengine import ReplayEngine
from TraverseHands import TraverseHands
import handsengine
import pprint
import traceback
pp = pprint.PrettyPrinter(indent=4)


class JoinrateRepairer:
    def __init__(self, ftdata):
        self.ftdata  =ftdata

    def repairdata(self):
        self.combine(Constant.HANDSTHRE,Constant.STATETHRE)
        self.repair(Constant.BELIEVERATE,Constant.FILTERHANDS)

    def enoughdata(self,betbbdata,handsthre, instancethre):
        mininstance = instancethre
        for payoffrate in betbbdata:
            if sum(betbbdata[payoffrate].values() ) >= handsthre:
                mininstance -= 1
                if mininstance == 0:
                    return True
        return False

    def combineinto(self,posdata,betbb,combinedbetbb):
        keylist1 = posdata[betbb].keys()
        keylist2 = posdata[combinedbetbb].keys()
        keymap = {}
        for key in keylist1:
            keymap[key] = 1
        for key in keylist2:
            keymap[key] = 1
        keylist = keymap.keys()
        keylist.sort(key=lambda v:int(v))

        for key in keylist:
            if key not in posdata[betbb]:
                posdata[betbb][key] = {"call":0,"fold":0,"raise":0,"sum":0}
            if key not in posdata[combinedbetbb]:
                posdata[combinedbetbb][key] = {"call":0,"fold":0,"raise":0,"sum":0}

        for key in keylist:
            betbbdata = posdata[betbb].get(key)
            combineddata = posdata[combinedbetbb].get(key)
            for key in betbbdata.keys():
                betbbdata[key] += combineddata[key]
        del posdata[combinedbetbb]

    def getrepaireddata(self):
        return self.repairedftata

    def combine(self,handsthre,statethre):
        self.repairedftata = copy.deepcopy(self.ftdata)
        for pos in self.ftdata.keys():
            posdata = self.repairedftata[pos]
            betbblist = posdata.keys()
            betbblist.sort(key = lambda v:int(v))

            idx = 1
            curidx = 0
            while curidx < len(betbblist):
                betbb = betbblist[curidx]
                if self.enoughdata(posdata[betbb],handsthre,statethre):
                    curidx = idx
                    idx += 1
                elif idx == len(betbblist):
                    # no more data, combine the last two betbb data and break
                    tmpbetbblist = posdata.keys()
                    tmpbetbblist.sort(key = lambda v:int(v) )
                    print tmpbetbblist,pos
                    if len(tmpbetbblist) > 1:
                        self.combineinto(posdata,tmpbetbblist[-2],tmpbetbblist[-1])
                    break
                else:
                    # combine idx and curidx
                    self.combineinto(posdata,betbblist[curidx],betbblist[idx])
                    idx += 1

    def payoffdatavalid(self,payoffratedata):
        up = 0
        down = 0
        for idx in xrange(len(payoffratedata) - 1):
            if payoffratedata[idx + 1] > payoffratedata[idx]:
                up = 1
            elif payoffratedata[idx + 1] < payoffratedata[idx]:
                down = 1
        if up == 1 and down == 1:
            return False
        return True

    def caloffset(self,payoffratedata,intervaldata,joinratedata,datatype):
        offset = 0
        keylist = intervaldata.keys()
        keylist.sort(key = lambda v: int(v))
        for idx in xrange(len(payoffratedata)):
            repaireddata = payoffratedata[idx]
            key = keylist[idx]
            intervallen = intervaldata[key][datatype][1] - intervaldata[key][datatype][0]
            vieweddata = joinratedata[key][datatype]

            offset += math.fabs(vieweddata - repaireddata) / intervallen

        return offset

    def getbestuppayoffratedata(self,intervaldata,joininratedata,datatype):
        payoffratelist = intervaldata.keys()
        payoffratelist.sort(key = lambda v: int(v))

        repairedrate = []
        for payoffrate in payoffratelist:
            repairedrate.append(joininratedata[payoffrate][datatype])

        lastoffset = -1
        for idx in xrange(1,len(repairedrate)):
            maxjoinrate = max(repairedrate[:idx])
            if repairedrate[idx] >= repairedrate[idx - 1]:
                continue
            joinrate = round(repairedrate[idx],3)
            offset = -1
            bestjoinrate = joinrate

            while joinrate <= maxjoinrate:
                tmprepairedrate = copy.deepcopy(repairedrate)
                tmprepairedrate[idx] = joinrate
                for i in xrange(idx):
                    if tmprepairedrate[i] > joinrate:
                        tmprepairedrate[i] = joinrate
                curoffset = self.caloffset(tmprepairedrate[:idx + 1],intervaldata,joininratedata,datatype)
                if offset == -1 or curoffset < offset:
                    bestjoinrate = joinrate
                    offset = curoffset
                    lastoffset = curoffset
                joinrate = round(joinrate+0.001,3)
            repairedrate[idx] = bestjoinrate
            for i in xrange(idx):
                if repairedrate[i] > bestjoinrate:
                    repairedrate[i] = bestjoinrate

        return repairedrate,lastoffset

    def getbestdownpayoffratedata(self,intervaldata,joininratedata,datatype):
        payoffratelist = intervaldata.keys()
        payoffratelist.sort(key = lambda v: int(v))

        repairedrate = []
        for payoffrate in payoffratelist:
            repairedrate.append(joininratedata[payoffrate][datatype])
        lastoffset = -1
        for idx in xrange(1,len(repairedrate)):
            minjoinrate = min(repairedrate[:idx])
            if repairedrate[idx] <= repairedrate[idx - 1]:
                continue
            joinrate = repairedrate[idx]
            offset = -1
            bestjoinrate = joinrate

            while joinrate >= minjoinrate:
                tmprepairedrate = copy.deepcopy(repairedrate)
                tmprepairedrate[idx] = joinrate
                for i in xrange(idx):
                    if tmprepairedrate[i] < joinrate:
                        tmprepairedrate[i] = joinrate
                curoffset = self.caloffset(tmprepairedrate[:idx + 1],intervaldata,joininratedata,datatype)
                if offset == -1 or curoffset < offset:
                    bestjoinrate = joinrate
                    offset = curoffset
                    lastoffset = curoffset
                joinrate = round(joinrate-0.001,3)
            repairedrate[idx] = bestjoinrate
            for i in xrange(idx):
                if repairedrate[i] < bestjoinrate:
                    repairedrate[i] = bestjoinrate

        return repairedrate,lastoffset

    def getbestpayoffratedata(self,intervaldata,joininratedata,datatype):
        updata, upoffset = self.getbestuppayoffratedata(intervaldata,joininratedata,datatype)
        downdata, downoffset = self.getbestdownpayoffratedata(intervaldata,joininratedata,datatype)
        if upoffset < downoffset:
            return updata
        else:
            return downdata

    def insertrepaireddata(self,betbbdata,repairedrate,datatype):
        payoffratelist = betbbdata.keys()
        payoffratelist.sort(key = lambda v: int(v))

        for idx in xrange(len(repairedrate)):
            payoffrate = payoffratelist[idx]
            betbbdata[payoffrate][datatype] = repairedrate[idx]

    def calfoldrate(self,betbbdata):
        for payoffrate,payoffratedata in betbbdata.items():
            payoffratedata["fold"] = round(1 - payoffratedata["call"],3)

    def repair(self,believerate,filterhands):
        believeintervaldata = {}
        joinratedata = {}

        for pos,posdata in self.repairedftata.items():
            believeintervaldata[pos] = {}
            joinratedata[pos] = {}
            # if pos != "9":
            #     continue
            for betbb, betbbdata in posdata.items():
                # if betbb != "24":
                #     continue
                believeintervaldata[pos][betbb] = {}
                joinratedata[pos][betbb] = {}

                for payoffrate, payoffratedata in betbbdata.items():

                    sumhands = payoffratedata["sum"]
                    if sumhands < filterhands:
                        del betbbdata[payoffrate]
                        continue
                    else:
                        believeintervaldata[pos][betbb][payoffrate] = {}
                        joinratedata[pos][betbb][payoffrate] = {}

                        believeintervaldict = believeintervaldata[pos][betbb][payoffrate]
                        joinratedict = joinratedata[pos][betbb][payoffrate]

                    callhands = payoffratedata["call"] + payoffratedata["raise"]
                    raisehands = payoffratedata["raise"]

                    believeintervaldict["call"] = believeinterval.calcBin(callhands, sumhands, believerate)
                    believeintervaldict["raise"] = believeinterval.calcBin(raisehands, sumhands, believerate)
                    joinratedict["call"] = round(callhands * 1.0 / sumhands,3)
                    joinratedict["raise"] = round(raisehands * 1.0 / sumhands,3)

                repairedcalldata = self.getbestpayoffratedata(believeintervaldata[pos][betbb],joinratedata[pos][betbb],"call")
                repairedraisedata = self.getbestpayoffratedata(believeintervaldata[pos][betbb],joinratedata[pos][betbb],"raise")
                self.insertrepaireddata(betbbdata,repairedcalldata,"call")
                self.insertrepaireddata(betbbdata,repairedraisedata,"raise")
                self.calfoldrate(betbbdata)

class Preflopstatemachine(ReplayEngine):
    def __init__(self,handsinfo,debug= False):
        ReplayEngine.__init__(self,handsinfo)
        if self.m_playerquantity < 6:
            return
        self.m_debug = debug
        self.retrivedoc()
        self.calstate()
        if not debug:
            self.savedoc()

    def retrivedoc(self):
        result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
        if result.count() == 0:
            prefloprange = {
                "_id":Constant.PREFLOPRANGEDOC,
                Constant.FTDATA:{},

                Constant.STDATA:{},
                Constant.A3BETDATA:{},
                Constant.A4BETDATA:{},
                Constant.A5BETDATA:{},
            }
        else:
            prefloprange = result.next()
        self.m_doc = prefloprange

    def savedoc(self):
        DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC},self.m_doc,True)

    def generatestate(self):
        laststate = self.getlaststate()
        circle = laststate["circle"]
        betlevel = laststate["betlevel"]
        relativepos = laststate["relativepos"]
        normalneedtobet = laststate["normalneedtobet"]
        normalpayoff = laststate["normalpayoff"]
        betbb = laststate["betbb"]
        pos = laststate["pos"]

        field = Constant.getprefloprangefield(circle,betlevel)
        targetdoc = self.m_doc[field]
        if circle == 1 and betlevel < 3:
            flkey = str(pos)
            slkey = str(betbb)
            tlkey = str(normalpayoff)
        else:
            flkey = str(relativepos)
            slkey = str(normalneedtobet)
            tlkey = str(normalpayoff)

        handsinfocommon.completedict(targetdoc, flkey, slkey, tlkey)
        targetdoc = targetdoc[flkey][slkey][tlkey]

        lastaction,lastattack = self.getlastaction()
        realaction = self.actiontransfer(lastaction)
        if realaction == Constant.CHECK:
            realaction = Constant.CALL
        if realaction:
            targetdoc[realaction] += 1
            targetdoc["sum"] += 1

    def calstate(self):
        preflopdata = self.m_handsinfo.getpreflopbetdata()
        for idx in xrange(len(preflopdata)):
            self.updatecumuinfo(1, idx)
            self.generatestate()

def tongjijoinrate():
    DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPJOINRATEDOC})
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        return
    joinratedoc = {"_id":Constant.PREFLOPJOINRATEDOC}
    rangedoc = result.next()
    keylist = rangedoc.keys()
    for key in keylist:
        if key == "_id":
            continue
        joinratedoc[key] = {}
        fielddoc = joinratedoc[key]
        rawdatadoc = rangedoc[key]

        for flkey, fldata in rawdatadoc.items():
            if flkey not in fielddoc:
                fielddoc[flkey] = {}
            for slkey, sldata in fldata.items():
                if slkey not in fielddoc[flkey]:
                    fielddoc[flkey][slkey] = {}
                for tlkey, tldata in sldata.items():
                    if tlkey not in fielddoc[flkey][slkey]:
                        fielddoc[flkey][slkey][tlkey] = {}
                    curfielddoc = fielddoc[flkey][slkey][tlkey]
                    currawdoc = rawdatadoc[flkey][slkey][tlkey]
                    sumhands = currawdoc["sum"]
                    curfielddoc["sum"] = sumhands
                    curfielddoc["fold"] = round(currawdoc["fold"] * 1.0 / sumhands,3)
                    curfielddoc["raise"] = round(currawdoc["raise"] * 1.0 / sumhands,3)
                    curfielddoc["call"] = round(currawdoc["call"] * 1.0 / sumhands,3)
                    # curfielddoc["call"] = round((currawdoc["raise"] + currawdoc["call"]) * 1.0 / sumhands,3)
    DBOperater.StoreData(Constant.HANDSDB, Constant.CUMUCLT,joinratedoc)

def repairjoinrate():
    DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPREPAIRJOINRATEDOC})
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        return
    preflopdoc = result.next()
    repairdoc = {"_id":Constant.PREFLOPREPAIRJOINRATEDOC}

    for key in preflopdoc.keys():
        if key == "_id":
            continue
        repairer = JoinrateRepairer(preflopdoc[key])
        repairer.repairdata()
        repairdoc[key] = repairer.getrepaireddata()

    DBOperater.StoreData(Constant.HANDSDB,Constant.CUMUCLT,repairdoc)

def removepreflopdoc():
    DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})

def tongjiftmain():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})
    doclen =  result.count()

    iternum = doclen / 10000 + 1
    for idx in xrange(iternum):
        tongjiftmain_(idx)

def tongjiftmain_(idx):
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{})
    # result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,
    #                         {"_id":"35858405032626420170603224833"})

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
            Preflopstatemachine(handsinfo)
        except:
            print "============="
            print handsinfo["_id"]
            traceback.print_exc()

class TestRangeAccuracy(ReplayEngine):
    def __init__(self,handsinfo):
        ReplayEngine.__init__(self, handsinfo)

        self.m_rangeengine = handsengine.prefloprangge()

    def test(self):
        if self.m_handsinfo.getplayerquantity() < 6:
            return list([0,0])
        self.traversepreflop()

        correct = 0
        wrong = 0
        for pos, pvhand in enumerate(self.m_handsinfo.getprivatehands()):
            if not pvhand:
                continue
            joinrate = self.m_prefloprange[pos]
            joinrate += 0.00001
            if pvhand in self.m_rangeengine.gethandsinrange(joinrate):
                correct += 1
            else:
                realjoinrate = self.m_rangeengine.gethandsjoinrate(pvhand)
                print self.m_handsinfo.getid(), pos, round(joinrate,3), pvhand, realjoinrate, round(realjoinrate / joinrate, 4)
                wrong += 1
        return list([correct, wrong])

rangeaccuracydict= {"correct":0,"wrong":0}

def mainfunc(handsinfo):
    global rangeaccuracydict
    correct, wrong = TestRangeAccuracy(handsinfo).test()
    rangeaccuracydict["correct"] += correct
    rangeaccuracydict["wrong"] += wrong

def testprefloprangemain():
    TraverseHands(Constant.HANDSDB,Constant.HANDSCLT,func=mainfunc,handsid="",sync=True, step=1000,end=10).traverse()
    handsinfocommon.pp.pprint(rangeaccuracydict)
    handsinfocommon.printdictbypercentage(rangeaccuracydict)

if __name__ == "__main__":
    # 下面这四个函数一起用来激活翻前范围程序
    removepreflopdoc()

    tongjiftmain()
    tongjijoinrate()
    repairjoinrate()

    # 下面这个程序用于测试上面生成的翻前范围配合翻前排力排行的准确率
    testprefloprangemain()

