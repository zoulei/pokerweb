
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
import os

# print math.factorial(52) / math.factorial(2) / math.factorial(52 - 2)
# print math.factorial(52) / math.factorial(3) / math.factorial(52 - 3)
# print math.factorial(52) / math.factorial(4) / math.factorial(52 - 4)
# print math.factorial(52) / math.factorial(5) / math.factorial(52 - 5)
def f(v):
    return v * v

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
    # handsinfocommon.pp.pprint(strengthmap)

    allcards = rangeobj._generateallcard()
    allboards = itertools.combinations(allcards,boardlen)
    boardidx = 0

    # completestrengthmap = {}
    # reversecompletestrengthmap = {}

    if os.path.exists(Constant.COMPLETESTRENGTHMAPPREFIX + str(boardlen)):
        completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(boardlen))
        usecache = True
    else:
        completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(boardlen), 'c')
        usecache = False
    if os.path.exists(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX + str(boardlen)):
        # reversecompletestrengthmap = shelve.open(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX + str(boardlen))
        pass
    else:
        reversecompletestrengthmap = shelve.open(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX + str(boardlen), 'c')

    psbhandsquantity = handsinfocommon.combination(52-boardlen,2)

    for board in allboards:
        boardidx += 1
        if boardidx % 1000 == 0:
            print "boardidx:",boardidx

        if usecache:
            strengthorder = completestrengthmap[hunlgame.board2str(board)]
            # reversestrengthorder = reversecompletestrengthmap[hunlgame.board2str(board)]
        else:
            tmpallcards= copy.deepcopy(allcards)
            for card in board:
                tmpallcards.remove(card)
            allhands = itertools.combinations(tmpallcards,2)
            allhandslist = []
            possiblehandsnumer = len(allhandslist)
            for hands in allhands:
                allhandslist.append(list(hands))

            tmpallhandslist = copy.deepcopy(allhandslist)
            strengthorder = hunlgame.sorthands_(board, tmpallhandslist)

            reversestrengthorder = {}
            for key in strengthorder.keys():
                handsidxlist = strengthorder[key]
                handslist = [str(hunlgame.Hands(allhandslist[v])) for v in handsidxlist]
                strengthorder[key] = handslist
                for handsstr in handslist:
                    reversestrengthorder[handsstr] = key

            completestrengthmap[hunlgame.board2str(board)] = strengthorder
            reversecompletestrengthmap[hunlgame.board2str(board)] = reversestrengthorder

        ranklist = strengthorder.keys()
        ranklist.sort(reverse=True)
        for rank in ranklist:
            handsstrlist = strengthorder[rank]
            rank -= ( psbhandsquantity - Constant.SCORERANGE )
            if rank < 1:
                rank = 1
            if len(handsstrlist) > 100:
                break
            for handsstr in handsstrlist:
                strengthmap[handsstr] += f(rank)

            if rank == 1:
                break
        # handsinfocommon.pp.pprint(strengthmap)
        # print "======================= " + hunlgame.board2str(board)
        # raw_input()

        # pp.pprint(strengthmap)
        # raw_input()

    for key in strengthmap.keys():
        strengthmap[key] /= (boardidx * 1.0)
    completestrengthmap.close()
    if not usecache:
        reversecompletestrengthmap.close()
    return strengthmap

