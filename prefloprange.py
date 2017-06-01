import Constant
import DBOperater
import handsinfocommon

def tongjifirstturnstate(handsinfo):
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
    preflopaction = handsinfo["data"][1]
    ftaction = preflopaction[:playerquantitiy]

    bb = handsinfocommon.readbb(handsinfo)
    anti = handsinfocommon.readanti(handsinfo)

    betvalue = bb
    total = anti * playerquantitiy + bb + bb / 2

    poslist = range(playerquantitiy - 2,0, -1)
    poslist.extend([9,8])
    print ftaction
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
        if str(betvalue / bb) not in ftdata_pos:
            ftdata_pos[str(betvalue / bb)] = {}
        ftdata_pos_bet = ftdata_pos[str(betvalue / bb)]
        normalpayoff = int(round(payoffrate * 2))
        if str(normalpayoff) not in ftdata_pos_bet:
            ftdata_pos_bet[str(normalpayoff)] = {"call":0,"raise":0,"fold":0}
        curstate = ftdata_pos_bet[str(normalpayoff)]
        if action == 1 or action == -1:
            curstate["fold"] += 1
        elif action == 2:
            curstate["raise"] += 1
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

def removepreflopdoc():
    DBOperater.DeleteData(Constant.HANDSDB,Constant.CUMUCLT,{"_id":Constant.PREFLOPRANGEDOC})

def tongjiftmain():
    result = DBOperater.Find(Constant.HANDSDB,Constant.TJHANDSCLT,{})
    for handsinfo in result:
        tongjifirstturnstate(handsinfo)

if __name__ == "__main__":
    removepreflopdoc()
    tongjiftmain()