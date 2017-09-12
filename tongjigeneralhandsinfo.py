from TraverseHands import TraverseHands
import Constant

class Tongjiallhands(TraverseHands):
    def filter(self, handsinfo):
        pass

    def mainfunc(self, handsinfo):
        pass

class Tongjivalidhands(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard >= 0 or showcard == -3):
            return True

    def mainfunc(self, handsinfo):
        pass

class Tongjifullinfomationhands(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard >= 0):
            return True

    def mainfunc(self, handsinfo):
        pass

class Tongjisolopot(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard >= 0 or showcard == -3):
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        # if handsinfo[Constant.STATEKEY][0][0] != "2;;2,1,2":
        #     return True
        return False

    def mainfunc(self, handsinfo):
        pass

class Tongjishowcardsolopot(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard == 1 or showcard == -3):
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        # if handsinfo[Constant.STATEKEY][0][0] != "2;;2,1,2":
        #     return True
        return False

    def mainfunc(self, handsinfo):
        pass

class Tongjirealshowcardsolopot(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard == 1):
            return True
        preflopgeneralinfo = handsinfo["preflopgeneralstate"]
        if preflopgeneralinfo["allin"] > 0:
            return True
        if preflopgeneralinfo["remain"] != 2:
            return True
        # if handsinfo[Constant.STATEKEY][0][0] != "2;;2,1,2":
        #     return True
        return False

    def mainfunc(self, handsinfo):
        pass

class Tongjishowcardpot(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not (showcard == 1 or showcard == -3):
            return True
        return False

    def mainfunc(self, handsinfo):
        pass

class Tongjirealshowcardpot(TraverseHands):
    def filter(self, handsinfo):
        showcard = handsinfo["showcard"]
        if not showcard == 1:
            return True
        return False

    def mainfunc(self, handsinfo):
        pass

if __name__ == "__main__":
    Tongjiallhands(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all hands"
    Tongjivalidhands(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all valid hands"
    Tongjifullinfomationhands(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all full information hands"
    Tongjisolopot(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all solo hands"
    Tongjishowcardsolopot(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all solo show card hands"
    Tongjirealshowcardsolopot(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all real solo show card hands"
    Tongjishowcardpot(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all show card hands"
    Tongjirealshowcardpot(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()
    print "all real show card hands"