
from Constant import *
import tensorflow as tf
import logging
import time
import pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FEATURELEN = 123
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
    dataset = dataset.shuffle(100000).repeat().batch(1000)
    dataset = dataset.prefetch(10000)
    dataset = dataset.make_one_shot_iterator().get_next()
    # return features, labels
    return dataset

def csv_input_fn(fname):
    ds = tf.data.TextLineDataset(fname)
    ds = ds.map(_parse_line, 22)
    # print ds
    # Shuffle, repeat, and batch the examples.
    dataset = ds.shuffle(100000).batch(1000).repeat()
    dataset = dataset.prefetch(1000)
    # Return the dataset.
    return dataset

def csv_input_fn_evaluate(fname):
    ds = tf.data.TextLineDataset(fname)
    ds = ds.map(_parse_line)
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
    # Pack the result into a dictionary
    features = dict(zip(COLUMNS, fields))
    # Separate the label from the features
    label = features.pop('label')
    return features, label



def absdifloss(labels, logits):
    return tf.math.abs(tf.math.subtract(labels, logits))

def serving_input_receiver_fn():
    # my_feature_columns = []
    # for key in range(FEATURELEN):
    #     my_feature_columns.append(tf.feature_column.numeric_column(key=str(key)))
    # feature_spec = tf.feature_column.make_parse_example_spec(my_feature_columns)
    # return tf.estimator.export.build_parsing_serving_input_receiver_fn(feature_spec)
    # feature_spec = {'foo': tf.FixedLenFeature([], dtype=tf.float32),
    #                 'bar': tf.FixedLenFeature([], dtype=tf.float32)}
    feature_spec = {}
    for key in range(FEATURELEN):
    #     # feature_spec[str(key)] = tf.FixedLenFeature([], dtype=tf.float32)
        feature_spec[str(key)] = tf.placeholder(dtype=tf.float32, shape=[1], name=str(key))
    # serialized_tf_example = tf.placeholder(dtype=tf.float32, shape=[9], name='input_example_tensor')
    # receiver_tensors = {'examples': serialized_tf_example}
    # features = tf.parse_example(serialized_tf_example, feature_spec)
    # return tf.estimator.export.ServingInputReceiver(feature_spec, feature_spec)
    return tf.estimator.export.build_raw_serving_input_receiver_fn(feature_spec)

    """Build the serving inputs."""
    # The outer dimension (None) allows us to batch up inputs for
    # efficiency. However, it also means that if we want a prediction
    # for a single instance, we'll need to wrap it in an outer list.
    # inputs = {"x": tf.placeholder(shape=[None, FEATURELEN], dtype=tf.float32)}
    # return tf.estimator.export.ServingInputReceiver(inputs, inputs)

