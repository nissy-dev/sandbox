import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

rng = np.random.RandomState(1234)
random_state = 42

def load_mnist():
    # 学習データ
    x_train = np.load('./data/x_train.npy')
    t_train = np.load('./data/t_train.npy')
    
    # テストデータ
    x_test = np.load('./data/x_test.npy')

    x_train = x_train.reshape(-1, 28, 28, 1).astype('float32') / 255
    x_test = x_test.reshape(-1, 28, 28, 1).astype('float32') / 255
    t_train = np.eye(10)[t_train.astype('int32').flatten()]

    return (x_train, x_test, t_train)

def tf_log(x):
    return tf.log(tf.clip_by_value(x, 1e-10, x))

###### 各レイヤーの定義 ########
class Conv:
    def __init__(self, filter_shape, function=lambda x: x, strides=[1,1,1,1], padding='VALID'):
        # filter_shape: (縦の次元数)x(横の次元数)x(入力チャンネル数)x(出力チャンネル数)
        fan_in = np.prod(filter_shape[:3])
        stddev = np.sqrt(2.0 / fan_in)
        initial = tf.truncated_normal(shape=filter_shape, stddev=stddev)
        self.W = tf.Variable(initial, name='W')
        self.b = tf.Variable(np.zeros((filter_shape[3]), dtype='float32'), name='b')
        self.function = function
        self.strides = strides
        self.padding = padding

    def __call__(self, x):
        u = tf.nn.conv2d(x, self.W, strides=self.strides, padding=self.padding) + self.b 
        return self.function(u) 
    
class Pooling:
    def __init__(self, ksize=[1,2,2,1], strides=[1,2,2,1], padding='VALID'):
        self.ksize = ksize
        self.strides = strides
        self.padding = padding
    
    def __call__(self, x):
        return  tf.nn.max_pool(x, ksize=self.ksize, strides=self.strides, padding=self.padding)
    
class Flatten:
    def __call__(self, x):
        return tf.reshape(x, (-1, np.prod(x.get_shape().as_list()[1:])))
    
class Dense:
    def __init__(self, in_dim, out_dim, function=lambda x: x):
        stddev = np.sqrt(2.0 / in_dim)
        initial = tf.truncated_normal(shape=(in_dim, out_dim), stddev=stddev)
        self.W = tf.Variable(initial, name='W')
        self.b = tf.Variable(np.zeros([out_dim]).astype('float32'))
        self.function = function

    def __call__(self, x):
        return self.function(tf.matmul(x, self.W) + self.b)

class Dropout:
    def __init__(self, dropout_keep_prob=1.0):
        self.dropout_keep_prob = dropout_keep_prob
        self.params = []
    
    def __call__(self, x):
        # 訓練時のみdropoutを適用
        return tf.cond(
            pred=is_training,
            true_fn=lambda: tf.nn.dropout(x, keep_prob=self.dropout_keep_prob),
            false_fn=lambda: x
        )

### モデルの構築 ###
def inference(x):
    # x: input_placefloder
    with tf.name_scope("inference") as scope:
        # 28x28x 1 -> 28x28x32
        h = Conv((3, 3, 1, 32), tf.nn.relu, padding='SAME')(x)
        # 28x28x32 -> 28x28x64
        h = Conv((3, 3, 32, 64), tf.nn.relu, padding='SAME')(h)
        #  28x28x64 ->  14x14x64
        h = Pooling((1, 2, 2, 1))(h)
        h = Dropout(0.3)(h)
        #  14x14x64 ->  14x14x128
        h = Conv((3, 3, 64, 128), tf.nn.relu, padding='SAME')(h)
        # 14x14x128 -> 14x14x256
        h = Conv((3, 3, 128, 256), tf.nn.relu, padding='SAME')(h)
        # 14x14x256 -> 7x7x256
        h = Pooling((1, 2, 2, 1))(h)
        h = Dropout(0.3)(h)
        h = Flatten()(h)
        # ここは次元計算する
        h = Dense(7*7*256, 1000, tf.nn.relu)(h)
        h = Dropout(0.5)(h)
        y = Dense(1000, 10, tf.nn.softmax)(h)
        return y

def calc_loss(y, t):
    # y: predicted_value, t: label_value
    with tf.name_scope("loss") as scope:
        cross_entropy = - tf.reduce_mean(tf.reduce_sum(t * tf_log(y), axis=1)) 
        return cross_entropy

def training(loss):
    # use Adam optimizer
    train = tf.train.AdamOptimizer(learning_rate=0.0009).minimize(loss)
    return train

# preparing
x_train, x_test, t_train = load_mnist()
x_train, x_valid, t_train, t_valid = train_test_split(x_train, t_train, test_size=10000)

# fitting
n_epochs = 60
batch_size = 100
n_batches = x_train.shape[0] // batch_size
tf.reset_default_graph()
with tf.Session() as sess:
    # write operation
    x = tf.placeholder(tf.float32, [None, 28, 28, 1])
    t = tf.placeholder(tf.float32, [None, 10])
    y = inference(x)
    loss = calc_loss(y, t)
    train = training(loss)

    init = tf.global_variables_initializer()
    sess.run(init)
    for epoch in range(n_epochs):
        x_train, t_train = shuffle(x_train, t_train, random_state=random_state)
        for batch in range(n_batches):
            start = batch * batch_size
            end = start + batch_size
            # train
            feed_dict={
                x: x_train[start:end],
                t: t_train[start:end],
                is_training: True
            }
            sess.run(train, feed_dict)

        # valid
        feed_dict={ x: x_valid, t: t_valid, is_training: False }
        y_pred, cost_valid = sess.run([y, loss], feed_dict)
        print('EPOCH: {}, Valid Cost: {:.3f}, Valid Accuracy: {:.3f}'.format(
            epoch,
            cost_valid,
            accuracy_score(t_valid.argmax(axis=1), y_pred.argmax(axis=1))
        ))
        
    # label保存
    feed_dict = { x: x_test, is_training: False }
    y_test_pred = sess.run(y, feed_dict)
    y_pred = y_test_pred.argmax(axis=1)
    submission = pd.Series(y_pred, name='label')
    submission.to_csv('./submission_pred.csv', header=True, index_label='id')
