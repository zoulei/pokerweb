import Constant
from afterflopwinrate import FnameManager
import pickle

class NearestQueryResult:
    def __init__(self, winrateobjlist, ):
        self.m_winrateobjlist = winrateobjlist

        self.tongjiattack()

    def tongjiattack(self):
        attacklist = [v.getattack() for v in self.m_winrateobjlist]
        attackset = set(attacklist)

        self.m_attackdict = {}
        for ele in attackset:
            self.m_attackdict.update({ele:attacklist.count(ele)})

        self.m_attackratedict = {}
        docsum = sum(self.m_attackdict.values()) * 1.0
        for key in self.m_attackdict.keys():
            self.m_attackratedict[key] = self.m_attackdict[key] / docsum

class HandQueryResult:
    def __init__(self, queryresultobjlist, handlist, handratelist = None):
        self.m_queryresult = queryresultobjlist
        self.m_handlist = handlist

        if handratelist is None:
            self.m_handratelist = [1.0/ len(handlist)] * len(handlist)
        else:
            self.m_handratelist = handratelist

    def getrange(self, attack):
        pass

class NearestQueryEngine:
    def __init__(self):
        self.m_fnameobj = FnameManager()
        self.m_database = {}

    def loaddata(self, statekey):
        if statekey in self.m_database:
            return
        fname = Constant.CACHEDIR + self.m_fnameobj.generatehandhisfname(statekey)
        self.m_database[statekey] = pickle.load(open(fname,"rb"))

    def query(self, queryobj,statekey):
        self.loaddata(statekey)

        resulthisobj = []
        for winratehisobj in self.m_database[statekey]:
            if queryobj.like(winratehisobj):
                resulthisobj.append(winratehisobj)
        return resulthisobj