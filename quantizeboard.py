import hunlgame
import privatecardsstrength
import copy
import itertools
import shelve
import Constant

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


    for card in allcards:
        tmpboard = copy.deepcopy(board)
        tmpboard.append(card)
        tmpboard.sort()

        # here need strength map of rank to hands and hands to rank
        # of each board
        boardstr = hunlgame.board2str(tmpboard)
        reversenextstrengthmap = reversenextfullstrengthmap[boardstr]
        reversestrengthmap = reversefullstrengthmap[boardstr]

        for key, rank in reversenextstrengthmap.items():
            if rank == 0:
                continue
            oldrank = reversestrengthmap[key]

            rankchange = rank - oldrank
            handsstrengthchangedict[key] += rankchange

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
    for board in allboards:
        boardvalue = getboardvalue(board)
        boardvaluedict[hunlgame.board2str(board)] = boardvalue

def viewflopboardvalue():
    fullstrengthmap = privatecardsstrength.readcompletestrengthmap(3)
    reversefullstrengthmap = privatecardsstrength.readreversecompletestrengthmap(3)
    board = [hunlgame.Card(0,7),hunlgame.Card(0,8),hunlgame.Card(1,13)]
    print getboardvalue(board,fullstrengthmap,reversefullstrengthmap)

def test():
    calavgstrengthchange(3)

def testprinthistomgranfile():
    boardvaluedict = shelve.open(Constant.BOARDVALUE+str(3))
    targetlist = ["2C7HAS","3C7HAS","6C7HAS","2H7HAS","2C7HKS"]

if __name__ == "__main__":
    test()