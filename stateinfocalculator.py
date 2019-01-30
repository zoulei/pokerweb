#-*- coding:utf-8 -*-
# 这个文档中的内容主要是和state相关,
# 包括计算历史牌局的state,以及计算state之间的相似度,
# 从牌局数据中读取state等

from handsengine import ReplayEngine
from TraverseHands import TraverseMultiplayerHands
import DBOperater
import Constant
import numpy
import handsinfocommon
import traceback
import copy

# 计算一个历史牌局中的state的类,并可以将数据保存起来
# 其具体用法参见下面的mainfunc方法
class StateCalculator(ReplayEngine):
    def __init__(self,handsinfo):
        ReplayEngine.__init__(self,handsinfo)
        self.initstaterecorder()
        self.m_realbetdata = {
            Constant.TURNPREFLOP:[],
            Constant.TURNFLOP:[],
            Constant.TURNTURN:[],
            Constant.TURNRIVER:[]
        }
        self.m_preflopinpoolstate = None
        self.m_handsinfo.m_handsinfo["_id"] = self.m_handsinfo.getid().replace(" ", "_")

    def initstaterecorder(self):
        self.m_preflopstate = []
        self.m_flopstate = []
        self.m_turnstate = []
        self.m_riverstate = []

    #True is, False not
    def isopener(self,pos):
        if self.getpreflopinfomation()["raiser"] == pos:
            return True
        return False

    # True has, False not
    def hasopener(self):
        if self.getpreflopinfomation()["raiser"] != 0:
            return True
        return False

    # 1 means the best position, 0 means the worst position
    def relativepos(self,pos):
        total = self.m_remainplayer - self.m_allinplayer
        if total == 1:
            return 1
        step = 1.0 / (total - 1)
        initial = - step
        for inpoolpos,state in enumerate(self.m_inpoolstate):
            if state == 1:
                initial += step
            if inpoolpos == pos:
                return 1 - initial

    # player quantity that still need to act
    def playerquantitytoact(self):
        total = 0
        poslist = self.getposlist()
        playeridx = poslist.index(self.m_nextplayer)
        if self.m_raiser == 0:
            for pos in poslist[playeridx + 1:]:
                if self.m_inpoolstate[pos] == 1:
                    total += 1
            return total
        for pos in poslist[playeridx + 1:] + poslist[:playeridx]:
            if pos == self.m_raiser:
                return total
            elif pos == self.m_fakeraiser:
                return 0
            if self.m_inpoolstate[pos] == 1:
                total += 1
        return total

    # player quantitiy that has made action
    def playerquantityacted(self):
        if self.m_circle > 1:
            return self.m_remainplayer - self.m_allinplayer - 1
        poslist= self.getposlist()
        playeridx = poslist.index(self.m_nextplayer)
        total = 0
        for pos in poslist[:playeridx]:
            if self.m_inpoolstate[pos] == 1:
                total += 1
        return total

    # player quantity that make raise or call raise
    def raiserquantity(self):
        total = 0
        if self.m_raiser != 0:
            poslist = range(self.m_raiser,0,-1) + range(9, self.m_raiser,-1)
        else:
            poslist = self.getposlist()
        for pos in poslist:
            if pos == self.m_nextplayer:
                break
            if self.m_inpoolstate[pos] == 0:
                continue
            total += 1
        return total

    # raiser's stack pot ratio,如果没有新的raiser则不能行动的人的最大后手
    def getraiserstackpotratio(self):
        myneedtobet = self.m_betvalue - self.m_bethistory.get(self.m_nextplayer,0)
        raisermaxstack = 0
        realpot = self.m_pot + myneedtobet
        if self.m_raiser != 0:
            poslist = range(self.m_raiser,0,-1) + range(9, self.m_raiser,-1)
            posidx = poslist.index(self.m_nextplayer)
        else:
            poslist = self.getposlist()
            posidx = poslist.index(self.m_nextplayer)
        for pos in poslist[:posidx]:
            # if pos == self.m_nextplayer:
            #     break
            if self.m_inpoolstate[pos] == 0:
                continue
            if self.m_stacksize[pos] > raisermaxstack:
                raisermaxstack = self.m_stacksize[pos]
        if self.m_stacksize[self.m_nextplayer] - myneedtobet < raisermaxstack:
            raisermaxstack = self.m_stacksize[self.m_nextplayer] - myneedtobet
        if raisermaxstack < 0:
            raisermaxstack = 0
        return raisermaxstack * 1.0 / realpot

    # players need to bet stack pot ratio，还能够行动的人的最大后手
    def getneedtobetstackratio(self):
        myneedtobet = self.m_betvalue - self.m_bethistory.get(self.m_nextplayer,0)
        realpot = self.m_pot + myneedtobet
        targetmaxstack = [0,]
        if self.m_raiser != 0:
            poslist = range(self.m_nextplayer -1,0,-1) + range(9, self.m_nextplayer - 1,-1)
            posidx = poslist.index(self.m_raiser)
        else:
            poslist = self.getposlist()[::-1]
            posidx = poslist.index(self.m_nextplayer)
        for pos in poslist[:posidx]:
            if self.m_inpoolstate[pos] != 1:
                continue
            targetneedtobet = self.m_betvalue - self.m_bethistory.get(pos,0)
            targetrealpot = realpot + targetneedtobet
            targetstacksize = min(self.m_stacksize[pos]-targetneedtobet,self.m_stacksize[self.m_nextplayer]-myneedtobet)
            if targetstacksize < 0:
                targetstacksize = 0
            targetmaxstack.append(targetstacksize * 1.0 / targetrealpot)
        targetmaxstack.sort()
        return max(targetmaxstack)

    def initalplayerquantity(self,turn):
        if turn == 1:
            return self.m_handsinfo.getplayerquantity()
        if turn == 2:
            info = self.getpreflopinfomation()
        elif turn == 3:
            info = self.getflopinformation()
        elif turn == 4:
            info = self.getturninformation()
        return info["remain"] + info["allin"]

    def updatecumuinfo(self,round,actionidx):
        if round == 2 and actionidx == 0:
            self.m_preflopinpoolstate = copy.deepcopy(self.m_inpoolstate)

        curplayer = self.m_nextplayer
        statedata = {}
        statedata[Constant.STATEHANDSID] = self.m_handsinfo.getid()
        statedata[Constant.ACTIONIDX] = actionidx
        statedata[Constant.INPOOLSTATE] = self.m_inpoolstate
        statedata[Constant.NEXTPLAYER] = self.m_nextplayer
        statedata[Constant.SHOWCARD] = self.m_handsinfo.gethand(self.m_nextplayer) is not None
        statedata[Constant.ISOPENER] = self.getpreflopinfomation()["raiser"] == self.m_nextplayer
        statedata[Constant.HASOPENER] = self.getpreflopinfomation()["raiser"] != 0
        statedata[Constant.RELATIVETOOPENER] = self.getrelativepostoopener(self.m_nextplayer)
        statedata[Constant.TURN] = round
        statedata[Constant.RELATIVEPOS] = self.relativepos(self.m_nextplayer)
        statedata[Constant.REMAINTOACT] = self.playerquantitytoact()
        statedata[Constant.REMAINRAISER] = self.raiserquantity()
        statedata[Constant.POTSIZE] = self.m_pot * 1.0 / self.m_bb
        # statedata[Constant.INITIALPLAYERQUANTITY] = self.initalplayerquantity(round)
        statedata[Constant.RAISERSTACKVALUE] = self.getraiserstackpotratio()
        statedata[Constant.REMAINSTACKVALUE] = self.getneedtobetstackratio()
        statedata[Constant.CURRENTATTACKVALUE] = self.m_attack
        statedata[Constant.PREFLOPINITALPQ] = self.m_playerquantity
        if round > 1:
            statedata[Constant.PREFLOPATTACKVALUE] = self.getpreflopinfomation()["newattack"]
            statedata[Constant.AFTERFLOPATTACKVALUE] = self.m_totalattack - self.getpreflopinfomation()["newattack"]
            statedata[Constant.FLOPINITALPQ] = self.getpreflopinfomation()["remain"] + self.getpreflopinfomation()["allin"]
        else:
            statedata[Constant.PREFLOPATTACKVALUE] = 0
            statedata[Constant.AFTERFLOPATTACKVALUE] = 0
            statedata[Constant.FLOPINITALPQ] = 0
        if round > 2:
            statedata[Constant.TURNINITALPQ] = self.getflopinformation()["remain"] + self.getflopinformation()["allin"]
        else:
            statedata[Constant.TURNINITALPQ] = 0
        if round > 3:
            statedata[Constant.RIVERINITALPQ] = self.getturninformation()["remain"] + self.getturninformation()["allin"]
        else:
            statedata[Constant.RIVERINITALPQ] = 0
        actionpos = self.m_handsinfo.getspecificturnbetdata(round)[actionidx][0]
        if actionpos != self.m_nextplayer:
            [self.m_preflopstate,self.m_flopstate,self.m_turnstate,self.m_riverstate][round-1].append({})
            ReplayEngine.updatecumuinfo(self,round,actionidx)
        else:
            ReplayEngine.updatecumuinfo(self,round,actionidx)
            statedata[Constant.ODDS] = self.m_laststate["odds"]
            [self.m_preflopstate,self.m_flopstate,self.m_turnstate,self.m_riverstate][round-1].append(copy.deepcopy(statedata))

        self.m_realbetdata[self.m_handsinfo.getturnstr(round)].append([curplayer,self.actiontransfer(self.m_lastaction),self.m_lastattackrate])

    # 存储计算得到的本牌局的state信息,并存储到一个新的数据集中
    def savestatedata(self):
        targetdoc = self.m_handsinfo.m_handsinfo["data"]
        targetdoc[Constant.PREFLOPRANGEDOC] = self.m_prefloprange
        targetdoc[Constant.PREFLOPINPOOLSTATE] = self.m_preflopinpoolstate
        for k in self.m_realbetdata.keys():
            if not len(self.m_realbetdata[k]):
                del self.m_realbetdata[k]
        targetdoc[Constant.REALBETDATA] = self.m_realbetdata
        targetdoc["STATEINFO"] = {}
        targetdoc = targetdoc["STATEINFO"]
        targetdoc["PREFLOP"] = self.m_preflopstate
        if self.m_flopstate:
            targetdoc["FLOP"] = self.m_flopstate
        if self.m_turnstate:
            targetdoc["TURN"] = self.m_turnstate
        if self.m_riverstate:
            targetdoc["RIVER"] = self.m_riverstate
        del self.m_handsinfo.m_handsinfo["rawstr"]
        DBOperater.ReplaceOne(Constant.HANDSDB,Constant.STATEINFOHANDSCLT,{"_id":self.m_handsinfo.getid()},self.m_handsinfo.m_handsinfo,True)