def train1():
    # global_step = tf.Variable(0, trainable=False)
    boundaries = [2000000, ]
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
        hidden_units=[500, 500, 500, 500, 500, 500],
        model_dir="/home/zoul15/pcshareddir/riverregressor/",
        optimizer=lambda: tf.train.AdamOptimizer(learning_rate=tf.train.piecewise_constant(
            tf.train.get_global_step(), boundaries, values)),
        loss_reduction=tf.losses.Reduction.MEAN
    )
    logging.getLogger().setLevel(logging.INFO)
    # estimator.train(input_fn=lambda:get_dataset(TRAINDATADIR+"1.tfrecords"), steps=3500000)
    # estimator.train(input_fn=lambda: csv_input_fn(TRAINDATADIR + "train.csv"), steps=3500000)
    # estimator.export_saved_model("/home/zoul15/pcshareddir/rivermodel/", serving_input_receiver_fn)
    # return
    starttime = time.time()
    print ("start evaluate test")
    # # for idx in range(3,4):
    eval_result = estimator.evaluate(input_fn=lambda: csv_input_fn_evaluate(TRAINDATADIR + "test.csv"))
    # print ("test idx:",idx)
    for key, value in eval_result.items():
        print (key, "\t", value)
    print ("finish evaluate")
    print (time.time() - starttime)
    #
    starttime = time.time()
    print ("start evaluate train")
    # for idx in range(3,4):
    eval_result = estimator.evaluate(input_fn=lambda: csv_input_fn_evaluate(TRAINDATADIR + "train.csv"))
    # print ("test idx:",idx)
    for key, value in eval_result.items():
        print (key, "\t", value)
    print ("finish evaluate")
    print (time.time() - starttime)

    # starttime = time.time()
    # predict_result = estimator.predict(input_fn=lambda: csv_input_fn_predict(TRAINDATADIR + "train.csv"))
    # print ("predict time:", time.time() - starttime)

    # ifile = open(TRAINDATADIR + "train.csv")
    # real_data = []
    # for line in ifile:
    #     real_data.append(line.strip().split(" ")[-1])
    # ifile.close()
    # lossdata = []
    # for i, v in enumerate(predict_result):
    #     try:
    #         lossdata.append(abs(float(real_data[i]) - v["predictions"][0])/float(real_data[i]))
    #     except:
    #         print (i, "\tv:", type(v), v)
    #         print ("avgloss:", sum(lossdata) / len(lossdata))
    #         raise
    #
    # step = 5
    # resultdata = dict()
    # for data in lossdata:
    #     # data = float(line.strip().split(" ")[-1])
    #     key = int(data / step)
    #     if key not in resultdata:
    #         resultdata[key] = 0
    #     resultdata[key] += 1
    # ifile.close()
    # maxkey = max(resultdata.keys())
    # keylist = range(maxkey + 1)[:20]
    # valuelist = []
    # for v in keylist:
    #     if v in resultdata:
    #         valuelist.append(resultdata[v])
    #     else:
    #         valuelist.append(0)
    # for i in range(1, len(valuelist)):
    #     valuelist[i] += valuelist[i - 1]
    # for i in range(len(valuelist)):
    #     valuelist[i] = valuelist[i] * 1.0 / sum(resultdata.values())
    # # Plotting the Results
    # plt.plot(keylist, valuelist, 'ro', label='Original data')
    # plt.title('Linear Regression Result')
    # # plt.legend()
    # plt.savefig("/home/zoul15/pcshareddir/gnuresult/mllossdata.png")

    # print ("sum:",sum(lossdata),len(lossdata))
    # print ("avgloss:",sum(lossdata)/len(lossdata))
    # print ("nonavgloss:",sum(nonabslossdata)/len(nonabslossdata))

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

def tongjiinfo():
    # inputdata = pandas.read_csv(TRAINDATADIR+"4", sep=" ", usecols=[FEATURELEN], names=["label"])
    ifile = open(TRAINDATADIR+"2")
    idx=0
    step = 10
    resultdata = dict()
    for line in ifile:
        idx+=1
        data = float(line.strip().split(" ")[-1])
        key = int(data / step)
        if key not in resultdata:
            resultdata[key] = 0
        resultdata[key]+=1
    ifile.close()
    maxkey = max(resultdata.keys())
    keylist = range(maxkey + 1)
    valuelist = []
    for v in keylist:
        if v in resultdata:
            valuelist.append(resultdata[v])
        else:
            valuelist.append(0)
    for i in range(1, len(valuelist)):
        valuelist[i] += valuelist[i - 1]
    # Plotting the Results
    plt.plot(keylist, valuelist, 'ro', label='Original data')
    plt.title('Linear Regression Result')
    # plt.legend()
    plt.savefig("/home/zoul15/pcshareddir/gnuresult/mlfoldrate.png")

def testloadsavedmodel():
    from tensorflow.contrib import predictor

    predict_fn = predictor.from_saved_model("/home/zoul15/pcshareddir/rivermodel/1559756321/")
    print("feed_tensors:\n", predict_fn.feed_tensors)
    print("\nkeys:\n", predict_fn.feed_tensors.keys())
    testfeature = []
    testlabel = []
    ifile = open(TRAINDATADIR+"test.csv")
    idx = 0
    for line in ifile:
        idx += 1
        if idx == 10:
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
            featuredict[str(i)].append([testfeature[j][i],])
    predictions = predict_fn(featuredict)
    # predictions = predict_fn({"inputs": testfeature})
    print (predictions)
    # predictions = predict_fn(
    #     {"x": [[6.4, 3.2, 4.5, 1.5],
    #            [5.8, 3.1, 5.0, 1.7]]})
    # print(predictions['scores'])

if __name__ == "__main__":
    # tongjiinfo()
    # savedatatotfrecord(TRAINDATADIR+"train.csv")
    train1()
    # testloadsavedmodel()
    # tf.logging.set_verbosity(tf.logging.INFO)
    # tf.app.run(main=train)