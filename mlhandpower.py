
from Constant import *
import tensorflow as tf
import logging

# Metadata describing the text columns
COLUMNS = [str(i) for i in range(21)] + ["label",]
FIELD_DEFAULTS = [[0.0]] * (22)
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
    for key in range(21):
        my_feature_columns.append(tf.feature_column.numeric_column(key=str(key)))
    estimator = tf.estimator.DNNRegressor(feature_columns = my_feature_columns, hidden_units=[500, 500, 500, 500, 500, 500],model_dir = "")
    logging.getLogger().setLevel(logging.INFO)
    estimator.train(input_fn=lambda:csv_input_fn(CACHEDIR+"all.csv"),steps=1000000)
    print ("start evaluate")
    # for idx in range(3,4):
    eval_result = estimator.evaluate(input_fn=lambda:csv_input_fn(CACHEDIR+"10.csv"))
    print ("test idx:",idx)
    for key, value in eval_result.items():
        print (key, "\t", value)

if __name__ == "__main__":
    train()
    # MLHandPower().transferdata()