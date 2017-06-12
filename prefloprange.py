import Constant
import DBOperater
import handsinfocommon
import copy
import believeinterval
import math
import pprint
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
                posdata[betbb][key] = {"call":0,"fold":0,"raise":0}
            if key not in posdata[combinedbetbb]:
                posdata[combinedbetbb][key] = {"call":0,"fold":0,"raise":0}

        for key in keylist:
            betbbdata = posdata[betbb].get(key)
            combineddata = posdata[combinedbetbb].get(key)
            for key in betbbdata.keys():
                betbbdata[key] += combineddata[key]
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
        for idx in xrange(1,len(repairedrate)):
            maxjoinrate = max(repairedrate[:idx])
            if repairedrate[idx] >= repairedrate[idx - 1]:
                continue
            joinrate = repairedrate[idx]
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
                joinrate = round(joinrate+0.001,3)
            repairedrate[idx] = bestjoinrate
            for i in xrange(idx):
                if repairedrate[i] > bestjoinrate:
                    repairedrate[i] = bestjoinrate

        return repairedrate

    def getbestdownpayoffratedata(self,intervaldata,joininratedata,datatype):
        payoffratelist = intervaldata.keys()
        payoffratelist.sort(key = lambda v: int(v))

        repairedrate = []
        for payoffrate in payoffratelist:
            repairedrate.append(joininratedata[payoffrate][datatype])
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
                joinrate = round(joinrate-0.001,3)
            repairedrate[idx] = bestjoinrate
            for i in xrange(idx):
                if repairedrate[i] < bestjoinrate:
                    repairedrate[i] = bestjoinrate

        return repairedrate

    def getbestpayoffratedata(self,intervaldata,joininratedata,datatype,sorttype="up"):
        if sorttype == "up":
            return self.getbestuppayoffratedata(intervaldata,joininratedata,datatype)
        elif sorttype == "down":
            return self.getbestdownpayoffratedata(intervaldata,joininratedata,datatype)

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
                # if betbb != "1":
                #     continue
                believeintervaldata[pos][betbb] = {}
                joinratedata[pos][betbb] = {}

                for payoffrate, payoffratedata in betbbdata.items():

                    sumhands = sum(payoffratedata.values())
                    payoffratedata["sum"] = sumhands
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

                repairedcalldata = self.getbestpayoffratedata(believeintervaldata[pos][betbb],joinratedata[pos][betbb],"call","up")
                repairedraisedata = self.getbestpayoffratedata(believeintervaldata[pos][betbb],joinratedata[pos][betbb],"raise","down")
                if pos == "9" and betbb == "1":
                    print "+"*100
                    print repairedcalldata
                    print repairedraisedata
                    pp.pprint(believeintervaldata[pos][betbb])
                    pp.pprint(joinratedata[pos][betbb])
                self.insertrepaireddata(betbbdata,repairedcalldata,"call")
                self.insertrepaireddata(betbbdata,repairedraisedata,"raise")
                self.calfoldrate(betbbdata)
                print "betbbdata"
                pp.pprint( betbbdata)
                print "repairedcalldata: ",repairedcalldata
                print "repairedraisedata: ",repairedraisedata


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

        haveinvested = 0
        if pos == 9:
            haveinvested = bb/2
        elif pos == 8:
            haveinvested = bb

        # betvalue / bb , pos ,round(payoffrate * 2) * 0.5
        # action just think about raise and call and fold
        ftdata = prefloprange["ftdata"]
        if str(pos) not in ftdata:
            ftdata[str(pos)] = {}
        ftdata_pos = ftdata[str(pos)]

        if betvalue / bb == 0:
            print handsinfo["_id"]
            print betvalue,bb,idx,action,value

        betbb = int((betvalue + 0.5 * bb) / bb)

        if str(betbb) not in ftdata_pos:
            ftdata_pos[str(betbb)] = {}
        ftdata_pos_bet = ftdata_pos[str(betbb)]
        normalpayoff = int(round(payoffrate * 2)) * 5
        # print pos,betvalue,bb,normalpayoff
        # if pos == 9 and betbb == 1 and normalpayoff < 55:
        #     print "info: ",total, needtobet,payoffrate,normalpayoff,handsinfo["_id"],betvalue,int((betvalue + 0.5) / bb),bb,betbb

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
            total += value -haveinvested
        elif action == 3 or action == 6:
            curstate["call"] += 1
            total += betvalue-haveinvested
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
            total += value-haveinvested
        elif action == 12:
            break

    # if "9" in prefloprange["ftdata"] and "1" in prefloprange["ftdata"]["9"] and "45" in prefloprange["ftdata"]["9"]["1"]:
    #     print handsinfo["_id"]
    #     asbc

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
    idx = 0
    for handsinfo in result:
        # if handsinfo["_id"] == "35357006093039820170526040210":
        idx += 1
        if idx % 1000 == 0:
            print idx
        tongjifirstturnstate(handsinfo, Constant.ANTI)

if __name__ == "__main__":
    # removepreflopdoc()
    #
    # tongjiftmain()
    # tongjijoinrate()
    repairjoinrate()