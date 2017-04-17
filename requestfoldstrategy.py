
from flask import request

import DBOperater

import Constant
import datetime
import json

# return
# 0 means username or pwd is not correct
# 1 means that the membership is overdue
# 2 means that foldStrategy is not set
# otherwise return foldstrategy
def requestfoldstrategy(request):
    username = request.form["username"]
    pwd = request.form["pwd"]

    result = DBOperater.Find(Constant.LOGINDB,Constant.LOGINCLT,{"username":username,"pwd":pwd})
    result = list(result)

    if not len(result):
        # didn't get any result, means that username or pwd is not correct
        return 0
    if len(result) > 1:
        # result cann't be more than 1
        pass
    resultMap = result[0]
    duetime = resultMap["due"]

    nowtime = datetime.datetime.now()

    if duetime < nowtime:
        # duetime is before nowtime, means that the membership is overdue
        return 1

    foldStrategy = resultMap["foldstrategy"]
    if not foldStrategy:
        # foldStrategy is not set
        return 2
    foldstgstr = json.dumps(foldStrategy)
    return foldstgstr