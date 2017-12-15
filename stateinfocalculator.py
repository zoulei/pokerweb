from handsengine import ReplayEngine

class StateCalculator(ReplayEngine):
    #True is, False not
    def isopener(self,pos):
        if self.getpreflopinfomation()["raiser"] == pos:
            return True
        return False

    # True has, False not
    def hasopener(self):
        if self.getpreflopinfomation()["raiser"] != 0:
            return True
        return False

    # 0 means the best position, 1 means the worst position
    def relativepos(self,pos):
        total = self.m_remainplayer - self.m_allinplayer
        step = 1.0 / (total - 1)
        initial = - step
        for inpoolpos,state in enumerate(self.m_inpoolstate):
            if state == 1:
                initial += step
            if inpoolpos == pos:
                return 1 - initial

    # player quantity that still need to act
    def playerquantitytoact(self):
        total = 0
        poslist = self.getposlist()
        playeridx = poslist.index(self.m_nextplayer)
        if self.m_raiser == 0:
            for pos in poslist[playeridx + 1:]:
                if self.m_inpoolstate[pos] == 1:
                    total += 1
            return total
        for pos in poslist[playeridx + 1:] + poslist[:playeridx]:
            if pos == self.m_raiser:
                return total
            elif pos == self.m_fakeraiser:
                return 0
            if self.m_inpoolstate[pos] == 1:
                total += 1
        return total
        # 1 2 3 4(r) 5 6 7(f) 8 9

    # player quantitiy that has made action
    def playerquantityacted(self):
        if self.m_circle > 1:
            return self.m_remainplayer - self.m_allinplayer - 1
        poslist= self.getposlist()
        playeridx = poslist.index(self.m_nextplayer)
        total = 0
        for pos in poslist[:playeridx]:
            if self.m_inpoolstate[pos] == 1:
                total += 1
        return total

