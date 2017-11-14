from math import pow
from privatecardsstrength import PrivateHandRank
from hunlgame import HandsRange

class HandsDisQuality:
    def __init__(self,dis = None):
        if dis is None:
            self.m_handsdis = {}
        else:
            self.m_handsdis = dis

    def __add__(self, other):
        for key in self.m_handsdis.keys():
            self.m_handsdis[key] += other.m_handsdis.get(key,0)
        for key in other.m_handsdis.keys():
            if key in self.m_handsdis:
                continue
            self.m_handsdis[key] = other.m_handsdis[key]
        return self

    # make the sum of probability be 1
    def normalize(self):
        total = sum(self.m_handsdis.values())
        for key in self.m_handsdis.keys():
            self.m_handsdis[key] /= total

    def calquality(self):
        quantity = 0
        handrankengine = PrivateHandRank()
        for hand, value in self.m_handsdis.items():
            quantity += self.f(handrankengine.getrank(hand),value )
        return quantity

    def calequalquality(self):
        handrankengine = PrivateHandRank()
        handrangeobj = HandsRange()
        handrangeobj.addFullRange()
        quantity = 0
        prob = 1.0/ 1326
        for hand in handrangeobj.get():
            quantity += self.f(handrankengine.getrank(hand),prob )
        return quantity

    def f(self, rank, value):
        return pow(rank, 2) * value

    # def getquality(self):
    #     pass