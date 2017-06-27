
import sys

import math
import hunlgame
import itertools
import copy
import json
import pprint
import Constant
import handsinfocommon
import pickle

from contextlib import closing
import shelve


# print math.factorial(52) / math.factorial(2) / math.factorial(52 - 2)
# print math.factorial(52) / math.factorial(3) / math.factorial(52 - 3)
# print math.factorial(52) / math.factorial(4) / math.factorial(52 - 4)
# print math.factorial(52) / math.factorial(5) / math.factorial(52 - 5)
def f(v):
    return v*v

def g(v1,v2,v3):
    return v1 + v2 + v3

def readcompletestrengthmap(boardlen):
    file = open(Constant.COMPLETESTRENGTHMAPPREFIX+str(boardlen))
    return json.loads(file.readline())

def readreversecompletestrengthmap(boardlen):
    file = open(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX+str(boardlen))
    return json.loads(file.readline())

# completestrengthmap records the hands strength of each hands
# on each board. The first level key is string of board, the
# Second level key is the rank of specific hands, and the value
# is array of string of hands.

# reversecompletestrengthmap records the same information as completestrengthmap,
# with the difference that the data is organised in different structure.
# The first level key is string of board, the second level key is
# string of hands, and the value is the rank of specific hands.
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

    # completestrengthmap = {}
    # reversecompletestrengthmap = {}

    completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(boardlen), 'c')
    reversecompletestrengthmap = shelve.open(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX + str(boardlen), 'c')


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
        tmpallhandslist = copy.deepcopy(allhandslist)
        strengthorder = hunlgame.sorthands_(board, tmpallhandslist)

        for rank, handsidxlist in strengthorder.items():
            for handsidx in handsidxlist:
                handsstr = str(hunlgame.Hands(allhandslist[handsidx]))
                strengthmap[handsstr] += f(rank)

        reversestrengthorder = {}
        for key in strengthorder.keys():
            handsidxlist = strengthorder[key]
            handslist = [str(hunlgame.Hands(allhandslist[v])) for v in handsidxlist]
            strengthorder[key] = handslist
            for handsstr in handslist:
                reversestrengthorder[handsstr] = key

        completestrengthmap[hunlgame.board2str(board)] = strengthorder
        reversecompletestrengthmap[hunlgame.board2str(board)] = reversestrengthorder
        # pp.pprint(strengthmap)
        # raw_input()

    for key in strengthmap.keys():
        strengthmap[key] /= (boardidx * 1.0)
    completestrengthmap.close()
    reversecompletestrengthmap.close()
    # completemapstr = pickle.dumps(completestrengthmap)
    # reversecompletemapstr = pickle.dumps(reversecompletestrengthmap)
    # file = open(Constant.COMPLETESTRENGTHMAPPREFIX + str(boardlen),"w")
    # file.write(completemapstr)
    # pickle.loads(completemapstr)
    # file.close()
    # file = open(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX + str(boardlen),"w")
    # file.write(reversecompletemapstr)
    # file.close()
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

    # turnstr = "{}"
    # riverstr = "{}"

    file = open(Constant.PRIVATECARDSSTRENGTH,"w")
    file.write(flopstr+"\n")
    file.write(turnstr+"\n")
    file.write(riverstr+"\n")
    file.close()

def calprivatecardstrength():
    file = open(Constant.PRIVATECARDSSTRENGTH)
    flopstr = file.readline()
    flopstr = flopstr.strip()
    flopstrengthmap = json.loads(flopstr)
    strenglist = flopstrengthmap.items()
    strenglist.sort(key = lambda v:v[1],reverse = True)
    # for key, value in strenglist:
    #     print key," : ",value
    return flopstrengthmap

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
    calsingleturncardstrength()
    avgstrengthmap = calprivatecardstrength()
    avgstrengthmap = removesymmetry(avgstrengthmap)
    strengthlist = avgstrengthmap.items()
    strengthlist.sort(key = lambda v:v[1],reverse=True)
    for handsstr ,strength in strengthlist:
        print handsstr, " : ", strength

def testcalcompletestrengthmap():
    import time
    startload = time.time()
    completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(4))
    endload = time.time() - startload
    keylist = completestrengthmap.keys()
    loadkeylist = time.time() - startload
    import random
    keylistlength = len(keylist)

    startloopup = time.time()
    lookupquantity = 100
    for idx in xrange(lookupquantity):
        keyidx = random.randint(0,keylistlength - 1)
        key = keylist[keyidx]
        time.sleep(1)
        handsinfocommon.pp.pprint(completestrengthmap[key])
    print "endload:",endload
    print "loadkeylist:",loadkeylist
    print "avgtime:", (time.time() - startloopup)/lookupquantity

    completestrengthmap.close()

if __name__ == "__main__":
    # test()
    # calsingleturncardstrength()
    # calprivatecardstrength
    # calavgstrength(3)
    testcalcompletestrengthmap()
    # test()
    # calavgstrength(3)

