# -*- coding:utf-8 -*-
from statestrategycalculator import *
from Constant import *
import DBOperater
from stateinfocalculator import *
from purehandsreader import *
import threading
import handsengine
import TraverseHands
import hunlgame
import os
import time
from handsdistribution import RangeState
from mytimer import Timer
from InMemoryTraverseHands import *

def submitmainfunc(para):
    handsinfo, state, stateid, stateturn, stateidx = para
    prefloprangeengine = handsengine.getprefloprangeobj()
    curturn = state.getstateturn()
    replay = PureHandsReader(handsinfo)
    if replay.getturncount() < 2:
        return
    trainstate = replay.getstate(curturn, 0)
    replay.initprivatehand()
    pvhand = replay.gethand(trainstate[Constant.NEXTPLAYER])
    if pvhand is None:
        return

    statesimilar = trainstate - state
    if statesimilar < 0.8:
        return

    oppohands = []
    for pos, inpoolstate in enumerate(trainstate[Constant.INPOOLSTATE]):
        if inpoolstate != 0 and pos != trainstate[Constant.NEXTPLAYER]:
            oppohands.append(
                handsdistribution.HandsDisQuality(prefloprangeengine.gethandsinrange(replay.getprefloprange()[pos])))
    replay.initboard()
    board = replay.getboardcard()[:3]
    # 把pvhand, board, oppohands, statesimilar都返回，由主函数统一写文件
    action = replay.getspecificturnrealbetdata(curturn)[0][1]
    RangeState(board, pvhand, oppohands).checkparavalid()
    fname = "_".join([stateid, str(stateturn), str(stateidx), replay["_id"], "0"])
    fname = fname.replace(" ", "")
    ofile = open(TEMPSUBMITTASKDIR + fname, "w")
    ofile.write(stateid + "\n")
    ofile.write(str(stateturn) + " " + str(stateidx) + "\n")
    ofile.write(str(statesimilar) + " " + action + "\n")
    ofile.write("".join([str(v) for v in pvhand.get()]) + " " + "".join([str(v) for v in board]) + "\n")
    ofile.write(str(len(oppohands)) + "\n")
    for handsdis in oppohands:
        # "0 0" 为标识符，一个该标识符表示接下来的数据为一个新的对手的手牌分布
        ofile.write(str(len(handsdis)) + "\n")
        for hands, rate in handsdis.items():
            ofile.write("".join([str(v) for v in hands.get()]) + " " + str(rate) + "\n")
    ofile.close()
    os.system("mv " + TEMPSUBMITTASKDIR + fname + " " + SUBMITTASKDIR + fname)
    return
    # return [stateid, stateturn, stateidx, pvhand, board, oppohands, statesimilar, action]

    # == == == == == == == == ==
    # cal
    # similar: 6.03044581413
    # prepare
    # para: 1.02557849884
    # traverse: 9.71223711967
    # work: 27.1291205883
    # prepare
    # replay: 4040.68550062
    # == == == == == == == == ==
    # cal
    # similar: 0.00147639207904
    # prepare
    # para: 0.000251085246231
    # traverse: 0.0023777794205
    # work: 0.00664183378518
    # prepare
    # replay: 0.989252909469

class TaskSubmitter():
    def __init__(self, db = HANDSDB, clt = STATEINFOHANDSCLT):
        # threading.Thread.__init__(self)
        self.m_db = db
        self.m_clt = clt

    def run(self):
        result = DBOperater.Find(self.m_db, self.m_clt, {"_id":"2017-12-11_20:05:31_116"})
        idx = 0
        for doc in result:
            replay = stateinfocalculator.StateReaderEngine(doc)
            if replay.m_handsinfo.getturncount() == 1:
                continue
            state = replay.getstate(2, 0)
            self.calstrategyforspecificstate(state, doc["_id"], 2, 0)
            break
            idx += 1
            if idx == 100:
                break

    def calstrategyforspecificstate(self, state, stateid, turnidx, actionidx):
        # 根据秀牌数据提交强化学习数据
        submittaskengine = TraverseHands.TraverseMultiplayerHands(self.m_db, self.m_clt, func=submitmainfunc, sync=True, step=10000, end=1,
                                          para=[state, stateid, turnidx, actionidx])
        submittaskengine.traverse()