# StateCalculator 的使用示例,同时也是用来多线程处理历史牌局的处理函数
def mainfunc(handsinfo):
    try:
        cal = StateCalculator(handsinfo)
        cal.traversealldata()
        cal.savestatedata()
        return True
        # print handsinfo["_id"]
    except:
        print "===============error=============="
        print "error : ", handsinfo["_id"]
        DBOperater.DeleteData(Constant.HANDSDB,Constant.HANDSCLT,{"_id":handsinfo["_id"]})
        handsinfocommon.pp.pprint(handsinfo)
        traceback.print_exc()
        return False
        # raise

# state类,类名中的byexpert指的是这个state的设计是基于专家的领域知识
class StateByExpert:
    # 本类并不由用户直接调用其构造函数产生,而是通过StateReaderEngine类从存储了state信息的牌局文档中读取
    def __init__(self,stateinfo):
        self.m_stateinfo = stateinfo

    def __getitem__(self, item):
        return self.m_stateinfo[item]

    # 获取该state属于哪一轮
    def getstateturn(self):
        return self.m_stateinfo[Constant.TURN]

    # 获取该state是否能够进行check
    def ischeckavailable(self):
        if self.m_stateinfo[Constant.CURRENTATTACKVALUE] == 0:
            return True
        else:
            return False

    # 计算两个state的相似度的方法,返回0-1
    def similar(self, other):
        # handsinfocommon.pp.pprint(self.m_stateinfo)
        # handsinfocommon.pp.pprint(other.m_stateinfo)
        for attr in [Constant.ISOPENER,Constant.HASOPENER,Constant.RELATIVETOOPENER,Constant.TURN]:
            if self.m_stateinfo[attr] != other.m_stateinfo[attr]:
                return 0
        attrsimilar = []
        for attr,weight in [[Constant.RELATIVEPOS,200],]:
            cursimilar = 1 - abs(self.m_stateinfo[attr] - other.m_stateinfo[attr])
            attrsimilar.append([cursimilar,weight])
        for attr,maxima,weight in [[Constant.REMAINTOACT,0,100],[Constant.REMAINRAISER,0,100],[Constant.ODDS,10,100],
                            [Constant.POTSIZE,200,100],
                            [Constant.RAISERSTACKVALUE,[7,3,3,2][self.m_stateinfo[Constant.TURN]-1],50],
                            [Constant.REMAINSTACKVALUE,[7,3,3,2][self.m_stateinfo[Constant.TURN]-1],50],
                            [Constant.PREFLOPINITALPQ,0,200],[Constant.FLOPINITALPQ,0,200],
                            [Constant.TURNINITALPQ,0,200],[Constant.RIVERINITALPQ,0,200]]:
            maxvalue = max(self.m_stateinfo[attr],other.m_stateinfo[attr])
            if maxima == 0:
                maxima = maxvalue
            minvalue = min(self.m_stateinfo[attr],other.m_stateinfo[attr],maxima)
            maxvalue = min(maxvalue,maxima)
            cursimilar = (minvalue+1) * 1.0 / (maxvalue+1)
            attrsimilar.append([cursimilar,weight])
        for attr,k,maxima,weight in [[Constant.PREFLOPATTACKVALUE,4,3,200],[Constant.CURRENTATTACKVALUE,4,3,200],
                              [Constant.AFTERFLOPATTACKVALUE,4,3,200]]:
            myvalue = min(self.m_stateinfo[attr],maxima)
            othervalue = min(other.m_stateinfo[attr],maxima)
            cursimilar = numpy.exp(-1 * k * abs(myvalue-othervalue))
            attrsimilar.append([cursimilar,weight])
        similar = 1.0 * sum([v[0]*v[1] for v in attrsimilar]) / sum([v[1] for v in attrsimilar])
        return similar

    def __sub__(self, other):
        return self.similar(other)

