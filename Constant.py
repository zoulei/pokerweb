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
PREFLOPRANGEDOC = "prefloprange"\

FTDATA = "ftdata"
FT3BETDATA = "ft3betdata"
FT4BETDATA = "ft4betdata"
FT5BETDATA = "ft5betdata"

STDATA = "stdata"
ST3BETDATA = "st3betdata"
ST4BETDATA = "st4betdata"
ST5BETDATA = "st5betdata"

JOINRATEDATA = "joinratedata"
FT3BETJOINRATEDATA = "ft3betjoinratedata"
FT4BETJOINRATEDATA = "ft4betjoinratedata"
FT5BETJOINRATEDATA = "ft5betjoinratedata"


REPAIRJOINRATE = "repairjoinrate"
FT3BETREPAIRJOINRATE = "ft3betrepairjoinrate"

UPLOAD_FOLDER = '/mnt/mfs/users/zoul15/pmimg/'
OCR_ERROR_FOLDER = "/mnt/mfs/users/zoul15/errorimg/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

NAMEIMGPREFIX = "shotname"

HANDSTHRE = 100
STATETHRE = 1

BELIEVERATE = 60
FILTERHANDS = 20

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

SCORERANGE = 50

# ========================symbol======================================
TAB = "\t"
SPACE = " "
DOT = ","

