import Constant
import DBOperater
import handsinfocommon
import copy
import believeinterval
import math
import tongjihandsinfo
import pprint
pp = pprint.PrettyPrinter(indent=4)

class prefloprangge:
    def __init__(self):
        result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
        self.m_rawdata = result.next()

    def getrange(self,curturn,betlevel,ftlevelkey,stlevelkey,thlevelkey,action):
        if not action:
            return
        targetfield = Constant.getpreflopjoinratefield(curturn,betlevel)
        targetdoc = self.m_rawdata[targetfield]

        for key in [ftlevelkey,stlevelkey,thlevelkey]:
            nearestftlevelkey = handsinfocommon.getnearestkey(key,targetdoc.keys())
            targetdoc = targetdoc[nearestftlevelkey]

        return targetdoc[action]



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
            if pos != "9":
                continue
            for betbb, betbbdata in posdata.items():
                if betbb != "24":
                    continue
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
                if pos == "9" and betbb == "24":
                    print "+"*100
                    print repairedcalldata
                    print repairedraisedata
                    pp.pprint(believeintervaldata[pos][betbb])
                    pp.pprint(joinratedata[pos][betbb])
                    pp.pprint(betbbdata)
                self.insertrepaireddata(betbbdata,repairedcalldata,"call")
                self.insertrepaireddata(betbbdata,repairedraisedata,"raise")
                self.calfoldrate(betbbdata)
                print "betbbdata"
                pp.pprint( betbbdata)
                print "repairedcalldata: ",repairedcalldata
                print "repairedraisedata: ",repairedraisedata


