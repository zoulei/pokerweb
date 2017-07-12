import pprint
import math
import hunlgame
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

def readinpool(handsinfo):
    return handsinfo["data"][0][2]

def readbb(handsinfo):
    return handsinfo["data"][0][0]

def readanti(handsinfo):
    return handsinfo["data"][0][1] / len(readinpool(handsinfo))

def roundhalf(value):
    return int(round(value * 2)) * 0.5

def combination(n,r):
    return math.factorial(n) / math.factorial(n - r) / math.factorial(r)

def permutation(n,r):
    return math.factorial(n) / math.factorial(n - r)

def getnearestkey(querykey,keylist):
    keylist = [int(v) for v in keylist]
    querykey = int(querykey)
    difflist = [abs(v - querykey) for v in keylist]
    targetkey = keylist[difflist.index(min(difflist))]
    return targetkey

# ==================debug related===========================
pp = pprint.PrettyPrinter(indent= 4)
