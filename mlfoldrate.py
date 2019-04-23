import numpy as np
import tensorflow as tf
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# import tensorflow_lattice as tfl
import logging
import Constant

def trainpolynomial(fname, ofname, validdatalen, complex = 5):
    REGULARIZATION = False
    ALPHA = 0.00001
    ifile = open(fname)
    xdata = []
    ydata = []
    misslen = 0
    fullxdata = []
    weightdata = []
    for line in ifile:
        tmpdata = line.strip().split("\t")
        fullxdata.append(int(tmpdata[0]) * Constant.HPVALUESLOT)
        curvalue = float(tmpdata[1])
        if curvalue < -1:
            misslen += 1
            continue
        # xdata.append(int(tmpdata[0]))
        xdata.append(int(tmpdata[0]) * Constant.HPVALUESLOT)
        ydata.append(float(tmpdata[1]))
        weightdata.append(float(tmpdata[2]))
    ifile.close()
    n = sum(weightdata)
    x = np.array(xdata[:validdatalen - misslen])
    y = np.array(ydata[:validdatalen - misslen])
    weightdata = np.array(weightdata[:validdatalen - misslen])
    X = tf.placeholder("float")
    Y = tf.placeholder("float")
    WEIGHT = tf.placeholder("float")

    COMPLEX = complex
    # B = tf.Variable(0.0,name = "B")
    weightvar = []
    y_pred = tf.add(1.0, 0.0)
    weightinitial = [0.2609869, -4.6568966, -1.8970723, 1.2587417]
    for pow_i in range(1, COMPLEX):
        W = tf.Variable(weightinitial[pow_i-1], name='weight_%d' % pow_i)
        y_pred = tf.add(tf.multiply(tf.pow(X, pow_i), W), y_pred)
        weightvar.append(W)

    learning_rate = 1
    training_epochs = 10000

    cost = tf.reduce_sum(tf.multiply(WEIGHT, tf.pow(tf.abs(y_pred - Y), 2))) / n

    if REGULARIZATION:
        reg = tf.add(0.0, 0.0)
        for i in range(1, COMPLEX):
            reg = tf.add(reg, tf.pow(weightvar[i-1], 2))
        reg = tf.pow(reg, 0.5)
        reg = tf.multiply(reg, ALPHA)
        cost = tf.add(cost, reg)
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)
    init = tf.global_variables_initializer()

    wlist = []
    prec = 10000
    with tf.Session() as sess:
        sess.run(init)
        for epoch in range(training_epochs):
            for (_x, _y, _w) in zip(x, y, weightdata):
                sess.run(optimizer, feed_dict={X: _x, Y: _y, WEIGHT: _w})
            if (epoch + 1) % 200 == 0:
                c = sess.run(cost, feed_dict={X: x, Y: y, WEIGHT: weightdata})
                print("Epoch", (epoch + 1), ": cost =", c)
                if prec - c < 0.0001:
                    break
                else:
                    prec = c
        training_cost = sess.run(cost, feed_dict={X: x, Y: y, WEIGHT: weightdata})

        for v in weightvar:
            wlist.append(sess.run(v))
    print("wlist:", wlist)
    predictions = []
    for v in x:
        curpre = 1.0
        for i in range(1, COMPLEX):
            # print ("i:", i, "\t", wlist[i] * pow(v, i), "\t", v, "\t", pow(v, i), "\t", wlist[i])
            curpre += wlist[i - 1] * pow(v, i)
        predictions.append(curpre)
    predictions = np.array(predictions)
    print("Training cost =", training_cost, '\n')

    # Plotting the Results
    plt.plot(x, y, 'ro', label='Original data')
    plt.plot(x, predictions, label='Fitted line')
    plt.title('Linear Regression Result')
    # plt.legend()
    plt.savefig("/home/zoul15/pcshareddir/gnuresult/mlfoldrate.png")

    realc = 0.0
    for y_true, y_pred in zip(y, predictions):
        realc += pow(y_pred - y_true, 2)
    print ("cccc:", realc / n)

if __name__ == "__main__":
    import time
    start = time.time()
    trainpolynomial("/home/zoul15/pcshareddir/gnudata/fulltestdata.csv", "", 36)
    print ("time:", time.time()-start)
    # lattice()