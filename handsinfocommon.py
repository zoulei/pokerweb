import pprint
import math
import hunlgame
# change the raw data format collected to hunlgame format
def getboard(handsdata):
    infolen = len(handsdata)
    if infolen < 6:
        # over before river
        return handsdata[-1]
    elif infolen == 7:
        # play to river or all in at turn
        return handsdata[-1]

    else:
        # infolen == 6
        # may be play to river and not show card
        # may be all in before river
        if not isinstance(handsdata[5][0][0],list):
            # play to river and not show card
            return handsdata[-1]

        for idx in xrange(4,0,-1):
            # all in before river
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

# ================== action statistics dict related ===========================
def completedict(rawdoc, * keys):
    for key in keys[:-1]:
        if key not in rawdoc:
            rawdoc[key] = {}
        rawdoc = rawdoc[key]
    if keys[-1] not in rawdoc:
        rawdoc[keys[-1]] = {"call":0,"raise":0,"fold":0,"sum":0}