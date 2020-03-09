import handsengine
import TraverseHands
import DBOperater
from Constant import *

def mainfunc(handsinfo):
    try:
        if handsengine.HandsInfo(handsinfo).getaction(1,0)[1] == "straddle":
            DBOperater.DeleteData(HANDSDB,HANDSCLT,{"_id":handsinfo["_id"]})
    except:
        pass

if __name__ == "__main__":
    TraverseHands.TraverseHands(HANDSDB,HANDSCLT,func=mainfunc).traverse()