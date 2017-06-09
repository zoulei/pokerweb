import Constant
import DBOperater
import handsinfocommon
import copy
import believeinterval
import math

class JoinrateRepairer:
    def __init__(self, ftdata):
        self.ftdata  =ftdata

    def repairdata(self):
        self.combine(Constant.HANDSTHRE,Constant.STATETHRE)
        self.repair(Constant.BELIEVERATE,Constant.FILTERHANDS)

    def enoughdata(self,betbbdata,handsthre, instancethre):
        mininstance = instancethre
        for payoffrate in betbbdata:
            if betbbdata[payoffrate]["sum"] >= handsthre:
                mininstance -= 1
                if mininstance == 0:
                    return True
        return False

    def combineinto(self,posdata,betbb,combinedbetbb):
        for key in posdata[betbb].keys():
            posdata[betbb][key] += posdata[combinedbetbb][key]
            del posdata[combinedbetbb]

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

    def caloffset(self,payoffratedata,intervaldata,joinratedata):
        offset = 0
        for idx in xrange(len(payoffratedata)):
            repaireddata = payoffratedata[idx]
            intervallen = intervaldata[idx][1] - intervaldata[idx][0]
            vieweddata = joinratedata[idx]

            offset += math.fabs(vieweddata - repaireddata) / intervallen

        return offset

    def nextpayoffrate(self,payoffratetmp,intervaldata,datatype,step = 0.1):
        payoffratelist = intervaldata.keys()
        payoffratelist.sort(key = lambda v: int(v))
        for idx in xrange(len(payoffratetmp) - 1 , -1 , -1):
            payoffrate = payoffratelist[idx]
            payoffratetmp[idx] += 0.1
            if payoffratetmp[idx] > intervaldata[payoffrate][datatype][1]:
                payoffratetmp[idx] = intervaldata[payoffrate][datatype][0]
            else:
                return True
        else:
            return False

    def getbestpayoffratedata(self,intervaldata,joininratedata,datatype):
        payoffratelist = intervaldata.keys()
        payoffratelist.sort(key = lambda v: int(v))

        payoffratetmp = []
        for payoffrate in payoffratelist:
            payoffratetmp.append(intervaldata[payoffrate][datatype][0])

        offset = 100000
        bestpayoffrate = []
        while True:
            if self.payoffdatavalid(payoffratetmp):
                curoffset = self.caloffset(payoffratetmp,intervaldata,joininratedata)
                if curoffset < offset:
                    offset = curoffset
                    bestpayoffrate = copy.deepcopy(payoffratetmp)
            if not self.nextpayoffrate(payoffratetmp,intervaldata,datatype):
                break
        return bestpayoffrate

    def insertrepaireddata(self,betbbdata,repairedrate,datatype):
        payoffratelist = betbbdata.keys()
        payoffratelist.sort(key = lambda v: int(v))

        for idx in xrange(len(repairedrate)):
            payoffrate = payoffratelist[idx]
            betbbdata[payoffrate][datatype] = repairedrate[idx]

    def repair(self,believerate,filterhands):
        believeintervaldata = {}
        joinratedata = {}

        for pos,posdata in self.repairedftata.items():
            believeintervaldata[pos] = {}
            joinratedata[pos] = {}

            for betbb, betbbdata in posdata.items():
                believeintervaldata[pos][betbb] = {}
                joinratedata[pos][betbb] = {}

                for payoffrate, payoffratedata in betbbdata.items():
                    believeintervaldata[pos][betbb][payoffrate] = {}
                    joinratedata[pos][betbb][payoffrate] = {}

                    believeintervaldict = believeintervaldata[pos][betbb][payoffrate]
                    joinratedict = joinratedata[pos][betbb][payoffrate]

                    sumhands = sum(payoffratedata.values())
                    if sumhands < filterhands:
                        continue
                    callhands = payoffratedata["call"] + payoffratedata["raise"]
                    raisehands = payoffratedata["raise"]

                    believeintervaldict["call"] = believeinterval.calcBin(callhands, sumhands, believerate)
                    believeintervaldict["raise"] = believeinterval.calcBin(raisehands, sumhands, believerate)
                    joinratedict["call"] = callhands * 1.0 / sumhands
                    joinratedict["raise"] = raisehands * 1.0 / sumhands

                repairedcalldata = self.getbestpayoffratedata(believeintervaldata[pos][betbb],joinratedata[pos][betbb],"call")
                repairedraisedata = self.getbestpayoffratedata(believeintervaldata[pos][betbb],joinratedata[pos][betbb],"raise")

                self.insertrepaireddata(betbbdata,repairedcalldata,"call")
                self.insertrepaireddata(betbbdata,repairedraisedata,"raise")


