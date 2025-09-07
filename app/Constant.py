# MONGOHOST = '192.168.112.111'
# MONGOHOST = '192.168.66.1'
# MONGOHOST = "data3,data2,data1"
MONGOHOST = "192.168.1.7"
REALTIMESERVERHOST = "192.168.0.11"

# MONGOHOST = "39.98.238.20"
# MONGOHOST = 'localhost'
# MONGOPORT = 27017
# DBUSERNAME = 'root'
# DBPWD = "123459"
DBUSERNAME = 'straddlecltreedb'
DBPWD = "Wv8Yg5gJD"
AUTHDBNAME = "admin"

LOGINDB = "pmdb"
LOGINCLT = "loginclt"

# HANDSDB = "handsdb"
# HANDSDB = "myhandsdb"
HANDSDB = "straddlecltreedb"
# HANDSCLT = "handsclt"
# HANDSCLT = "1054988"
HANDSCLT = "111111"
ONLINECLT = "online_111111"
COLLECTINFOCLT = "collectinfo"
COLLECTCHECKROOM = "collectcheckroom"
# STATEINFOHANDSCLT = "stateinfohandsclt"
STATEINFOHANDSCLT = "stateinfo111111"

JOINEDROOMCLT = "joinedroom"
UPLOADSUCCESS = "uploadsuccess"

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
BB = 4
ANTI = 1

# ========================cache data related=============================
TRAINTURN = 4
TRAINALLIN = False
# CACHEDIR = "/mnt/mfs/users/zoul15/pokercachedata/"
CACHEDIR = "/home/zoul15/pcshareddir/"
TRAINDATADIR  = CACHEDIR + "TRAINDATADIR/" + str(TRAINTURN) + "/"
TRAINDATAFILE = TRAINDATADIR + "randomtrain" + ("allin" if TRAINALLIN else "") + ".csv"
NORMALIZEDTRAINDATAFILE = TRAINDATADIR + "normalizedrandomtrain" + ("allin" if TRAINALLIN else "") + ".csv"
COMBINEDTRAINDATAFILE = TRAINDATADIR + "combinedrandomtrain" + ("allin" if TRAINALLIN else "") + ".csv"
def get_combined_train_data_file(step):
    return COMBINEDTRAINDATAFILE + "_" + str(step)
def get_normalized_train_data_file(step):
    return NORMALIZEDTRAINDATAFILE + "_" + str(step)

TESTDATAFILE = TRAINDATADIR + "test" + ("allin" if TRAINALLIN else "") + ".csv"
NORMALIZEDTESTDATAFILE = TRAINDATADIR + "normalizedtest" + ("allin" if TRAINALLIN else "") + ".csv"
COMBINEDTESTDATAFILE = TRAINDATADIR + "combinedtest" + ("allin" if TRAINALLIN else "") + ".csv"
def get_combined_test_data_file(step):
    return COMBINEDTESTDATAFILE + "_" + str(step)
def get_normalized_test_data_file(step):
    return NORMALIZEDTESTDATAFILE + "_" + str(step)

REGRESSORDIR = CACHEDIR + "regressor_combined/" + str(TRAINTURN) + ("allin" if TRAINALLIN else "") + "/"
def get_regressor_dir(step, layer):
    return CACHEDIR + "regressor_{}_{}/".format(str(step), "_".join([str(v) for v in layer])) + str(TRAINTURN) + ("allin" if TRAINALLIN else "") + "/"


def get_train_data_schema_file(step=0):
    if step==0:
        return "data/train_data_schema"
    else:
        return "data/train_data_schema_{}".format(step)

# REGRESSORDIR = CACHEDIR + "regressor_250/" + str(TRAINTURN) + ("allin" if TRAINALLIN else "") + "/"
# REGRESSORDIR = CACHEDIR + "regressor_three_layer/" + str(TRAINTURN) + ("allin" if TRAINALLIN else "") + "/"
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
STATEHANDSID = "statehandsid"
ACTIONIDX = "actionidx"
INPOOLSTATE = "inpoolstate"
NEXTPLAYER = "nextplayer"
SHOWCARD = "showcard"
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
FILEQUANTITYTHRE = 1000000

# ================================ml related==================================
# TRAINDATAFILE = CACHEDIR + "TRAINDATAFILE"
# TRAINDATAFILENORMALIZE = CACHEDIR + "TRAINDATAFILENORMALIZE.csv"
# SMALLTRAINDATAFILENORMALIZE = CACHEDIR + "TRAINDATAFILENORMALIZE1.csv"
# TESTDATAFILENORMALIZE = CACHEDIR + "TESTDATAFILENORMALIZE"
# MODELDIR = CACHEDIR + "modeldir/"

HPVALUESLOT = 0.01