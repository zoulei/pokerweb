import os

def getallfile(dirname):
    allfname = []
    alldirname = [dirname,]
    while len(alldirname):
        curdir = alldirname.pop()
        # print "curdir:", curdir
        fnamelist = os.listdir(curdir)
        # print "fnamelist:", fnamelist
        for fname in fnamelist:
            curpath = os.path.join(curdir, fname)
            if os.path.isdir(curpath):
                alldirname.append(curpath)
            else:
                allfname.append(curpath)
    allfname = [v[len(dirname):] for v in allfname]
    return allfname

def removesamefileunderdir(cmpdir, targetdir):
    cmpallfname = getallfile(cmpdir)
    targetallfname = getallfile(targetdir)
    for fname in targetallfname:
        if fname in cmpallfname:
            os.remove(os.path.join(targetdir, fname))
        else:
            print "notnotno:", fname

if __name__ == "__main__":
    removesamefileunderdir("I:\pokerrobot/tools\AndroidKiller_v1.3.1\AndroidKiller_v1.3.1\projects\PokerMaster_update_kill_copy\Project\smali\okhttp3/",
                           "I:\pokerrobot/tools\AndroidKiller_v1.3.1\AndroidKiller_v1.3.1\projects/app-debug\Project\smali\okhttp3/")