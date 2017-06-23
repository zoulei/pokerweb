import hunlgame
import privatecardsstrength
import copy

def getboardvalue(board, fullstrengthmap, reversenextfullstrengthmap, playerhands = None):
    strengthmap = fullstrengthmap[hunlgame.board2str(board)]
    strkey = strengthmap.keys()
    maxkey = strkey[-1]
    if playerhands:
        strongesthands = [playerhands,]
    else:
        strongesthands = strengthmap[maxkey]

    rangeobj = hunlgame.HandsRange()
    allcards = rangeobj._generateallcard()

    for card in board:
        allcards.remove(card)

    totaldec = 0
    rawstrength = privatecardsstrength.f(maxkey)
    for card in allcards:
        tmpboard = copy.deepcopy(board)
        tmpboard.append(card)

        # here need strength map of rank to hands and hands to rank
        # of each board
        boardstr = hunlgame.board2str(tmpboard)
        reversenextstrengthmap = reversenextfullstrengthmap(boardstr)
        avgstrength = 0
        for handsstr in strongesthands:
            avgstrength += privatecardsstrength.f(reversenextstrengthmap[handsstr])
        avgstrength /= len(strongesthands) * 1.0

        totaldec += rawstrength - avgstrength

    avgdec = totaldec * 1.0 / len(allcards)
    return avgdec



def viewflopboardvalue():
    fullstrengthmap = privatecardsstrength.readcompletestrengthmap(3)
    reversefullstrengthmap = privatecardsstrength.readreversecompletestrengthmap(3)
    board = [hunlgame.Card(0,7),hunlgame.Card(0,8),hunlgame.Card(1,13)]
    print getboardvalue(board,fullstrengthmap,reversefullstrengthmap)