import hunlgame
from Constant import *
from handspower import *
import numpy as np
import tensorflow as tf
from tensorflow import keras
import time
import logging

# Metadata describing the text columns
COLUMNS = [str(i) for i in xrange(1326 + 5 * 5)] + ["label",]
FIELD_DEFAULTS = [[0.0]] * (1326 + 5 * 5 + 1)
def _parse_line(line):
    # Decode the line into its fields
    fields = tf.decode_csv(line, FIELD_DEFAULTS,field_delim=' ')

    # Pack the result into a dictionary
    features = dict(zip(COLUMNS,fields))

    # Separate the label from the features
    label = features.pop('label')

    return features, label

def csv_input_fn(fname):
    ds = tf.data.TextLineDataset(fname)
    ds = ds.map(_parse_line)
    # print ds
    # Shuffle, repeat, and batch the examples.
    dataset = ds.shuffle(10000).repeat().batch(1000)

    # Return the dataset.
    return dataset

def train():
    my_feature_columns = []
    for key in xrange(1326 + 5 * 5):
        my_feature_columns.append(tf.feature_column.numeric_column(key=str(key)))
    estimator = tf.estimator.DNNRegressor(feature_columns = my_feature_columns, hidden_units=[500, 500, 500, 500, 500, 500],model_dir = "")
    logging.getLogger().setLevel(logging.INFO)
    # estimator.train(input_fn=lambda:csv_input_fn(TRAINDATAFILENORMALIZE),steps=400000)
    print "start evaluate"
    for idx in xrange(26):
        eval_result = estimator.evaluate(input_fn=lambda:csv_input_fn(TESTDATAFILENORMALIZE+str(idx)+".csv"))
        print "test idx:",idx
        for key, value in eval_result.items():
            print key,"\t",value

class MLHandPower:
    def __init__(self):
        self.m_handsmap = None

    def transferdata(self):
        self.inithandsmap()
        self.m_cardidx = []

        ifile = open(TRAINDATAFILE)
        ofile = open(TRAINDATAFILENORMALIZE,"w")
        testofile = []
        for idx in xrange(26):
            testofile.append( open(TESTDATAFILENORMALIZE + str(idx)+".csv","w"))
        flen = 0
        for line in ifile:
            flen += 1
        ifile.close()
        ifile = open(TRAINDATAFILE)
        trainlen = flen * 0.8
        idxxx = 0
        for line in ifile:
            idxxx += 1
            if idxxx % 20000 == 0:
                print idxxx / 2
            line = line.strip()
            if line == "":
                continue
            data = line.split(" ")
            myhand = data[0]
            board = data[1]
            opponum = int(data[2])
            oppohandsnum = int(data[3])
            curdata = [0] * (1326 + 5 * 5)
            for idx, card in enumerate(hunlgame.generateCards(myhand + board)):
                curdata[idx * 5] = card.value / 14.0
                curdata[idx * 5 + card.symbol + 1] = 1
                if idxxx == 1:
                    self.m_cardidx.append(idx * 5)
            for idx in xrange(oppohandsnum):
                oppohand = data[4 + idx * 2]
                oppohandrate = float(data[5 + idx * 2])
                curdata[5 * 5 + self.m_handsmap[oppohand]] = oppohandrate
            hpstr = data[-1]
            hp = HandPower(winratestr = hpstr)
            curdata.append(hp.m_curwinrate)
            if idxxx < trainlen:
                ofile.write(" ".join([str(v) for v in curdata]) + "\n")
            else:
                testofile[int(hp.m_curwinrate/0.04)].write(" ".join([str(v) for v in curdata]) + "\n")
        ifile.close()
        ofile.close()
        for v in testofile:
            v.close()

    def inithandsmap(self):
        print "initing handsmap"
        if self.m_handsmap is not None:
            return
        self.m_handsmap = {}
        rangeobj = hunlgame.HandsRange()
        rangeobj.addFullRange()
        fullhandslist = rangeobj.get()
        handsstrlist = [v.cppstr() for v in fullhandslist]
        for idx,handsstr in enumerate(handsstrlist):
            self.m_handsmap[handsstr] = idx

if __name__ == "__main__":
    train()
    # MLHandPower().transferdata()