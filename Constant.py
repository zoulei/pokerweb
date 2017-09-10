MONGOHOST = '192.168.112.111'
#MONGOHOST = 'localhost'
MONGOPORT = 27017
DBUSERNAME = 'root'
DBPWD = "123459"
AUTHDBNAME = "admin"

LOGINDB = "pmdb"
LOGINCLT = "loginclt"

HANDSDB = "handsdb"
HANDSCLT = "handsclt"

RAWHANDSCLT = "rawhandsclt"
HISHANDSCLT = "hishandsclt"
TJHISHANDSCLT = "tjhishandsclt"
TJHANDSCLT = "tjhandsclt"

GAMESEQCLT = "gameseqclt"

CUMUCLT = "cumuclt"

# =====================preflop state related=============================
PREFLOPRANGEDOC = "prefloprange"
PREFLOPJOINRATEDOC  = "preflopjoinratedoc"
PREFLOPREPAIRJOINRATEDOC = "prefloprepairjoinratedoc"

FTDATA = "ftdata"
# FT3BETDATA = "ft3betdata"
# FT4BETDATA = "ft4betdata"
# FT5BETDATA = "ft5betdata"

STDATA = "stdata"
# ST3BETDATA = "st3betdata"
# ST4BETDATA = "st4betdata"
# ST5BETDATA = "st5betdata"

A3BETDATA = "3betdata"
A4BETDATA = "4betdata"
A5BETDATA = "5betdata"

FTJOINRATEDATA = "ftjoinratedata"
FT3BETJOINRATEDATA = "ft3betjoinratedata"
FT4BETJOINRATEDATA = "ft4betjoinratedata"
FT5BETJOINRATEDATA = "ft5betjoinratedata"

STJOINRATEDATA = "stjoinratedata"
ST3BETJOINRATEDATA = "st3betjoinratedata"
ST4BETJOINRATEDATA = "st4betjoinratedata"
ST5BETJOINRATEDATA = "st5betjoinratedata"

FTREPAIRJOINRATEDATA = "ftrepairjoinratedata"
FT3BETREPAIRJOINRATEDATA = "ft3betrepairjoinratedata"
FT4BETREPAIRJOINRATEDATA = "ft4betrepairjoinratedata"
FT5BETREPAIRJOINRATEDATA = "ft5betrepairjoinratedata"

STREPAIRJOINRATEDATA = "strepairjoinratedata"
ST3BETREPAIRJOINRATEDATA = "st3betrepairjoinratedata"
ST4BETREPAIRJOINRATEDATA = "st4betrepairjoinratedata"
ST5BETREPAIRJOINRATEDATA = "st5betrepairjoinratedata"

UPLOAD_FOLDER = '/mnt/mfs/users/zoul15/pmimg/'
OCR_ERROR_FOLDER = "/mnt/mfs/users/zoul15/errorimg/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

NAMEIMGPREFIX = "shotname"

HANDSTHRE = 100
STATETHRE = 1

BELIEVERATE = 60
FILTERHANDS = 20

PREFLOPGENERALSTATE = "preflopgeneralstate"

def getprefloprangefield(curturn,betlevel):
    if betlevel == 3:
        return A3BETDATA
    elif betlevel == 4:
        return A4BETDATA
    elif betlevel >= 5:
        return A5BETDATA

    if curturn == 1:
        return FTDATA
    else:
        return STDATA


# ========================game level related=============================
BB = 10
ANTI = 2

# ========================cache data related=============================
# CACHEDIR = "/mnt/mfs/users/zoul15/pokercachedata/"
CACHEDIR = "/home/zoul15/temp/"
AFTERFLOPSTATEHEADER = CACHEDIR + "afterflopstateheader"
AFTERFLOPSTATEDATA = CACHEDIR + "afterflopstatedata"

# ========================hands strength related=====================
COMPLETESTRENGTHMAPPREFIX = CACHEDIR + "strengthmap"
REVERSECOMPLETESTRENGTHMAPPREFIX = CACHEDIR + "reversestrengthmap"

PRIVATECARDSSTRENGTH = CACHEDIR + "privatecardsstrength"

SCORERANGE = 50 # lower, pair gets priority

NEWSTRENGTHMAP = CACHEDIR + "newstrengthmap"

    # ----------------------next turn strength histogram----------------
HANDSTRENGTHSLOT = 0.04

# ========================board value related================================
BOARDVALUE = CACHEDIR + "boardvalue"

# ========================state related======================================
STATEKEY =  "statekeys"

# ========================symbol======================================
TAB = "\t"
SPACE = " "
DOT = ","

# =========================pos related===================================
SBPOS = 9
BBPOS = 8

# =========================nearest state related=========================
CURWINRATETHRE = 0.05
HISTOGRAMTHRE = 1

# =========================other==========================================
THREADNUM = 15