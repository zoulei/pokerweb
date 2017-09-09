import Constant
import os
import pickle

class PickleEngine:
    def __init__(self):
        pass

    @ staticmethod
    def tempdump(self, obj, fname):
        pickle.dump(obj, open(fname,"wb"))

    @ staticmethod
    def combine(self, ends, getrawkeyfunc, getfnamefunc, directory = Constant.CACHEDIR):
        filelist = os.listdir(directory)
        fnamedict = {}
        # tmpfnameobj = FnameManager()
        for fname in filelist:
            statekey = getrawkeyfunc(fname)
            if not statekey:
                continue
            if statekey not in fnamedict:
                fnamedict[statekey] = []
            fnamedict[statekey].append(fname)

        # load boardhistogram from temp file
        for statekey in fnamedict.keys():
            fnamelist = fnamedict[statekey]
            targetlist = []
            for fname in fnamelist:
                targetlist.append(pickle.load(open(Constant.CACHEDIR + fname,"rb")))
                os.remove(Constant.CACHEDIR + fname)
            fnamedict[statekey] = targetlist

        # load boardhistogram from file
        for statekey in fnamedict.keys():
            boardhisfname = getfnamefunc(statekey)
            boardhisobjlist = []
            fullboardhisfname = Constant.CACHEDIR + boardhisfname
            if os.path.exists(fullboardhisfname):
                boardhisobjlist = pickle.load(open(fullboardhisfname,"rb"))
            boardhisobjlist.extend(fnamedict[statekey])

            pickle.dump(boardhisobjlist, open(fullboardhisfname,"wb"))