
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

from Constant import *
# import tensorflow as tf
import logging
import time
import pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# FEATURELEN = 1023
FEATURELEN = 124
# Metadata describing the text columns
COLUMNS = [str(i) for i in range(FEATURELEN)] + ["label", ]
FIELD_DEFAULTS = [[0.0]] * (FEATURELEN+1)


def savedatatotfrecord(fname):
    csv = pandas.read_csv(fname, sep=" ").values
    pos = fname.rfind(".")
    if pos == -1:
        tffname = fname+".tfrecords"
    else:
        tffname = fname[:pos] + ".tfrecords"
    with tf.python_io.TFRecordWriter(tffname) as writer:
        for row in csv:
            features, label = row[:-1], row[-1]
            example = tf.train.Example()
            example.features.feature["features"].float_list.value.extend(features)
            example.features.feature["label"].float_list.value.append(label)
            writer.write(example.SerializeToString())


def parse_function(example_proto):
    features = {
        'features': tf.FixedLenFeature((FEATURELEN,), tf.float32),
        'label': tf.FixedLenFeature((), tf.float32)
    }
    parsed_features = tf.parse_single_example(example_proto, features)
    my_features = {}
    for idx, v in enumerate(COLUMNS):
        my_features[v] = parsed_features["features"][idx]
    # features = dict(zip(COLUMNS, parsed_features["features"]))
    return my_features, parsed_features['label']


def get_dataset(fname):
    dataset = tf.data.TFRecordDataset([fname])
    dataset = dataset.map(parse_function, 22)
    dataset = dataset.shuffle(50000).repeat().batch(1000)
    # dataset = dataset.prefetch(10000)
    dataset = dataset.make_one_shot_iterator().get_next()
    # return features, labels
    return dataset

def csv_input_fn(fname):
    dataset = tf.data.TextLineDataset(fname)
    dataset = dataset.apply(tf.data.experimental.shuffle_and_repeat(50000))
    dataset = dataset.apply(tf.data.experimental.map_and_batch(map_func=_parse_line, batch_size=1000,num_parallel_calls=48))
    dataset = dataset.prefetch(50000)

    # dataset = tf.data.experimental.make_csv_dataset(
    #     fname,
    #     batch_size=1000,
    #     column_names=COLUMNS,
    #     column_defaults=FIELD_DEFAULTS,
    #     label_name="label",
    #     field_delim=" ",
    #     header=False,
    #     shuffle_buffer_size=100000,
    #     num_parallel_reads=48
    # )
    # Return the dataset.
    return dataset

def csv_input_fn_evaluate(fname):
    ds = tf.data.TextLineDataset(fname)
    ds = ds.map(_parse_line,44)
    # print ds
    # Shuffle, repeat, and batch the examples.
    dataset = ds.batch(1000)
    # Return the dataset.
    return dataset

def _parse_line_predict(line):
    # Decode the line into its fields
    fields = tf.decode_csv(line, FIELD_DEFAULTS,field_delim=' ')
    # Pack the result into a dictionary
    features = dict(zip(COLUMNS,fields))
    # Separate the label from the features
    label = features.pop('label')
    return features, label

def csv_input_fn_predict(fname):
    ds = tf.data.TextLineDataset(fname)
    ds = ds.map(_parse_line_predict)
    # print ds
    # Shuffle, repeat, and batch the examples.
    # dataset = ds.shuffle(10000).repeat().batch(1000)
    dataset = ds.batch(1000)
    # Return the dataset.
    return dataset

def _parse_line(line):
    # Decode the line into its fields
    fields = tf.decode_csv(line, FIELD_DEFAULTS, field_delim=' ')
    # fields = map(float, line.split(" "))
    # Pack the result into a dictionary
    features = dict(zip(COLUMNS, fields))
    # Separate the label from the features
    label = features.pop('label')
    return features, label



def absdifloss(labels, logits):
    return tf.math.abs(tf.math.subtract(labels, logits))

def serving_input_receiver_fn():
    feature_spec = {}
    for i in range(FEATURELEN):
        feature_spec[str(i)] = tf.FixedLenFeature(shape=[1], dtype=tf.float32)
    serialized_tf_example = tf.placeholder(dtype=tf.string, shape=[None], name="input_example_tensor")
    receiver_tensors = {"examples": serialized_tf_example}
    features = tf.parse_example(serialized_tf_example, feature_spec)
    return tf.estimator.export.ServingInputReceiver(features, receiver_tensors)

def countfile(fname):
    ifile = open(fname)
    cnt = 0
    for line in ifile:
        cnt += 1
    return cnt

