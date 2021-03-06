
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
import math

# FEATURELEN = 1023
FEATURELEN = 128
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
    # fields[0] = 0
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
    ifile = open(TRAINDATADIR + "4_allin")
    idx =0
    for line in ifile:
        data = line.strip().split(" ")
        idx += 1
        if len(data) != 125:
            print(line)
            print (len(data))
            print ("idx:",idx)
            break
    ifile.close()

def tongjiinfo(step, dataidx, maxvalue, pngidentity):
    plt.clf()
    # inputdata = pandas.read_csv(TRAINDATADIR+"4", sep=" ", usecols=[FEATURELEN], names=["label"])
    ifile = open(TRAINDATAFILE)
    idx = 0
    # step = 0.01
    # step = 1
    resultdata = dict()
    import math
    nannumber = 0
    spenumber = 0
    for line in ifile:
        idx += 1
        if idx == 10000:
            break
        # data = float(line.strip().split(" ")[-1])
        # data = float(line.strip().split(" ")[0])
        data = float(line.strip().split(" ")[dataidx])
        if data > maxvalue:
            data = maxvalue
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
        # if key > 200:
        #     key = 200
        # if key > 800:
        #     key = 800
        # if key > maxvalue:
        #     key = maxvalue
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
    plt.savefig("/home/zoul15/pcshareddir/gnuresult/ml" + str(TRAINTURN) + str(TRAINALLIN) + pngidentity + ".png")
    plt.clf()
    for i in range(1, len(valuelist)):
        valuelist[i] += valuelist[i - 1]
    for i in range(0, len(valuelist)):
        valuelist[i] /= valuelist[- 1] * 1.0
        if dataidx==3:
            print (i, ":", valuelist[i])
    # Plotting the Results
    plt.plot(keylist, valuelist, 'ro', label='Original data')
    plt.title('Label distribution')
    # plt.legend()
    plt.savefig("/home/zoul15/pcshareddir/gnuresult/ml" + str(TRAINTURN) + str(TRAINALLIN) + "cdf" + pngidentity + ".png")
    # print ("nannumber:", nannumber)
    # print ("spenumber:", spenumber)

class ErrorData:
    def __init__(self, step, maxvalue):
        self.m_error = 0.0
        self.m_bindata = []
        self.m_step = step
        self.m_binsize = int(maxvalue / step)
        for _ in range(self.m_binsize):
            self.m_bindata.append([0, 0])
        self.m_size = 0

    def AddData(self, value, realvalue):
        self.m_error += value
        binnumber = int(realvalue / self.m_step)
        if binnumber >= self.m_binsize:
            binnumber = self.m_binsize - 1
        self.m_bindata[binnumber][1] += 1
        self.m_bindata[binnumber][0] += value
        self.m_size += 1

    def PrintData(self, msg):
        print (msg)
        print ("error:", self.m_error if self.m_error == 0 else self.m_error / abs(self.m_error) * math.sqrt(abs(self.m_error) / self.m_size))
        print ("data size:", self.m_size)
        for i in range(len(self.m_bindata)):
            if self.m_bindata[i][1] != 0:
                print (i * self.m_step, ":", abs(self.m_bindata[i][0]) / self.m_bindata[i][0] * math.sqrt(abs(self.m_bindata[i][0]) / self.m_bindata[i][1]))

    def Plot(self, identifier):
        keylist = range(len(self.m_bindata))
        valuelist = []
        for v in self.m_bindata:
            if v[1]:
                valuelist.append(abs(v[0]) / v[0] * math.sqrt(abs(v[0]) / v[1]))
            else:
                valuelist.append(0)
        # valuelist = [math.sqrt(v[0] / v[1]) for v in self.m_bindata]
        plt.plot(keylist, valuelist, 'ro', label='Original data')
        plt.title('Label distribution')
        # plt.legend()
        plt.savefig(
            "/home/zoul15/pcshareddir/gnuresult/ml" + str(TRAINTURN) + str(TRAINALLIN) + identifier + ".png")