class ResultDealer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.m_taskdata = TaskData()

    def run(self):
        fnamelist = os.listdir(TASKRESULTDIR)
        for fname in fnamelist:
            ifile = open(TASKRESULTDIR+fname)
            stateid = ifile.readline().strip()
            stateturn, stateidx = [int(v) for v in ifile.readline().strip().split(SPACE)]
            actiondisdata = self.m_taskdata.getdata(stateid, stateturn, stateidx).getdata()
            for line in ifile:
                hpidx, action, weight = line.strip().split(SPACE)
                actiondisdata.addaction(hpidx, action, weight)
        # 这里还缺少了一个写结果的步骤，这个之后再想怎么写
            os.system("rm "+TASKRESULTDIR+fname)

class FastFullActionDis:
    def __init__(self, restorestr = None):
        self.m_marker = handspower.RandomMarker()
        if restorestr is None:
            self.initdata()
        else:
            self.restoredata(restorestr)

    # 从存储的文本中恢愎数据
    def restoredata(self,restorestr):
        svdata = json.loads(restorestr)
        self.m_actiondisdata = [ActionDis(jsonstr=v) for v in svdata]
        self.m_actiondisidx = {}
        for idx, v in enumerate(self.m_marker.m_hplist):
            self.m_actiondisidx[v] = idx

    # 该方法初始化本类的数据结构
    def initdata(self):
        self.m_actiondisdata = []
        self.m_actiondisidx = {}
        for idx,v in enumerate(self.m_marker.m_hplist):
            self.m_actiondisidx[v] = idx
            self.m_actiondisdata.append(ActionDis())

    # 更新数据的时候可以根据hp的下标更新或者直接查找hp更新
    # 根据hp的下标更新速度应该会更快一点
    def addaction(self, hp, action, rate):
        if isinstance(hp, int):
            self.m_actiondisdata[hp].addaction(action, rate)
        else:
            self.m_actiondisdata[self.m_actiondisidx[hp]].addaction(action, rate)

    # 该方法将完整的行为分布中每一个hp的行为分布都归一化
    def normalize(self):
        for hp in self.m_actiondisdata:
            hp.normalize()

    def __str__(self):
        return json.dumps([str(v) for v in self.m_actiondisdata])

class StateTrainData:
    def __init__(self, stateid, turn, idx):
        self.m_id = stateid
        self.m_turn = turn
        self.m_idx = idx
        self.m_fullactiondis = FastFullActionDis()

    def getdata(self):
        return self.m_fullactiondis

class TaskData:
    def __init__(self, db = HANDSDB, clt = STATEINFOHANDSCLT):
        self.m_db = db
        self.m_clt = clt
        self.m_taskdata = {}
        # self.readhandsdoc()

    # 把所有的手牌数据都读进来不实际的，因为所有的手牌太大了
    # 大概1000手牌占内存1G
    # def readhandsdoc(self ):
    #     self.m_replaydata = []
    #     result = DBOperater.Find(self.m_db, self.m_clt, {})
    #     idx = 0
    #     for handsinfo in result:
    #         replay = ReplayEngine(handsinfo)
    #         if replay.m_handsinfo.getplayerquantity() > 5:
    #             idx += 1
    #             if idx % 1000 == 0:
    #                 print idx
    #             self.m_replaydata.append(replay)

    def getdatakey(self, stateid, turn, idx):
        return stateid + "\t" + str(turn) + "\t" + str(idx)

    def getdata(self, stateid, turn, idx):
        key = self.getdatakey(stateid, turn, idx)
        if key not in self.m_taskdata:
            self.m_taskdata[key] = StateTrainData(stateid, turn, idx)
        return self.m_taskdata[key]

def testdocsize():
    import copy
    import time
    result = DBOperater.Find(HANDSDB,STATEINFOHANDSCLT,{})
    doclist = []
    idx = 0
    for doc in result:
        idx += 1
        if idx %1000 == 0:
            print idx
        doclist.append(PureHandsReader(doc))
    time.sleep(100)
    # 读进所有395000个doc一共27GB内存
    # 读进所有395000个doc并存为PureHandsReader一共27GB内存
    # 移除掉rawstr之后一共22GB内存
    # 但是ReplayEngine的变量太多，占用的内存非常大，是不能够全部存入内存的

if __name__ == "__main__":
    # getinmemoryhands()
    t = TaskSubmitter()
    t.run()

    # rsd = ResultDealer()
    # rsd.start()

    # testdocsize()