def train1():
    linecnt = countfile(TRAINDATAFILE)
    print ("===========================steps:", linecnt * 3 // 10)
    # global_step = tf.Variable(0, trainable=False)
    # boundaries = [1900000, ]
    # boundaries = [800000, ] if (TRAINTURN == 4 or (TRAINTURN == 3 and TRAINALLIN)) else [400000, ]
    # boundaries = [320000, ] if (TRAINTURN == 4 or (TRAINTURN == 3 and TRAINALLIN)) else [160000, ]
    boundaries = [linecnt * 200 // 1000, ]
    # values = [0.001, 0.0001]
    values = [0.001, 0.0001]
    # learning_rate = tf.train.piecewise_constant(tf.train.get_global_step(), boundaries, values)

    my_feature_columns = []
    for key in range(FEATURELEN):
        my_feature_columns.append(tf.feature_column.numeric_column(key=str(key)))
    feature_spec = tf.feature_column.make_parse_example_spec(my_feature_columns)
    # export_input_fn = tf.estimator.export.build_parsing_serving_input_receiver_fn(feature_spec)
    # print ("feature spec:\n", feature_spec)
    # head = tf.estimator.regression_head(
    #     loss_reduction=tf.losses.Reduction.MEAN,
    #     loss_fn=absdifloss
    # )
    estimator = tf.estimator.DNNRegressor(
        # head=head,
        # activation_fn=tf.nn.relu,
        feature_columns=my_feature_columns,
        hidden_units=[500, 500, 500, 500, 500, ],
        model_dir=REGRESSORDIR,
        optimizer=lambda: tf.train.AdamOptimizer(learning_rate=tf.train.piecewise_constant(
            tf.train.get_global_step(), boundaries, values)),
        loss_reduction=tf.losses.Reduction.MEAN
    )
    print("=========================================TRAINDATAFILE::", TRAINDATAFILE)
    logging.getLogger().setLevel(logging.INFO)
    # estimator.train(input_fn=lambda:get_dataset(TRAINDATADIR+"1.tfrecords"), steps=3500000)
    # estimator.train(input_fn=lambda: csv_input_fn(TRAINDATAFILE), steps=1400000 if (TRAINTURN == 4 or (TRAINTURN == 3 and TRAINALLIN)) else 700000)
    # estimator.train(input_fn=lambda: csv_input_fn(TRAINDATAFILE),
    #                 steps=560000 if (TRAINTURN == 4 or (TRAINTURN == 3 and TRAINALLIN)) else 280000)
    estimator.train(input_fn=lambda: csv_input_fn(TRAINDATAFILE), steps=linecnt * 300 // 1000)
    # estimator.train(input_fn=lambda: csv_input_fn(TRAINDATAFILE), steps=80000)

                    # steps=560000 if (TRAINTURN == 4 or (TRAINTURN == 3 and TRAINALLIN)) else 280000)
    # estimator.train(input_fn=lambda: csv_input_fn(TRAINDATAFILE), steps=700000)
    # estimator.train(input_fn=lambda: csv_input_fn(TRAINDATAFILE), steps=2800000)
    estimator.export_saved_model("/home/zoul15/pcshareddir/rivermodel/", serving_input_receiver_fn, as_text=True)
    # return
    starttime = time.time()
    print ("start evaluate test")
    # # for idx in range(3,4):
    eval_result = estimator.evaluate(input_fn=lambda: csv_input_fn_evaluate(TESTDATAFILE))
    # print ("test idx:",idx)
    # eval_result = estimator.evaluate(input_fn=lambda: csv_input_fn_evaluate(TRAINDATADIR + "test.csv"))
    # print ("test idx:",idx)
    for key, value in eval_result.items():
        print (key, "\t", value)
    print ("finish evaluate")
    print (time.time() - starttime)

    starttime = time.time()
    print ("start evaluate train")
    # for idx in range(3,4):
    eval_result = estimator.evaluate(input_fn=lambda: csv_input_fn_evaluate(TRAINDATAFILE))
    # print ("test idx:",idx)
    for key, value in eval_result.items():
        print (key, "\t", value)
    print ("finish evaluate")
    print (time.time() - starttime)

    starttime = time.time()
    predict_result = estimator.predict(input_fn=lambda: csv_input_fn_predict(TESTDATAFILE))
    print ("predict time:", time.time() - starttime)

    ifile = open(TESTDATAFILE)
    real_data = []
    pot_data = []
    for line in ifile:
        real_data.append(float(line.strip().split(" ")[-1]) * float(line.strip().split(" ")[0]))
        pot_data.append(float(line.strip().split(" ")[0]))
    ifile.close()
    lossdata = []
    nonabslossdata = 0
    for i, v in enumerate(predict_result):
        try:
            nonabslossdata += float(real_data[i]) - v["predictions"][0] * pot_data[i]
            lossdata.append(abs(float(real_data[i]) - v["predictions"][0] * pot_data[i]))
        except:
            print (i, "\tv:", type(v), v)
            print ("avgloss:", sum(lossdata) / len(lossdata))
            raise

    print("real sum:", sum(real_data), "\tloss sum:", sum(lossdata), "\trate:", sum(lossdata) / sum(real_data))
    print("nonabslossdata:", nonabslossdata)
    print("abslossdata:", sum(lossdata))
    step = 5
    resultdata = dict()
    for data in lossdata:
        # data = float(line.strip().split(" ")[-1])
        key = int(data / step)
        if key not in resultdata:
            resultdata[key] = 0
        resultdata[key] += 1
    ifile.close()
    maxkey = max(resultdata.keys())
    keylist = range(maxkey + 1)[:20]
    valuelist = []
    for v in keylist:
        if v in resultdata:
            valuelist.append(resultdata[v])
        else:
            valuelist.append(0)
    for i in range(1, len(valuelist)):
        valuelist[i] += valuelist[i - 1]
    for i in range(len(valuelist)):
        valuelist[i] = valuelist[i] * 1.0 / sum(resultdata.values())
    # Plotting the Results
    plt.plot(keylist, valuelist, 'ro', label='Original data')
    plt.title('Linear Regression Result')
    # plt.legend()
    plt.savefig("/home/zoul15/pcshareddir/gnuresult/mllossdata.png")


def train():
    # global_step = tf.Variable(0, trainable=False)
    boundaries = [2000000, ]
    values = [0.001, 0.0001]
    # learning_rate = tf.train.piecewise_constant(tf.train.get_global_step(), boundaries, values)

    my_feature_columns = []
    for key in range(FEATURELEN):
        my_feature_columns.append(tf.feature_column.numeric_column(key=str(key)))
    estimator = tf.estimator.DNNRegressor(
        feature_columns=my_feature_columns,
        hidden_units=[200, 200, 200],
        model_dir="/home/zoul15/pcshareddir/riverregressormse/",
        optimizer=lambda: tf.train.AdamOptimizer(learning_rate=tf.train.piecewise_constant(
            tf.train.get_global_step(), boundaries, values)),
        loss_reduction=tf.losses.Reduction.MEAN,
    )
    logging.getLogger().setLevel(logging.INFO)
    # estimator.train(input_fn=lambda:csv_input_fn(TRAINDATADIR+"train.csv"), steps=3500000)
    estimator.train(input_fn=lambda: csv_input_fn(TRAINDATADIR + "train.csv"), steps=1000)
    starttime = time.time()
    print ("start evaluate")
    # for idx in range(3,4):
    eval_result = estimator.evaluate(input_fn=lambda: csv_input_fn_evaluate(TRAINDATADIR + "train.csv"))
    # print ("test idx:",idx)
    for key, value in eval_result.items():
        print (key, "\t", value)
    print ("finish evaluate")
    print (time.time() - starttime)

def testdata():
    ifile = open(TRAINDATAFILE)
    for line in ifile:
        data = line.strip().split(" ")[24:-1]
        for v in data:
            if 0 < float(v) < 1:
                print (line)
    ifile.close()

def tongjiinfo():
    plt.clf()
    # inputdata = pandas.read_csv(TRAINDATADIR+"4", sep=" ", usecols=[FEATURELEN], names=["label"])
    ifile = open(TRAINDATAFILE)
    idx = 0
    step = 0.01
    resultdata = dict()
    import math
    nannumber = 0
    spenumber = 0
    for line in ifile:
        idx += 1
        data = float(line.strip().split(" ")[-1])
        key = int(data / step)
        if key == 0:
            tmpdata = line.strip().split(" ")
            # printline = ""
            # for idx, v in enumerate(tmpdata):
            #     printline += str(idx) + ":" + v + "  "
            # print (printline + "\n")
            # if float(tmpdata[3]) > 0.03:
            #     print("=================================\n")
            #     spenumber += 1
        if math.isnan(key):
            nannumber += 1
            continue
        key = int(key)
        if key > 200:
            continue
        if key not in resultdata:
            resultdata[key] = 0
        resultdata[key] += 1
    ifile.close()
    maxkey = max(resultdata.keys())
    keylist = range(maxkey + 1)
    valuelist = []
    for v in keylist:
        if v in resultdata:
            valuelist.append(resultdata[v])
        else:
            valuelist.append(0)
    plt.plot(keylist, valuelist, 'ro', label='Original data')
    plt.title('Label distribution')
    # plt.legend()
    plt.savefig("/home/zoul15/pcshareddir/gnuresult/ml" + str(TRAINTURN) + str(TRAINALLIN) + "ev.png")
    plt.clf()
    for i in range(1, len(valuelist)):
        valuelist[i] += valuelist[i - 1]
    for i in range(0, len(valuelist)):
        valuelist[i] /= valuelist[- 1] * 1.0
        print (i, ":", valuelist[i])
    # Plotting the Results
    plt.plot(keylist, valuelist, 'ro', label='Original data')
    plt.title('Label distribution')
    # plt.legend()
    plt.savefig("/home/zoul15/pcshareddir/gnuresult/ml" + str(TRAINTURN) + str(TRAINALLIN) + "cdfev.png")
    print ("nannumber:", nannumber)
    print ("spenumber:", spenumber)

def testloadsavedmodel():
    from tensorflow.contrib import predictor

    predict_fn = predictor.from_saved_model("/home/zoul15/pcshareddir/rivermodel/1559839163/")
    print("feed_tensors:\n", predict_fn.feed_tensors)
    print("\nkeys:\n", predict_fn.feed_tensors.keys())
    testfeature = []
    testlabel = []
    ifile = open(TRAINDATADIR+"test.csv")
    idx = 0
    for line in ifile:
        idx += 1
        if idx == 2:
            break
        data = line.strip().split(" ")
        data = [float(v) for v in data]
        testfeature.append(data[:-1])
        testlabel.append(data[-1])
    ifile.close()
    featuredict = {}
    for i in range(len(testfeature[0])):
        featuredict[str(i)] = []
        for j in range(len(testfeature)):
            featuredict[str(i)]= testfeature[j][i]
    print(featuredict)

    feature = {}
    for k, v in featuredict.items():
        feature[k] = tf.train.Feature(float_list=tf.train.FloatList(value=[v]))
    model_input = tf.train.Example(features=tf.train.Features(feature=feature))
    model_input = model_input.SerializeToString()

    predictions = predict_fn({"inputs":[model_input,]})
    # predictions = predict_fn({"inputs": testfeature})
    print (predictions)
    # predictions = predict_fn(
    #     {"x": [[6.4, 3.2, 4.5, 1.5],
    #            [5.8, 3.1, 5.0, 1.7]]})
    # print(predictions['scores'])

def testpipline():
    ifile = open(TRAINDATADIR + "test.csv")
    nousedata = []
    idx = 1
    parsetime = 0
    floattime = 0
    ziptime = 0
    for line in ifile:
        start = time.time()
        for _ in range(10000):
            data = line.strip().split(" ")
            nousedata.append(data)
        data = line.strip().split(" ")
        if idx % 1 == 0:
            print ("|||||||||||||||||||||||||||||||", idx)
            parsetime += time.time() - start
            print ("parsetime:", parsetime)
        for _ in range(10000):
            data = list(map(float, data))
            # data = [float(v) for v in data]
            nousedata.append(data)
        if idx % 1 == 0:
            print ("-------------------------------", idx)
            # print (time.time() - start)
            # print (idx)
            # print ((time.time() - start) / idx)
            floattime += time.time() - start
            print ("floattime:", floattime)

        start = time.time()
        data = line.strip().split(" ")
        for _ in range(10000):
            # features = {"pp":data}
            features = dict(zip(COLUMNS, data))
            label = features.pop("label")
            nousedata.append(label)
        if idx % 1 == 0:
            print ("===============================",idx)
            # print (time.time() - start)
            # print (idx)
            # print ((time.time() - start) / idx)
            ziptime += time.time() - start
            print ("ziptime:", ziptime)
        nousedata = []
        idx += 1
    # print (time.time() - start)
    # print (idx)
    # print ((time.time() - start) / idx)

def findtargetdata():
    for i in [1,2,3,4]:
        print (i,"====================================================")
        ifile = open(TRAINDATADIR + str(i) )
        for line in ifile:
            if line.startswith("25 26.33") and float(line.split(" ")[2]) > 0.95:
                print(line)

if __name__ == "__main__":
    # testpipline()
    # testdata()
    # tongjiinfo()
    # savedatatotfrecord(TRAINDATADIR+"train.csv")

    # train1()
    findtargetdata()
    # testloadsavedmodel()
    # tf.logging.set_verbosity(tf.logging.INFO)
    # tf.app.run(main=train)