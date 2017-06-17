import sys
sys.path.append("C:/Users/zoulei/PycharmProjects/")

import math
import hunlgame
import itertools
import copy
import json

# print math.factorial(52) / math.factorial(2) / math.factorial(52 - 2)
# print math.factorial(52) / math.factorial(3) / math.factorial(52 - 3)
# print math.factorial(52) / math.factorial(4) / math.factorial(52 - 4)
# print math.factorial(52) / math.factorial(5) / math.factorial(52 - 5)
def f(v):
    return v*v

def g(v1,v2,v3):
    return v1 + v2 + v3

def calavgstrength( boardlen):
    rangeobj = hunlgame.HandsRange()

    rangeobj.addFullRange()
    fullhandslist = rangeobj.get()
    handsstrlist = [str(v) for v in fullhandslist]

    strengthmap = {}
    for handsstr in handsstrlist:
        strengthmap[handsstr] = 0

    allcards = rangeobj._generateallcard()
    allboards = itertools.combinations(allcards,boardlen)
    boardidx = 0
    for board in allboards:
        boardidx += 1
        if boardidx % 1000 == 0:
            print "boardidx:",boardidx
        tmpallcards= copy.deepcopy(allcards)
        for card in board:
            tmpallcards.remove(card)
        allhands = itertools.combinations(tmpallcards,2)
        allhandslist = []
        for hands in allhands:
            allhandslist.append(list(hands))

        strengthorder = hunlgame.sorthands_(board, allhandslist)

        for rank, handsidxlist in strengthorder.items():
            for handsidx in handsidxlist:
                handsstr = str(hunlgame.Hands(allhandslist[handsidx]))
                strengthmap[handsstr] += f(rank)

    for key in strengthmap.keys():
        strengthmap[key] /= (boardidx * 1.0)

    return strengthmap

def calsingleturncardstrength():
    print "cal flop"
    flopstrengthmap = calavgstrength(3)
    flopstr = json.dumps(flopstrengthmap)
    print "cal turn"
    turnstrengthmap = calavgstrength(4)
    turnstr = json.dumps(turnstrengthmap)
    print "cal river"
    riverstrengthmap = calavgstrength(5)
    riverstr = json.dumps(riverstrengthmap)

    file = open("privatecardstrengthdata","w")
    file.write(flopstr+"\n")
    file.write(turnstr+"\n")
    file.write(riverstr+"\n")
    file.close()

def calprivatecardstrength():
    file = open("privatecardstrengthdata")
    flopstr = file.readline()
    flopstr = flopstr.strip()
    flopstrengthmap = json.loads(flopstr)
    turnstr = file.readline()
    turnstr = turnstr.strip()
    turnstrengthmap = json.loads(turnstr)
    riverstr = file.readline()
    riverstr = riverstr.strip()
    riverstrengthmap = json.loads(riverstr)

    avgstremgthmap = {}
    for key in flopstrengthmap.keys():
        avgstremgthmap[key] = g(flopstrengthmap[key],turnstrengthmap[key],riverstrengthmap[key])

    return avgstremgthmap

def removesymmetry(avgstrengthmap):
    newmap = {}
    for key,value in avgstrengthmap.items():
        if key[1] == key[4]:
            newkey = key[0] + key[3] + "s"
        else:
            newkey = key[0] + key[3] + "o"
        newmap[newkey] = value
    return newmap

def test():
    avgstrengthmap = calprivatecardstrength()
    avgstrengthmap = removesymmetry(avgstrengthmap)
    strengthlist = avgstrengthmap.items()
    strengthlist.sort(key = lambda v:v[1],reverse=True)
    for handsstr ,strength in strengthlist:
        print handsstr, " : ", strength

if __name__ == "__main__":
    calsingleturncardstrength()
    # test()