# key order,{pos, how many bb, payoffrate}
def tongjifirstturnstate(handsinfo,anti):
    if "showcard" not in handsinfo:
        print handsinfo["_id"]
    # if len(handsinfo["data"])
    showcard = handsinfo["showcard"]
    if not (showcard >= 0 or showcard == -3):
        return

    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        prefloprange = {"_id":Constant.PREFLOPRANGEDOC,"ftdata":{}}
    else:
        prefloprange = result.next()
        if "ftdata" not in prefloprange:
            prefloprange["ftdata"] = {}

    playerquantitiy = len(handsinfo["data"][0][2])
    if playerquantitiy < 6:
        return
    preflopaction = handsinfo["data"][1]
    ftaction = preflopaction[:playerquantitiy]

    bb = handsinfocommon.readbb(handsinfo)
    #anti = handsinfocommon.readanti(handsinfo)

    betvalue = bb
    total = anti * playerquantitiy + bb + bb / 2

    poslist = range(playerquantitiy - 2,0, -1)
    poslist.extend([9,8])
    # print ftaction
    for idx,pos in enumerate(poslist):
        if idx  == len(ftaction):
            continue
        action ,value = ftaction[idx]

        needtobet = betvalue
        if pos == 9:
            needtobet -= bb/2
        elif pos == 8:
            needtobet -= bb

        if needtobet != 0:
            payoffrate = total * 1.0 / needtobet
        else:
            payoffrate = 10000



        # betvalue / bb , pos ,round(payoffrate * 2) * 0.5
        # action just think about raise and call and fold
        ftdata = prefloprange["ftdata"]
        if str(pos) not in ftdata:
            ftdata[str(pos)] = {}
        ftdata_pos = ftdata[str(pos)]

        if betvalue / bb == 0:
            print handsinfo["_id"]
            print betvalue,bb,idx,action,value

        if str(betvalue / bb) not in ftdata_pos:
            ftdata_pos[str(betvalue / bb)] = {}
        ftdata_pos_bet = ftdata_pos[str(betvalue / bb)]
        normalpayoff = int(round(payoffrate * 2)) * 5
        if pos == 9 and betvalue == bb and normalpayoff == 45:
            print "info: ",total, needtobet,payoffrate,normalpayoff,handsinfo["_id"]
        if str(normalpayoff) not in ftdata_pos_bet:
            ftdata_pos_bet[str(normalpayoff)] = {"call":0,"raise":0,"fold":0}
        curstate = ftdata_pos_bet[str(normalpayoff)]
        if action == 1 or action == -1:
            curstate["fold"] += 1
        elif action == 2:
            curstate["raise"] += 1

            if (betvalue >= value):
                break

            betvalue = value
            total += value
        elif action == 3 or action == 6:
            curstate["call"] += 1
            total += betvalue
        elif action == 4:
            if value <= betvalue:
                 curstate["call"] += 1
            else:
                givepayoff = (value + total) * 1.0 / ( value - betvalue)
                givepayoff = handsinfocommon.roundhalf(givepayoff)
                if givepayoff <= 2.5:
                    curstate["raise"] += 1
                else:
                    curstate["call"] += 1
                betvalue = value
            total += value
        elif action == 12:
            break

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC},prefloprange,True)

def tongjijoinrate():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        return
    preflopdoc = result.next()
    joinratedoc = {}
    preflopdoc[Constant.JOINRATEDATA] = joinratedoc

    ftdata = preflopdoc[Constant.FTDATA]
    for pos, posdata in ftdata.items():
        if pos not in joinratedoc:
            joinratedoc[pos] = {}
        for betbb, betbbdata in posdata.items():
            if betbb not in joinratedoc[pos]:
                joinratedoc[pos][betbb] = {}
            for payoffrate, payoffratedata in betbbdata.items():
                if payoffrate not in joinratedoc[pos][betbb]:
                    joinratedoc[pos][betbb][payoffrate] = {}
                curdict = joinratedoc[pos][betbb][payoffrate]
                sumhands = sum(payoffratedata.values())
                curdict["sum"] = sumhands
                for action, value in payoffratedata.items():
                    curdict[action] = round(value * 1.0 / sumhands * 100,1)
                curdict["call"] += curdict["raise"]
                curdict["call"] = round(curdict["call"],1)

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC},preflopdoc,True)

def repairjoinrate():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        return
    preflopdoc = result.next()

    ftdata = preflopdoc[Constant.FTDATA]
    repairer = JoinrateRepairer(ftdata)
    repairer.repairdata()
    preflopdoc[Constant.REPAIRJOINRATE] = repairer.repairedftata

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC},preflopdoc,True)

def removepreflopdoc():
    DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})

def tongjiftmain():
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{})
    for handsinfo in result:
        # if handsinfo["_id"] == "35357006093039820170526040210":
        tongjifirstturnstate(handsinfo, Constant.ANTI)

if __name__ == "__main__":
    removepreflopdoc()
    tongjiftmain()
    tongjijoinrate()
    repairjoinrate()