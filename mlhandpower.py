import hunlgame
from Constant import *
from handspower import *
import numpy as np
import tensorflow as tf
from tensorflow import keras

class MLHandPower:
    def __init__(self):
        self.m_handsmap = None
        self.m_traindata = None
        self.m_trainlabel = None
        self.m_testdata = None
        self.m_testlabel = None
        self.m_model = None
        self.m_cardidx = None

    def run(self):
        self.loaddata(TRAINDATAFILE)
        self.normalizetraindata()
        self.buildmodel()
        self.train()
        print(self.evaluate())

    def train(self):
        self.m_model.fit(self.m_traindata,self.m_trainlabel, epochs = 5)

    def evaluate(self):
        test_loss, test_acc = self.m_model.evaluate(self.m_testdata, self.m_testlabel)
        return [test_loss, test_acc]

    def buildmodel(self):
        self.m_model = keras.Sequential([
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(47, activation=tf.nn.softmax)
        ])
        self.m_model.compile(optimizer=tf.train.AdamOptimizer(),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

    def normalizetraindata(self):
        for idx in self.m_cardidx:
            self.m_traindata[:,idx] = self.m_traindata[:,idx] / 14.0
            self.m_testdata[:,idx] = self.m_testdata[:,idx] / 14.0

    def loaddata(self, fname, testdatarate = 0.2):
        self.inithandsmap()
        self.m_cardidx = []
        ifile = open(fname)
        traindata = []
        labeldata = []
        for line in ifile:
            data = line.strip().split(" ")
            myhand = data[0]
            board = data[1]
            opponum = int(data[2])
            oppohandsnum = int(data[3])
            curdata = [0] * (1326 + 5 * 5)
            for idx, card in enumerate(hunlgame.generateCards(myhand + board)):
                curdata[idx * 5] = card.value
                self.m_cardidx.append(idx * 5)
                curdata[idx * 5 + card.symbol + 1] = 1
            for idx in xrange(oppohandsnum):
                oppohand = data[4 + idx]
                oppohandrate = float(data[5 + idx])
                curdata[5 * 5 + self.m_handsmap[oppohand]] = oppohandrate
            traindata.append(curdata)
            hpstr = data[-1]
            hp = HandPower(hpstr)
            labeldata.append(hp.m_data[0])
        testdatalen = int(len(traindata) * testdatarate)
        self.m_testdata = np.array(traindata[:testdatalen])
        self.m_testlabel = np.array(labeldata[:testdatalen])
        self.m_traindata = np.array(traindata[testdatalen:])
        self.m_trainlabel = np.array(labeldata[testdatalen:])

    def inithandsmap(self):
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
    MLHandPower().run()