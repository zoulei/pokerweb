import hunlgame
import privatecardsstrength
import copy
import itertools
import shelve
import Constant
import earthmover
import handsinfocommon

# return a dict, avg change for each hands
def getboardvalue(board, fullstrengthmap, reversefullstrengthmap, reversenextfullstrengthmap):
    # strengthmap = fullstrengthmap[hunlgame.board2str(board)]
    # strkey = strengthmap.keys()
    # maxkey = strkey[-1]

    rangeobj = hunlgame.HandsRange()
    allcards = rangeobj._generateallcard()

    handsstrengthchangedict = {}
    allhands = itertools.combinations(allcards,2)
    for cardslist in allhands:
        handsstrengthchangedict[ str(hunlgame.Hands(cardslist))] = 0

    for card in board:
        allcards.remove(card)

    reversestrengthmap = reversefullstrengthmap[hunlgame.board2str(board)]

    for card in allcards:
        tmpboard = list(copy.deepcopy(board))
        tmpboard.append(card)
        tmpboard.sort()

        # here need strength map of rank to hands and hands to rank
        # of each board
        boardstr = hunlgame.board2str(tmpboard)
        reversenextstrengthmap = reversenextfullstrengthmap[boardstr]

        for key, rank in reversenextstrengthmap.items():
            if rank == 0:
                continue
            oldrank = reversestrengthmap[key]

            rankchange = rank - oldrank
            handsstrengthchangedict[key] += abs(rankchange)

    return handsstrengthchangedict

def savetohistongram(handsstrengthchangedict, sfname):
    file = open(sfname,"w")
    for key,value in handsstrengthchangedict.items():
        file.write(str(key) + "\t" + str(value) + "\n")
    file.close()

def calavgstrengthchange(boardlen):
    rangeobj = hunlgame.HandsRange()
    allcards = rangeobj._generateallcard()

    allboards = itertools.combinations(allcards,boardlen)
    boardvaluedict = shelve.open(Constant.BOARDVALUE+str(boardlen),'c')

    fullstrengthmap = shelve.open(Constant.COMPLETESTRENGTHMAPPREFIX+str(boardlen))
    reversefullstrengthmap = shelve.open(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX+str(boardlen))
    reversenextfullstrengthmap = shelve.open(Constant.REVERSECOMPLETESTRENGTHMAPPREFIX+str(boardlen+1))

    # targetlist = ["2C 7H AS","3C 7H AS","6C 7H AS","2H 7H AS","2C 7H KS"]
    targetlist = ["2C 7H AS","3C 7H AS","2H 7H AS"]
    allboards = [ hunlgame.generateCards(v.replace(" ","")) for v in targetlist ]

    idx = 0
    for board in allboards:
        idx += 1
        if idx % 1000 == 0:
            print idx
        boardvalue = getboardvalue(board,fullstrengthmap,reversefullstrengthmap,reversenextfullstrengthmap)
        boardvaluedict[hunlgame.board2str(board)] = boardvalue
        # handsinfocommon.pp.pprint(boardvalue)
        # raw_input()
    boardvaluedict.close()
    fullstrengthmap.close()
    reversefullstrengthmap.close()
    reversenextfullstrengthmap.close()

def viewflopboardvalue():
    fullstrengthmap = privatecardsstrength.readcompletestrengthmap(3)
    reversefullstrengthmap = privatecardsstrength.readreversecompletestrengthmap(3)
    board = [hunlgame.Card(0,7),hunlgame.Card(0,8),hunlgame.Card(1,13)]
    print getboardvalue(board,fullstrengthmap,reversefullstrengthmap)

def test():
    calavgstrengthchange(3)

def testprinthistomgranfile():
    boardvaluedict = shelve.open(Constant.BOARDVALUE+str(3))
    targetlist = ["2C 7H AS","3C 7H AS","2H 7H AS"]
    for idx in xrange(len(targetlist)):
        for cdx in xrange(idx+1, len(targetlist)):
            key1 = targetlist[idx]
            key2 = targetlist[cdx]
            print  key1, key2,earthmover.simplediff(boardvaluedict[targetlist[idx]],boardvaluedict[targetlist[cdx]] )
            earthmover.compare(boardvaluedict[targetlist[idx]],boardvaluedict[targetlist[cdx]])
            # raw_input()

if __name__ == "__main__":
    test()
    testprinthistomgranfile()