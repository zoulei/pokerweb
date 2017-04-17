import DBOperater
import datetime
import time
import Constant

def storeTestData():
    nowtime = datetime.datetime.now()
    onemonthlater = time.mktime(nowtime.timetuple())
    onemonthlater += 3600*24*30
    onemonthlater = datetime.datetime.fromtimestamp(onemonthlater)
    oneyearlater = time.mktime(nowtime.timetuple())
    oneyearlater += 3600*24*30*12
    oneyearlater = datetime.datetime.fromtimestamp(oneyearlater)

    rangeList = [[14,14,0],[13,13,0],[12,12,0],[11,11,0],[10,10,0],[9,9,0],[8,8,0],
                       [7,7,0],[6,6,0],[5,5,0],[4,4,0],[3,3,0],[2,2,0],
                        [14,13,0],[14,13,1],[14,12,0],[14,12,1],[14,11,0],[14,11,1],[14,10,0],[14,10,1]]
    foldstg = {}
    for i in xrange(1,10):
        foldstg[str(i)] = {}
        for j in xrange(1,i+1):
            foldstg[str(i)][str(j)] = rangeList

    data = {"username":"zl","pwd":"1234","due":oneyearlater,"foldstrategy":foldstg}
    DBOperater.Connect()
    DBOperater.StoreData(Constant.LOGINDB,Constant.LOGINCLT,data)
    data = {"username": "robot", "pwd": "robot1234", "due": onemonthlater, "foldstrategy": {}}
    DBOperater.StoreData(Constant.LOGINDB, Constant.LOGINCLT, data)
    data = {"username": "robot1", "pwd": "robot11234", "due": nowtime, "foldstrategy": foldstg}
    DBOperater.StoreData(Constant.LOGINDB, Constant.LOGINCLT, data)

if __name__ == "__main__":
    storeTestData()