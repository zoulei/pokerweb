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

    # raiser's stack pot ratio
    def getraiserstackpotratio(self):
        myneedtobet = self.m_betvalue - self.m_bethistory[self.m_nextplayer]
        raisermaxstack = 0
        realpot = self.m_pot + myneedtobet
        if self.m_raiser != 0:
            poslist = range(self.m_raiser,0,-1) + range(9, self.m_raiser,-1)
        else:
            poslist = self.getposlist()
        for pos in poslist:
            if pos == self.m_nextplayer:
                break
            if self.m_inpoolstate[pos] == 0:
                continue
            if self.m_stacksize[pos] > raisermaxstack:
                raisermaxstack = self.m_stacksize[pos]
        if self.m_stacksize[self.m_nextplayer] - myneedtobet < raisermaxstack:
            raisermaxstack = self.m_stacksize[self.m_nextplayer] - myneedtobet
        if raisermaxstack < 0:
            raisermaxstack = 0
        return raisermaxstack * 1.0 / realpot

    # players need to bet stack pot ratio
    def getneedtobetstackratio(self):
        myneedtobet = self.m_betvalue - self.m_bethistory[self.m_nextplayer]
        realpot = self.m_pot + myneedtobet
        targetmaxstack = []
        if self.m_raiser != 0:
            poslist = range(self.m_nextplayer -1,0,-1) + range(9, self.m_nextplayer - 1,-1)
            posidx = poslist.index(self.m_raiser)
        else:
            poslist = self.getposlist()[::-1]
            posidx = poslist.index(self.m_nextplayer)
        for pos in poslist[:posidx]:
            if self.m_inpoolstate[pos] != 1:
                continue
            targetneedtobet = self.m_betvalue - self.m_bethistory[pos]
            targetrealpot = realpot + targetneedtobet
            targetstacksize = min(self.m_stacksize[pos]-targetneedtobet,self.m_stacksize[self.m_nextplayer]-myneedtobet)
            if targetstacksize < 0:
                targetstacksize = 0
            targetmaxstack.append(targetstacksize * 1.0 / targetrealpot)
        targetmaxstack.sort()
        return targetmaxstack