# 读取牌局数据中的state的类
class StateReaderEngine(ReplayEngine):
    # 读取指定轮的所有state原始信息
    def getspecificturnstatedata(self,turn):
        return self.m_handsinfo.m_handsinfo["data"]["STATEINFO"].get(self.m_handsinfo.getturnstr(turn),[])

    # 读取指定轮第指定次行动时的state
    def getstate(self,turn, actionidx):
        return StateByExpert(self.getspecificturnstatedata(turn)[actionidx])

    # 读取指定轮的所有state
    def getallstate(self, turn):
        staterawinfo = self.m_handsinfo.m_handsinfo["data"]["STATEINFO"].get(self.m_handsinfo.getturnstr(turn),[])
        return [StateByExpert(v) for v in staterawinfo]

    def getprefloprange(self):
        return self.m_handsinfo["data"][Constant.PREFLOPRANGEDOC]

    def getpreflopinpoolstate(self):
        return self.m_handsinfo["data"][Constant.PREFLOPINPOOLSTATE]

# 测试state相似度计算的代码
def teststatesimilarity():
    targethandsid = "2017-12-09 23:02:37 88"
    result = DBOperater.Find(Constant.HANDSDB,Constant.STATEINFOHANDSCLT,{"_id":targethandsid})
    targetstatereader = StateReaderEngine(result.next())
    turn = 2
    targetstate = targetstatereader.getstate(turn,0)

    result1 = DBOperater.Find(Constant.HANDSDB,Constant.STATEINFOHANDSCLT,{})
    for doc in result1:
        handsinfocommon.pp.pprint(doc)
        curstatereader = StateReaderEngine(doc)
        if curstatereader.m_handsinfo.getplayerquantity() == 2:
            continue
        for idx,statedata in enumerate(curstatereader.getspecificturnstatedata(turn)):
            print curstatereader.m_handsinfo.getid(),"\t",idx,":",StateByExpert(statedata).similar(targetstate)
            raw_input()
            if idx > 2:
                break

class countshowcardstatequan(TraverseMultiplayerHands):
    def initdata(self):
        self.m_showcard = 0

    def mainfunc(self, handsinfo):
        replay = StateReaderEngine(handsinfo)
        turncount = replay.m_handsinfo.getturncount()
        for turn in xrange(2, turncount+1):
            for state in replay.getallstate(turn):
                if state[Constant.SHOWCARD]:
                    self.m_showcard += 1

def countshowcard():
    tvs = countshowcardstatequan(Constant.HANDSDB,Constant.STATEINFOHANDSCLT)
    tvs.traverse()
    print "showcard:", tvs.m_showcard

if __name__ == "__main__":
    # TraverseHandsWithReplayEngine(Constant.HANDSDB,Constant.HANDSCLT,sync=False,func=mainfunc,handsid="2017-12-10 23:32:41 255").traverse()

    # 下面这句话用于将库中的牌谱都计算完state信息,并存入state数据库中
    TraverseMultiplayerHands(Constant.HANDSDB,Constant.HANDSCLT,sync=False,func=mainfunc,handsid="").traverse()

    # teststatesimilarity()

    # 下面这个是用于计算有多少个state是秀了牌的state，结果是一共有572043个秀了牌的state
    # countshowcard()
