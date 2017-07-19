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
    # if curturn == 1:
    #     if betlevel <= 2:
    #         return FTREPAIRJOINRATEDATA
    #     elif betlevel == 3:
    #         return FT3BETREPAIRJOINRATEDATA
    #     elif betlevel == 4:
    #         return FT4BETREPAIRJOINRATEDATA
    #     else:
    #         return FT5BETREPAIRJOINRATEDATA
    # else:
    #     if betlevel <= 2:
    #         return STREPAIRJOINRATEDATA
    #     elif betlevel == 3:
    #         return ST3BETREPAIRJOINRATEDATA
    #     elif betlevel == 4:
    #         return ST4BETREPAIRJOINRATEDATA
    #     else:
    #         return ST5BETREPAIRJOINRATEDATA

# ========================game level related=============================
BB = 10
ANTI = 2

# ========================cache data related=============================
CACHEDIR = "/mnt/mfs/users/zoul15/pokercachedata/"
AFTERFLOPSTATEHEADER = CACHEDIR + "afterflopstateheader"
AFTERFLOPSTATEDATA = CACHEDIR + "afterflopstatedata"

# ========================hands strength related=====================
COMPLETESTRENGTHMAPPREFIX = CACHEDIR + "strengthmap"
REVERSECOMPLETESTRENGTHMAPPREFIX = CACHEDIR + "reversestrengthmap"

PRIVATECARDSSTRENGTH = CACHEDIR + "privatecardsstrength"

SCORERANGE = 50 # lower, pair gets priority

# ========================board value related================================
BOARDVALUE = CACHEDIR + "boardvalue"

# ========================symbol======================================
TAB = "\t"
SPACE = " "
DOT = ","

# =========================pos related===================================
SBPOS = 9
BBPOS = 9
