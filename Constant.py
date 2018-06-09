# MONGOHOST = '192.168.112.111'
# MONGOHOST = '192.168.66.1'
MONGOHOST = "data3,data2,data1"
#MONGOHOST = 'localhost'
# MONGOPORT = 27017
# DBUSERNAME = 'root'
# DBPWD = "123459"
DBUSERNAME = 'cltreedb'
DBPWD = "Wv8Yg5gJD"
AUTHDBNAME = "admin"

LOGINDB = "pmdb"
LOGINCLT = "loginclt"

# HANDSDB = "handsdb"
HANDSDB = "cltreedb"
HANDSCLT = "handsclt"
STATEINFOHANDSCLT = "stateinfohandsclt"

TESTCLT = "testclt"
RAWHANDSCLT = "rawhandsclt"
HISHANDSCLT = "hishandsclt"
TJHISHANDSCLT = "tjhishandsclt"
TJHANDSCLT = "tjhandsclt"

GAMESEQCLT = "gameseqclt"
COLLECTGAMECLT = "collectgameclt"

CUMUCLT = "cumuclt"

# =====================preflop state related=============================
PREFLOPINPOOLSTATE = "preflopinpoolstate"
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
CACHEDIR = "/dev/shm/home/zoul15/temp/"
SUBMITTASKDIR = CACHEDIR + "submittask/"
TEMPSUBMITTASKDIR = CACHEDIR + "tmpsubmittask/"
TASKRESULTDIR = CACHEDIR + "taskresult/"
TEMPTASKRESULTDIR = CACHEDIR + "tmptaskresult/"
AFTERFLOPSTATEHEADER = CACHEDIR + "afterflopstateheader"
AFTERFLOPSTATEDATA = CACHEDIR + "afterflopstatedata"
DATADIR = "data/"

# ========================hands strength related=====================
COMPLETESTRENGTHMAPPREFIX = CACHEDIR + "strengthmap"
REVERSECOMPLETESTRENGTHMAPPREFIX = CACHEDIR + "reversestrengthmap"

PRIVATECARDSSTRENGTH = CACHEDIR + "privatecardsstrength"

SCORERANGE = 50 # lower, pair gets priority

NEWSTRENGTHMAP = CACHEDIR + "newstrengthmap"

ALLHANDSSTRENGTH = CACHEDIR + "calculateallhandsstrength"
ALLHANDSRANK = CACHEDIR + "calculateallhandsrank"
ALLHANDSRANKINMEMORYJSON = CACHEDIR + "allhandsrankinmemoryjson"
ALLHANDSRANKINMEMORYSTR = CACHEDIR + "allhandsrankinmemorystr"

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

# =========================hands power related===========================
CURWINRATEDIFFRATE = 25

# =========================other==========================================
THREADNUM = 10

# =========================state related===================================
ISOPENER = "isopener"
HASOPENER = "hasopener"
RELATIVETOOPENER = "relativetoopener"
TURN = "turn"

RELATIVEPOS = "relativepos"

REMAINTOACT = "remaintoact"
REMAINRAISER = "remainraiser"
ODDS = "odds"
POTSIZE = "potsize"
#INITIALPLAYERQUANTITY = "initialplayerquantity"
RAISERSTACKVALUE = "raiserstackvalue"
REMAINSTACKVALUE = "remainstackvalue"
PREFLOPINITALPQ = "preflopinitalpq"
FLOPINITALPQ = "flopinitalpq"
TURNINITALPQ = "turninitalpq"
RIVERINITALPQ = "riverinitalpq"

PREFLOPATTACKVALUE = "preflopattackvalue"
CURRENTATTACKVALUE = "currentattackvalue"
AFTERFLOPATTACKVALUE = "afterflopattackvalue"

# ============================phone related=================================
def getphoneid(phonecolor):
    if phonecolor == "b":
        return "353570060047458"
    elif phonecolor == "w":
        return "358584050326264"
    elif phonecolor == "r":
        return "353570060930398"
    return "NA"

def getphonecolor(phoneid):
    if phoneid == "353570060047458":
        return "b"
    elif phoneid == "358584050326264":
        return "w"
    elif phoneid == "353570060930398":
        return "r"
    return "NA"

# ==============================handspower related============================
HANDSPOWERGRANULARITY = 0.5
HANDSPOWERMARKER = DATADIR + "handspowermarker"

# ===============================actionn related==============================
CHECK = "check"
CALL = "call"
RAISE = "raise"
FOLD = "fold"

# ===============================turn related=================================
TURNPREFLOP = "PREFLOP"
TURNFLOP = "FLOP"
TURNTURN = "TURN"
TURNRIVER = "RIVER"

# ===============================field related================================
REALBETDATA = "REALBETDATA"

# ===============================calculate time related=======================
SYNC = False

# ===============================train state strategy related=================
FILEQUANTITYTHRE = 10000