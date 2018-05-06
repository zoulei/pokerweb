# -*- coding:utf-8 -*-
import json
import Constant
from hunlgame import generateCards,board2str,generateHands
import shelve

def cards2key(cards):
    return "".join(sorted([str(v) for v in cards]))

engine = None

class HandsRankDict:
    def __init__(self):
        # self.m_handsrank = shelve.open(Constant.ALLHANDSRANK)

        # 19 GB
        self.m_handsrank = json.load(open(Constant.ALLHANDSRANKINMEMORYJSON))

    # 最小的牌的排名为1,0意味着没有找到
    def __getitem__(self,key):
        return self.m_handsrank.get(key,0)

def getengine():
    global engine
    if engine is None:
        engine = HandsRankDict()
    return engine

class HandsRankEngine:
    def __init__(self, myhand, ophands, board):
        self.m_myhand = myhand
        self.m_ophands = ophands
        self.m_board = board
        self.sort()

    def sort(self):
        allhandslist = [self.m_myhand,] + self.m_ophands
        allhands = [v.get() for v in allhandslist]
        self.m_len = len(allhands)
        allfullcards = [v+self.m_board for v in allhands]
        allfullkey = [cards2key(v) for v in allfullcards]
        rankengine =  getengine()
        allrank = [rankengine[v] for v in allfullkey]
        handsrankdata = zip(allhandslist,allrank)
        handsrankdata.sort(key=lambda v:v[1])
        self.m_handsrankdata = handsrankdata
        self.m_rankedhands = [v[0] for v in self.m_handsrankdata]
        self.m_rank = self.m_rankedhands.index(self.m_myhand)
        self.m_rankvalue = allrank[0]
        self.m_invalid = 0
        for idx in xrange(len(handsrankdata)):
            if handsrankdata[idx][1] != 0:
                self.m_invalid = idx
                break
        self.m_tie = 0
        for idx in xrange(self.m_rank - 1,-1,-1):
            if handsrankdata[idx][1] == self.m_rankvalue:
                self.m_tie += 1
            else:
                break
        self.m_win = self.m_rank - self.m_tie - self.m_invalid
        for idx in xrange(self.m_rank + 1,self.m_len):
            if handsrankdata[idx][1] == self.m_rankvalue:
                self.m_tie += 1
            else:
                break
        self.m_lose = self.m_len - self.m_win - self.m_tie - 1 - self.m_invalid

    def getinvalid(self):
        return self.m_invalid

    def getwin(self):
        return self.m_win

    def gettie(self):
        return self.m_tie

    def getlose(self):
        return self.m_lose

    def getinvalidhands(self):
        return self.m_rankedhands[:self.m_invalid]

    def getwinhands(self):
        return self.m_rankedhands[self.m_invalid:self.m_win+self.m_invalid]

    def gettiehands(self):
        return self.m_rankedhands[self.m_win+self.m_invalid:self.m_rank] + self.m_rankedhands[self.m_rank + 1:self.m_win+self.m_tie+1+self.m_invalid]

    def getlosehands(self):
        return self.m_rankedhands[self.m_win + self.m_tie + 1 + self.m_invalid:]

    def printresult(self):
        print "myhand:",str(self.m_myhand)
        print "board:",board2str(self.m_board)
        print "invalid:",self.m_invalid
        print "win:",self.m_win
        print "tie:",self.m_tie
        print "lose:",self.m_lose
        print "my rank:",self.m_rank
        print "invalid:",[str(v) for v in self.getinvalidhands()]
        print "winhand:",[str(v) for v in self.getwinhands()]
        print "tiehand:",[str(v) for v in self.gettiehands()]
        print "losehand:",[str(v) for v in self.getlosehands()]

def testhandsrankengine():
    HandsRankEngine(generateHands("AHTH"),[generateHands(v) for v in ["TC9C","5S7S","ACTC","KSAC","8CAH"]],generateCards("KSQSJS5H8C")).printresult()
    HandsRankEngine(generateHands("5S7S"),[generateHands(v) for v in ["TC9C","AHTH","ASTS","ACTC"]],generateCards("KSQSJS5H8C")).printresult()
    print getengine()[cards2key(generateCards("ASKSQSJSTS"))]
    print getengine()[cards2key(generateCards("ASKSQSJSTS6S8T"))]
    print getengine()[cards2key(generateCards("7S5S4S3S2H"))]

def testhands():
    a = [generateHands(v) for v in ["9DAH","9HAD","9HAS","9SAD"]]
    print a.index(generateHands("9SAD"))
    print generateHands("9SAD") == a[0]
    print [str(v) for v in a]

if __name__ == "__main__":
    # testhandsrankengine()
    testhands()