def testloadsavedmodel():
    from tensorflow.contrib import predictor
    import math

    predict_fn = predictor.from_saved_model("/home/zoul15/pcshareddir/rivermodel/1593740822/")
    print("feed_tensors:\n", predict_fn.feed_tensors)
    print("\nkeys:\n", predict_fn.feed_tensors.keys())
    testfeature = []
    # testlabel = []
    ifile = open(TESTDATAFILE)
    idx = 0
    # error = 0.0
    # rawmseerror = 0.0
    # mahatonerror = 0.0
    # rawmahatonerror = 0.0
    # bindata = []
    # rawmse = []
    # mahaton = []
    # rawmahaton = []
    # step = 0.01
    # binsize = int(2.0/step)
    # for i in range(binsize):
    #     bindata.append([0, 0])
    #     rawmse.append([0, 0])
    #     mahaton.append([0, 0])
    #     rawmahaton.append([0, 0])

    mseobj = ErrorData(0.01, 2)
    absmseobj = ErrorData(0.01, 2)
    mahatonobj = ErrorData(0.01, 2)
    absmahatonobj = ErrorData(0.01, 2)
    for line in ifile:
        idx += 1
        # if idx == 300:
        #     break
        data = line.strip().split(" ")
        data = [float(v) for v in data]
        testfeature.append(data[:-1])
        # testlabel.append(data[-1])

        featuredict = {}
        for i in range(len(data)-1):
            featuredict[str(i)] = data[i]
        # print(featuredict)

        feature = {}
        for k, v in featuredict.items():
            feature[k] = tf.train.Feature(float_list=tf.train.FloatList(value=[v]))
        model_input = tf.train.Example(features=tf.train.Features(feature=feature))
        model_input = model_input.SerializeToString()

        predictions = predict_fn({"inputs":[model_input,]})
        # print (predictions["outputs"][0][0])
        # print ("truth:", data[-1])
        curerror = (predictions["outputs"][0][0] - data[-1])*(predictions["outputs"][0][0] - data[-1])
        mseobj.AddData(curerror, data[-1])
        currawmseerror = (predictions["outputs"][0][0] - data[-1])*abs(predictions["outputs"][0][0] - data[-1])
        absmseobj.AddData(currawmseerror, data[-1])
        curmahatonerror = abs(predictions["outputs"][0][0] - data[-1])
        mahatonobj.AddData(curmahatonerror, data[-1])
        if data[-1] < 0.01 and curmahatonerror > 0.1:
            print(predictions["outputs"][0][0])
            print(line)
        currawmahatonerror = predictions["outputs"][0][0] - data[-1]
        absmahatonobj.AddData(currawmahatonerror, data[-1])
        # error += curerror
        # rawmseerror += currawmseerror
        # mahatonerror += curmahatonerror
        # rawmahatonerror += currawmahatonerror
        # binnumber = int(data[-1]/step)
        # if binnumber >= binsize:
        #     binnumber = binsize - 1
        # bindata[binnumber][1] += 1
        # bindata[binnumber][0] += curerror
        # rawmse[binnumber][1] += 1
        # rawmse[binnumber][0] += currawmseerror
        # mahaton[binnumber][1] += 1
        # mahaton[binnumber][0] += curmahatonerror
        # rawmahaton[binnumber][1] += 1
        # rawmahaton[binnumber][0] += currawmahatonerror
    ifile.close()
    mseobj.PrintData("mse result:")
    mseobj.Plot("mse_result")
    absmseobj.PrintData("nonabs mse result:")
    absmseobj.Plot("nonabs_mse_result")
    mahatonobj.PrintData("mahaton result:")
    mahatonobj.Plot("mahaton_result")
    absmahatonobj.PrintData("nonabs mahaton result:")
    absmahatonobj.Plot("nonabs_mahaton_result")


    # print ("error:", math.sqrt(error/idx))
    # print ("data size:", idx)
    # for i in range(len(bindata)):
    #     if bindata[i][1] != 0:
    #         print (i*step, ":", math.sqrt(bindata[i][0]/bindata[i][1]))
    #
    # keylist = range(len(bindata))
    # valuelist = [math.sqrt(v[0]/v[1]) for v in bindata]
    # plt.plot(keylist, valuelist, 'ro', label='Original data')
    # plt.title('Label distribution')
    # # plt.legend()
    # plt.savefig(
    #     "/home/zoul15/pcshareddir/gnuresult/ml" + str(TRAINTURN) + str(TRAINALLIN) + "msedistribution" + ".png")
    #
    #
    # print ("error:", math.sqrt(error/idx))
    # print ("data size:", idx)
    # for i in range(len(bindata)):
    #     if bindata[i][1] != 0:
    #         print (i*step, ":", math.sqrt(bindata[i][0]/bindata[i][1]))
    #
    # keylist = range(len(bindata))
    # valuelist = [math.sqrt(v[0]/v[1]) for v in bindata]
    # plt.plot(keylist, valuelist, 'ro', label='Original data')
    # plt.title('Label distribution')
    # # plt.legend()
    # plt.savefig(
    #     "/home/zoul15/pcshareddir/gnuresult/ml" + str(TRAINTURN) + str(TRAINALLIN) + "msedistribution" + ".png")


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

    # typeone = [[1, "isopener"], [2, "hasopener"], [3, "relativetoopener"], [17, "hasflopraiser"], [18, "flopraiser"],
    #            [19, "hasturnraiser"], [20, "turnraiser"]]
    # typetwo = [[4, "turn"], [6, "remaintoact"], [7, "remainraiser"], [8, "preflopinitialpq"], [9, "flopinitialpq"],
    #            [10, "turninitialpq"], [11, "riverinitialpq"]]
    # typethree = [[12, "raiserstackvalue"], [13, "remainstackvalue"], [14, "preflopattackvalue"], [15, "currentattackvalue"],
    #              [16, "afterflopattackvalue"]]
    # featureinfo = [[1, 0, 800, "pot"], [0.01, -1, 2, "ev"], [0.1, 1, 10, "stackpotratio"], [0.05, 2, 1, "curwinrate"], [0.05, 3, 1, "hpvalue"],
    #                [0.1, 4, 1, "relativepos"], [1, 5, 1, "cancheck"], [0.5, 6, 10, "odds"], ]
    # for idx, identi in typeone:
    #     featureinfo.append([1, idx + 6, 1, identi])
    # for idx, identi in typetwo:
    #     featureinfo.append([1, idx + 6, 10, identi])
    # for idx, identi in typethree:
    #     featureinfo.append([0.1, idx + 6, 10, identi])
    # for idx in range(27, FEATURELEN):
    #     featureinfo.append([0.1, idx, 10, "winrate_" + str(idx - 27)])
    # for v in featureinfo:
    #     print ("v:::::", v)
    #     tongjiinfo(*v)

    # savedatatotfrecord(TRAINDATADIR+"train.csv")

    # train1()
    # findtargetdata()
    testloadsavedmodel()
    # tf.logging.set_verbosity(tf.logging.INFO)
    # tf.app.run(main=train)