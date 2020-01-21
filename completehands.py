import DBOperater
import Constant
import os.path
import os
import time
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
import cv2
import numpy as np
import shutil
import traceback

DBOperater.Connect()

def modifyimg(sf,of):
    img = cv2.imread(sf)

    h,w,_ = img.shape


    for i in xrange(h):
            for j in xrange(w):
                    color = img[i,j]
#                       if 0 <= color[2] <= 30 and 40 <= color[1] <= 90 and 50 <= color[0] <= 160:
                    if color[2] <= 50 or color[1] <= 50 or color[0] <= 50:
                            img[i,j] = [255,255,255]
                    else:
                            img[i,j] = [0,0,0]
    #cv2.rectangle(img,(0,0),(w,4),(255,255,255),-1)
    #cv2.rectangle(img,(0,31),(w,h-1),(255,255,255),-1)
    cv2.imwrite(of,img)

def completehands():
    result = DBOperater.Find(Constant.HANDSDB,Constant.RAWHANDSCLT,{})

    for rawhand in result:
        try:
            curid = rawhand["_id"]
            tbsize = rawhand["tbsize"]

            allname = []

            # identify name
            for j in xrange(1,tbsize+1):
                namelist = []
                for i in xrange(3):
                    imgfname = Constant.UPLOAD_FOLDER +  Constant.NAMEIMGPREFIX + "_" + curid + "_" + str(j) + "_" + str(i) + ".png"
                    tmpfname = Constant.UPLOAD_FOLDER +  Constant.NAMEIMGPREFIX + "_" + "tmp" + "_" + curid + "_" + str(j) + "_" + str(i) + ".png"
                    if not os.path.isfile(imgfname):
                        continue
                    modifyimg(imgfname,tmpfname)
                    ocrresult = pytesseract.image_to_string(Image.open(tmpfname),lang = 'chi_sim')
                    if (not ("\n" in ocrresult) ) and ocrresult != "":
                        namelist.append( ocrresult)
                    if "\n" in ocrresult or ocrresult == "":
                        shutil.copyfile(imgfname,Constant.OCR_ERROR_FOLDER +  Constant.NAMEIMGPREFIX + "_" + curid + "_" + str(j) + "_" + str(i) + ".png")
                realname = "?"
                for i in xrange(len(namelist)):
                    cnt = 0
                    for j in xrange(len(namelist)):
                        if namelist[i] == namelist[j]:
                            cnt += 1
                    if cnt >= 2:
                        realname = namelist[i]
                        break
                if (realname == "?" and len(namelist) != 0):
                    realname = namelist[0]
                print "="*100
                print namelist
                print realname

                allname.append(realname)

            # store history hands data
            DBOperater.StoreData(Constant.HANDSDB,Constant.HISHANDSCLT,rawhand)

            # update hands data
            rawhand["playername"] = allname

            # store complete hands data
            DBOperater.StoreData(Constant.HANDSDB,Constant.HANDSCLT,rawhand)

            # remove raw hands data
            delresult = DBOperater.DeleteData(Constant.HANDSDB,Constant.RAWHANDSCLT,{"_id":curid})
            if delresult.deleted_count == 0:
                print "error: the _id is ",curid
                break

            # delete img file
            for j in xrange(1,tbsize+1):
                namelist = []
                for i in xrange(3):
                    imgfname = Constant.UPLOAD_FOLDER + Constant.NAMEIMGPREFIX + "_" + curid + "_" + str(j) + "_" + str(i) + ".png"
                    tmpfname = Constant.UPLOAD_FOLDER +  Constant.NAMEIMGPREFIX + "_" + "tmp" + "_" + curid + "_" + str(j) + "_" + str(i) + ".png"
                    if not os.path.isfile(imgfname):
                        continue
                    os.remove(imgfname)
                    if not os.path.isfile(tmpfname):
                        continue
                    os.remove(tmpfname)
            print curid
            print "\n"*4
        except KeyboardInterrupt:
            raise
        except:
            print "excepttion occur:",curid
            traceback.print_exc()
        # 1022

def maincompleteh1023
    while True:
        try:
            completehands()
            time.sleep( 10)
        except KeyboardInterrupt:
            raise
        except:
            print "excepttion occur:"
            traceback.print_exc()

if __name__ == "__main__":
    maincompletehands()