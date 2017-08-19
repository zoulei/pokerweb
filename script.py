import Constant
import handsinfocommon
import sys

def tongjilabel(fname):
    f = open(Constant.CACHEDIR + fname)
    tjdict = {}
    for line in f:
        data = line.strip().split(Constant.TAB)
        label = data[2]
        if label not in tjdict:
            tjdict[label] = 0
        tjdict[label] += 1

    handsinfocommon.pp.pprint(tjdict)

if __name__ == "__main__":
    tongjilabel(sys.argv[1])