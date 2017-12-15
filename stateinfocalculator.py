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
    def playerquantitiytoact(self):
        toactplayers = 0
        for pos in range(self.m_nextplayer - 1,0,-1) + range(10, self.m_raiser, -1):
            if self.m_inpoolstate[pos] != 1:
                continue
            else:
                toactplayers += 1
        return toactplayers

    # player quantitiy that has made action
    def playerquantityacted(self):
        if self.m_circle