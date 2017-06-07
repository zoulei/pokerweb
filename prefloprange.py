import Constant
import DBOperater
import handsinfocommon
import copy

class Joinrate:
    def __init__(self, ftdata):
        self.ftdata  =ftdata

    def combineposdata(self, pos):
        posdata = self.repairedftata[pos]
        betbblist = posdata.keys()
        betbblist.sort(key = lambda v:int(v))

        idx = 1
        curidx = 0
        while curidx < len(betbblist):
            betbb = betbblist[curidx]
            if enoughdata(posdata[betbb]):
                curidx = idx
                idx += 1
            elif idx == len(betbblist):
                # no more data, combine the last two betbb data and break
                pass
                break
            else:
                # combine idx and curidx
                pass
                # combine idx and curidx
                idx += 1

    def combine(self):
        self.repairedftata = copy.deepcopy(self.ftdata)
        for pos in self.ftdata.keys():
            self.combineposdata(pos)



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
        if pos == 9 and betvalue == bb and normalpayoff > 170:
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

    DBOperater.ReplaceOne(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC},preflopdoc,True)

def enoughdata(betbbdata,handsthre, instancethre):
    mininstance = instancethre
    for payoffrate in betbbdata:
        if betbbdata[payoffrate]["sum"] >= handsthre:
            mininstance -= 1
            if mininstance == 0:
                return True
    return False

def combinepayoffrate(posdata):
    betbblist = posdata.keys()
    betbblist.sort(key = lambda v:int(v))
    combineresult = []

    for idx in xrange(len(betbblist)):
        betbb = betbblist[idx]
        betbbdata = posdata[betbb]

        if enoughdata(betbbdata, Constant.HANDSTHRE, Constant.STATETHRE):
            combineresult


def repairjoinrate():
    result = DBOperater.Find(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})
    if result.count() == 0:
        return
    preflopdoc = result.next()
    repairratedoc = {}
    preflopdoc[Constant.REPAIRJOINRATE] = repairratedoc

    joinratedoc = preflopdoc[Constant.JOINRATEDATA]
    for pos, posdata in joinratedoc.items():
        if pos not in repairratedoc:
            repairratedoc[pos] = {}

        betbblist = posdata.keys()
        betbblist.sort(key = lambda v:int(v))

        for betbb, betbbdata in posdata.items():
            if betbb not in repairratedoc[pos]:
                repairratedoc[pos][betbb] = {}

            if not enoughdata(betbbdata, Constant.HANDSTHRE, Constant.STATETHRE):


            payoffratelist = betbbdata.keys()
            payoffratelist.sort(key= lambda v:int(v))






            for payoffrate, payoffratedata in betbbdata.items():
                if payoffrate not in joinratedoc[pos][betbb]:
                    joinratedoc[pos][betbb][payoffrate] = {}
                curdict = joinratedoc[pos][betbb][payoffrate]
                sumhands = sum(payoffratedata.values())
                curdict["sum"] = sumhands
                for action, value in payoffratedata.items():
                    curdict[action] = round(value * 1.0 / sumhands * 100,1)
                curdict["call"] += curdict["raise"]

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