# key order,{pos, how many bb, payoffrate}
def tongjifirstturnstate(handsinfo,anti):
    handsdata = handsinfo
    if "showcard" not in handsinfo:
        print handsinfo["_id"]
    # if len(handsinfo["data"])
    showcard = handsinfo["showcard"]
    if not (showcard >= 0 or showcard == -3):
        return

    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        prefloprange = {
            "_id":Constant.PREFLOPRANGEDOC,
            "ftdata":{},
            Constant.FT3BETDATA:{},
            Constant.FT4BETDATA:{},
            Constant.FT5BETDATA:{},

            Constant.STDATA:{},
            Constant.ST3BETDATA:{},
            Constant.ST4BETDATA:{},
            Constant.ST5BETDATA:{}
        }
    else:
        prefloprange = result.next()
        # if "ftdata" not in prefloprange:
        #     prefloprange["ftdata"] = {}
        # if Constant.FT3BETDATA not in prefloprange:
        #     prefloprange[Constant.FT3BETDATA] = {}
        # if Constant.FT4BETDATA not in prefloprange:
        #     prefloprange[Constant.FT4BETDATA] = {}
        # if Constant.FT5BETDATA not in prefloprange:
        #     prefloprange[Constant.FT5BETDATA] = {}

    playerquantitiy = len(handsinfo["data"][0][2])
    if playerquantitiy < 6:
        return
    preflopaction = handsinfo["data"][1]
    # ftaction = preflopaction[:playerquantitiy]
    ftaction = preflopaction
    bb = handsinfocommon.readbb(handsinfo)
    #anti = handsinfocommon.readanti(handsinfo)

    betvalue = bb
    total = anti * playerquantitiy + bb + bb / 2

    # poslist uses virtual pos, not the real pos on screen
    poslist = range(playerquantitiy - 2,0, -1)
    poslist.extend([9,8])
    # print ftaction

    # this is used to calculate payoffrate for those player call in,
    # since which generates separate pot.
    bethis = {9:bb/2,8:bb}

    betlevel = 1

    # inpool = handsdata[0][2]

    # start from index 1, value 0 means fold, value 1 means in pool, value 2 means all in
    # this is different from the code in tongjihandsinfo.
    inpoolstate = [0]*10
    for pos in poslist:
        inpoolstate[pos] = 1
    # curplayer = poslist[0]
    jumpplayerquantity = 0
    raiser = 0
    raisevalue = bb

    for idx,pos in enumerate(poslist*2):
        curturn = idx / len(poslist) + 1
        # if curturn == 3:
        #     break
        # print "=====================:",idx,pos,inpoolstate[pos],jumpplayerquantity
        if inpoolstate[pos] != 1:
            # this one has folded his hands or all in.
            jumpplayerquantity += 1
            # print "continue"
            continue
        if idx - jumpplayerquantity == len(ftaction):
            # print "break"
            # print idx - jumpplayerquantity,len(ftaction)
            break

        # print "-------------------------------:",idx,pos,curturn,inpoolstate

        action ,value = ftaction[idx - jumpplayerquantity]

        if value != 0 and value < betvalue:
            # call all in
            needtobet = value
            if needtobet < bb:
                needtobet = bb

            if pos in bethis:
                needtobet -= bethis[pos]
            if needtobet != 0:
                seppot = anti * playerquantitiy + bb + bb / 2
                for hispos,hisbetvalue in bethis.items():
                    if hisbetvalue > value:
                        seppot += value
                    else:
                        seppot += hisbetvalue
                if 9 in bethis:
                    seppot -= bb /2
                payoffrate = seppot * 1.0 / needtobet
            else:
                payoffrate = 10000

            # since call all in, betbb depends on his remaining stack, NOT the real betbb
            if value < bb:
                betbb = int((bb + 0.5 * bb) / bb)
            else:
                betbb = int((value + 0.5 * bb) / bb)

        else:
            needtobet = betvalue
            if pos in bethis:
                needtobet -= bethis[pos]
            if needtobet != 0:
                payoffrate = total * 1.0 / needtobet
            else:
                payoffrate = 10000

            betbb = int((betvalue + 0.5 * bb) / bb)

        if payoffrate < 0:
            print handsinfo["_id"], payoffrate, idx, pos, curturn

        normalpayoff = int(round(payoffrate * 2)) * 5
        haveinvested = 0
        if pos == 9:
            haveinvested = bb/2
        elif pos == 8:
            haveinvested = bb

        if betvalue / bb == 0:
            print handsinfo["_id"]
            print betvalue,bb,idx,action,value

        if curturn == 1:
            if betlevel < 3:
                ftdata = prefloprange[Constant.FTDATA]
            elif betlevel == 3:
                ftdata = prefloprange[Constant.FT3BETDATA]
            elif betlevel == 4:
                ftdata = prefloprange[Constant.FT4BETDATA]
            elif betlevel >= 5:
                ftdata = prefloprange[Constant.FT5BETDATA]

            if str(pos) not in ftdata:
                ftdata[str(pos)] = {}
            ftdata_pos = ftdata[str(pos)]

            if str(betbb) not in ftdata_pos:
                ftdata_pos[str(betbb)] = {}
            ftdata_pos_bet = ftdata_pos[str(betbb)]

            # print pos,betvalue,bb,normalpayoff
            # if pos == 9 and betbb == 1 and normalpayoff < 55:
            #     print "info: ",total, needtobet,payoffrate,normalpayoff,handsinfo["_id"],betvalue,int((betvalue + 0.5) / bb),bb,betbb

            if str(normalpayoff) not in ftdata_pos_bet:
                ftdata_pos_bet[str(normalpayoff)] = {"call":0,"raise":0,"fold":0}
            curstate = ftdata_pos_bet[str(normalpayoff)]

            if betlevel < 3 and betbb > 10:
                print handsinfo["_id"], betbb

        else:
            # second turn related
            if betlevel < 3:
                ftdata = prefloprange[Constant.STDATA]
            elif betlevel == 3:
                ftdata = prefloprange[Constant.ST3BETDATA]
            elif betlevel == 4:
                ftdata = prefloprange[Constant.ST4BETDATA]
            elif betlevel >= 5:
                ftdata = prefloprange[Constant.ST5BETDATA]

            if pos > raiser:
                # bad position
                relativepos = 0
            elif pos < raiser:
                # good position
                relativepos = 1
            else:
                # call invalid raise.
                # when this happen, the raiser call and end the round.
                # so we can just end the for loop.
                break

            if str(relativepos) not in ftdata:
                ftdata[str(relativepos)] = {}
            ftdata_pos = ftdata[str(relativepos)]

            normalneedtobet = int( (needtobet + 0.5 * bb) / bb )
            if str(normalneedtobet) not in ftdata_pos:
                ftdata_pos[str(normalneedtobet)] = {}
            ftdata_pos_bet = ftdata_pos[str(normalneedtobet)]

            if str(normalpayoff) not in ftdata_pos_bet:
                ftdata_pos_bet[str(normalpayoff)] = {"call":0,"raise":0,"fold":0}
            curstate = ftdata_pos_bet[str(normalpayoff)]

        if action == 1 or action == -1:
            curstate["fold"] += 1
            inpoolstate[pos] = 0
        elif action == 2:
            curstate["raise"] += 1
            betlevel += 1
            raisevalue = value - betvalue
            if (betvalue >= value):
                break

            betvalue = value
            total += value -haveinvested
            raiser = pos

        elif action == 3 or action == 6:
            curstate["call"] += 1
            bethis[pos] = betvalue
            total += betvalue-haveinvested

        elif action == 4:
            if value <= betvalue:
                 curstate["call"] += 1
            else:
                if value - betvalue < raisevalue:
                    # invalid raise
                    pass
                else:
                    # valid raise
                    raiser = -1
                    raisevalue = value - betvalue

                givepayoff = (value + total - bethis.get(pos,0)) * 1.0 / ( value - betvalue)
                givepayoff = handsinfocommon.roundhalf(givepayoff)
                if givepayoff <= 3:
                    curstate["raise"] += 1
                    betlevel += 1
                else:
                    curstate["call"] += 1
                betvalue = value
            total += value-haveinvested
        elif action == 12:
            break

        bethis[pos] = value

    # if "9" in prefloprange["ftdata"] and "1" in prefloprange["ftdata"]["9"] and "45" in prefloprange["ftdata"]["9"]["1"]:
    #     print handsinfo["_id"]
    #     asbc

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC},prefloprange,True)

def tongjijoinrate():
    tongjijoinrate_(Constant.JOINRATEDATA)


def tongjijoinrate_(datafield):
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        return
    preflopdoc = result.next()
    joinratedoc = {}
    preflopdoc[datafield] = joinratedoc

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
    # result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,
    #                         {"_id":"35357006093039820170308111711"})
    idx = 0
    for handsinfo in result:
        # if handsinfo["_id"] == "35357006093039820170526040210":
        idx += 1
        if idx % 1000 == 0:
            print idx
        tongjifirstturnstate(handsinfo, Constant.ANTI)

if __name__ == "__main__":
    removepreflopdoc()

    tongjiftmain()
    # tongjijoinrate()
    # repairjoinrate()