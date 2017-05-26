# change the raw data format collected to hunlgame format
def getboard(handsdata):
    infolen = len(handsdata)
    if infolen < 6:
        return handsdata[-1]
    if infolen == 7:
        return handsdata[-1]
    for idx in xrange(4,0,-1):
        if handsdata[idx]!= None:
            return handsdata[idx]