def calsingleturncardstrength():
    print "cal flop"
    flopstrengthmap = calavgstrength(3)
    flopstr = json.dumps(flopstrengthmap)
    print "cal turn"
    turnstrengthmap = calavgstrength(4)
    turnstr = json.dumps(turnstrengthmap)
    print "cal river"
    # riverstrengthmap = calavgstrength(5)
    riverstrengthmap = {}
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
    # return flopstrengthmap

    turnstr = file.readline()
    turnstr = turnstr.strip()
    turnstrengthmap = json.loads(turnstr)
    riverstr = file.readline()
    riverstr = riverstr.strip()
    riverstrengthmap = json.loads(riverstr)

    avgstremgthmap = {}
    flopstrengthmap = removesymmetry(flopstrengthmap)
    turnstrengthmap = removesymmetry(turnstrengthmap)

    import printtongjiinfo
    print "=========================================flop==============================="
    printstrengthrank(flopstrengthmap)
    print "=========================================turn==============================="
    printstrengthrank(turnstrengthmap)

    riverstrengthmap = removesymmetry(riverstrengthmap)

    for key in flopstrengthmap.keys():
        avgstremgthmap[key] = g(flopstrengthmap[key],turnstrengthmap[key],riverstrengthmap[key])


    print "=========================================river==============================="
    printstrengthrank(riverstrengthmap)
    print "=========================================avg==============================="
    printstrengthrank(avgstremgthmap)

    return avgstremgthmap

def removesymmetry(avgstrengthmap):
    newmap = {}
    for key,value in avgstrengthmap.items():
        cardsstr = key.split(" ")
        if cardsstr[0][-1] == cardsstr[1][-1]:
            newkey = cardsstr[0][:-1] + cardsstr[1][:-1] + "s"
        else:
            newkey = cardsstr[0][:-1] + cardsstr[1][:-1] + "o"

        # if key[1] == key[4]:
        #     newkey = key[0] + key[3] + "s"
        # else:
        #     newkey = key[0] + key[3] + "o"
        newmap[newkey] = value
    return newmap

def printstrengthrank(targmap):
    tarlist = targmap.items()
    tarlist.sort(key = lambda v:v[1],reverse = True)
    handsnum = 0
    for handsstr ,strength in tarlist:
        if len(handsstr) == 5:
            handsnum += 6
        elif len(handsstr) == 4:
            if handsstr[-1] == "s":
                handsnum += 4
            else:
                handsnum += 12
        else:
            if handsstr[0] == handsstr[1]:
                handsnum += 6
            elif handsstr[-1] == "s":
                handsnum += 4
            else:
                handsnum += 12
        print handsstr, " : ", strength, handsnum * 1.0 / 1326 * 100

def test():
    calsingleturncardstrength()
    avgstrengthmap = calprivatecardstrength()

def testprintboardstr():
    completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(3))
    idx = 0
    for key in completestrengthmap:
        print key
        idx += 1
        if idx % 100 == 0:
            raw_input()


def testshelveefficient():
    import time
    startload = time.time()
    completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(5))
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

def testshelveefficient1():
    import time
    startload = time.time()
    completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(5))
    endload = time.time() - startload

    startloopup = time.time()
    lookupquantity = 1000
    idx = 0
    for key in completestrengthmap:
        idx += 1
        if idx == lookupquantity:
            break
        handsinfocommon.pp.pprint(completestrengthmap[key])
    print "endload:",endload
    print "avgtime:", (time.time() - startloopup)/lookupquantity

    completestrengthmap.close()

def testshelveefficient2():
    rangeobj = hunlgame.HandsRange()

    rangeobj.addFullRange()
    allcards = rangeobj._generateallcard()
    allboards = itertools.combinations(allcards,5)


    import time
    startload = time.time()
    completestrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX + str(5))
    endload = time.time() - startload

    startloopup = time.time()
    lookupquantity = 1000
    idx = 0
    for board in allboards:
        idx += 1
        if idx == lookupquantity:
            break
        handsinfocommon.pp.pprint(completestrengthmap[hunlgame.board2str(board)])
    print "endload:",endload
    print "avgtime:", (time.time() - startloopup)/lookupquantity

    completestrengthmap.close()


if __name__ == "__main__":
    # test()
    # calsingleturncardstrength()
    # calprivatecardstrength
    # calavgstrength(3)
    # testshelveefficient2()
    # testshelveefficient1()
    # test()
    # calavgstrength(4)
    testprintboardstr()
