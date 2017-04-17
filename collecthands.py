
from flask import request

import DBOperater

import Constant
import datetime
import json
import os
from werkzeug import secure_filename

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Constant.ALLOWED_EXTENSIONS

def uploadNameImg(request):
    # Get the name of the uploaded file
    filelist = request.files.getlist("file[]")
    # Check if the file is one of the allowed types/extensions
    for file in filelist:
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            file.save(os.path.join(Constant.UPLOAD_FOLDER, filename))
        else:
            return "0"
    return "1"

def uploadHandsInfo(request):
    contents = request.get_json(silent=True)
    if not contents:
        return "0"
    for content in contents:
        DBOperater.StoreData(Constant.HANDSDB,Constant.RAWHANDSCLT,content)
    return "1"

def gameseq(deviceID):
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{})
    result = list(result)

    if not len(result):
        return json.dumps([])

    seqlist = []
    seqdata = result[0]["data"]

    if deviceID in seqdata.keys():
        del seqdata[deviceID]

    for device in seqdata:
        seqlist.append(seqdata[device])

    DBOperater.DeleteData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone"})
    DBOperater.StoreData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone","data":seqdata})
    return json.dumps(seqlist)

def joingame(deviceID,seq):
    seq = int(seq)
    result = DBOperater.Find(Constant.HANDSDB,Constant.GAMESEQCLT,{})
    result = list(result)

    if not len(result):
        DBOperater.StoreData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone","data":{deviceID:seq}})
        return "1"

    seqdata = result[0]["data"]
    if deviceID in seqdata.keys():
        del seqdata[deviceID]

    for v in seqdata.values():
        if v == seq:
            return "0"

    seqdata[deviceID] = seq
    DBOperater.DeleteData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone"})
    DBOperater.StoreData(Constant.HANDSDB,Constant.GAMESEQCLT,{"_id":"onlyone","data":seqdata})
    return "1"
