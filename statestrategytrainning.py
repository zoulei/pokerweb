# -*- coding:utf-8 -*-
from statestrategycalculator import *
from Constant import *
import DBOperater
from stateinfocalculator import *
import threading
import handsengine
from TraverseHands import TraverseHands
import hunlgame
import os
import time
from handsdistribution import RangeState

def submitmainfunc(para):
    handsinfo, state, stateid, stateturn, stateidx= para
    prefloprangeengine = handsengine.getprefloprangeobj()
    curturn = state.getstateturn()
    replay = stateinfocalculator.StateReaderEngine(handsinfo)
    if replay.m_handsinfo.getturncount() < 2:
        return []
    replay.traversepreflop()
    pvhand = replay.m_handsinfo.gethand(replay.m_nextplayer)
    if pvhand is None:
        return []
    oppohands = []
    for pos, inpoolstate in enumerate(replay.m_inpoolstate):
        if inpoolstate != 0 and pos != replay.m_nextplayer:
            oppohands.append(
                handsdistribution.HandsDisQuality(prefloprangeengine.gethandsinrange(replay.m_prefloprange[pos])))
    board = replay.m_handsinfo.getboardcard()[:3]
    statesimilar = replay.getstate(curturn, 0) - state
    # 把pvhand, board, oppohands, statesimilar都返回，由主函数统一写文件
    action = replay.m_handsinfo.getspecificturnrealbetdata(curturn)[0][1]
    return [stateid, stateturn, stateidx, pvhand, board, oppohands, statesimilar, action]

class SubmitTraverseMain(TraverseHands):
    def initdata(self):
        self.m_idx = 0

    def parttraverse(self, idx):
        result = TraverseHands.parttraverse(self, idx)
        for subresult in result:
        # for stateid, stateturn, stateidx, pvhand, board, oppohands, statesimilar in result:
            # 这里把东西写入文件
            if not subresult:
                continue
            stateid, stateturn, stateidx, pvhand, board, oppohands, statesimilar, action = subresult
            RangeState(board, pvhand, oppohands).checkparavalid()
            fnamelist = os.listdir(SUBMITTASKDIR)
            while len(fnamelist) >= FILEQUANTITYTHRE:
                time.sleep(10)
            fname = "_".join([stateid, str(stateturn), str(stateidx), str(self.m_idx)])
            self.m_idx += 1
            fname = fname.replace(" ", "")
            ofile = open(TEMPSUBMITTASKDIR + fname, "w")
            ofile.write(stateid + "\n")
            ofile.write(str(stateturn)+" "+str(stateidx)+"\n")
            ofile.write(str(statesimilar)+" "+action+"\n")
            ofile.write("".join([str(v) for v in pvhand.get()])+" "+"".join([str(v) for v in board])+"\n")
            for handsdis in oppohands:
                # "0 0" 为标识符，一个该标识符表示接下来的数据为一个新的对手的手牌分布
                ofile.write(str(len(handsdis))+"\n")
                for hands,rate in handsdis.items():
                    ofile.write("".join([str(v) for v in hands.get()])+" "+str(rate)+"\n")
            ofile.close()
            os.system("mv "+TEMPSUBMITTASKDIR + fname +" "+SUBMITTASKDIR+fname)

class TaskSubmitter(threading.Thread):
    def __init__(self, db = HANDSDB, clt = STATEINFOHANDSCLT):
        threading.Thread.__init__(self)
        self.m_db = db
        self.m_clt = clt

    def run(self):
        result = DBOperater.Find(self.m_db, self.m_clt, {})
        idx = 0
        for doc in result:
            replay = stateinfocalculator.StateReaderEngine(doc)
            if replay.m_handsinfo.getturncount() == 1:
                continue
            state = replay.getstate(2, 0)
            self.calstrategyforspecificstate(state, doc["_id"], 2, 0)
            idx += 1
            if idx == 100:
                break

    def calstrategyforspecificstate(self, state, stateid, turnidx, actionidx):
        # 根据秀牌数据提交强化学习数据
        submittaskengine = SubmitTraverseMain(self.m_db, self.m_clt, func=submitmainfunc, sync=True, step=10000,
                                          para=[state, stateid, turnidx, actionidx])
        submittaskengine.traverse()

class ResultDealer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.m_taskdata = TaskData()

    def run(self):
        fnamelist = os.listdir(TASKRESULTDIR)
        for fname in fnamelist:
            ifile = open(fname)
            stateid = ifile.readline().strip()
            stateturn, stateidx = [int(v) for v in ifile.readline().strip().split(SPACE)]
            actiondisdata = self.m_taskdata.getdata(stateid, stateturn, stateidx).getdata()
            for line in ifile:
                hpidx, action, weight = line.strip().split(SPACE)
                actiondisdata.addaction(hpidx, action, weight)
        # 这里还缺少了一个写结果的步骤，这个之后再想怎么写

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

if __name__ == "__main__":
    t = TaskSubmitter()
    t.start()
