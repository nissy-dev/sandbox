import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from tensorflow.keras.preprocessing.sequence import pad_sequences

def load_dataset():
    # save np.load
    np_load_old = np.load
    # modify the default parameters of np.load (work around)
    np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)
    # 学習データ
    x_train = np.load('./x_train.npy')
    t_train = np.load('./t_train.npy')
    # テストデータ
    x_test = np.load('./x_test.npy')
    # restore the np.load
    np.load = np_load_old
    return (x_train, x_test, t_train)


def tf_log(x):
    return tf.log(tf.clip_by_value(x, 1e-10, x))


### Embedding ###
class Embedding:
    def __init__(self, vocab_size, emb_dim, scale=0.08):
        # 各単語IDに対する特徴量ベクトルを作成
        self.V = tf.Variable(tf.random_normal([vocab_size, emb_dim], stddev=scale), name='V')

    def __call__(self, x):
        # self.Vからレビューに対応するデータを取り出す
        return tf.nn.embedding_lookup(self.V, x)


### RNN ####
class RNN:
    def __init__(self, hid_dim, seq_len = None, initial_state = None):
        self.cell = tf.nn.rnn_cell.BasicRNNCell(hid_dim)
        self.initial_state = initial_state
        self.seq_len = seq_len

    def __call__(self, x):
        if self.initial_state is None:
            self.initial_state = self.cell.zero_state(tf.shape(x)[0], tf.float32)

        # outputsは各系列長分以降は0になるので注意
        outputs, state = tf.nn.dynamic_rnn(self.cell, x, self.seq_len, self.initial_state)
        return tf.gather_nd(outputs, tf.stack([tf.range(tf.shape(x)[0]), self.seq_len-1], axis=1))


### LSTM ####
class LSTM:
    def __init__(self, hid_dim, seq_len=None, initial_state=None, is_training=None, _keep_prob=1.0):
        self.cell = tf.nn.rnn_cell.BasicLSTMCell(hid_dim)
        self.initial_state = initial_state
        self.seq_len = seq_len
        self.is_training = is_training
        self._keep_prob = _keep_prob

    def __call__(self, x):
        if self.initial_state is None:
            self.initial_state = self.cell.zero_state(tf.shape(x)[0], tf.float32)

        # dropout
        keep_prob = tf.cond(self.is_training, lambda:tf.constant(self._keep_prob), lambda:tf.constant(1.0))
        self.cell = tf.contrib.rnn.DropoutWrapper(self.cell, input_keep_prob=keep_prob)

        outputs, state = tf.nn.dynamic_rnn(self.cell, x, self.seq_len, self.initial_state)
        return tf.gather_nd(outputs, tf.stack([tf.range(tf.shape(x)[0]), self.seq_len-1], axis=1))


### モデルの構築 ###
def inference(x, hid_dim, emb_dim, pad_index, num_words, is_training):
    """build model

    Parameters
    ----------
    x : 学習データ (データ数×レビュー長さ(データによって異なる))
    hid_dim : 隠れ層の数
    emb_dim : 単語の特徴量ベクトルの次元
    pad_index : 0 = レビューの長さをを全て同じにする
    num_words : 単語IDの最大値
    """
    # 各データのレビュー長さの計算
    seq_len = tf.reduce_sum(tf.cast(tf.not_equal(x, pad_index), tf.int32), axis=1)
    h = Embedding(num_words, emb_dim)(x)
    # dropout
    h = tf.layers.dropout(h, 0.4, training=is_training)
    # 内部でdropoutする
    h = LSTM(
        hid_dim=hid_dim, 
        seq_len=seq_len, 
        is_training=is_training,
        _keep_prob=0.6,
    )(h)
    y = tf.layers.Dense(1, tf.nn.sigmoid)(h)
    return y

def calc_loss(y, t):
    """caluculate loss value

    Parameters
    ----------
    y: predicted_value
    t: label_value
    """
    cost = -tf.reduce_mean(t * tf_log(y) + (1 - t) * tf_log(1 - y))
    return cost


def training(loss):
    # use Gradient Clipping
    optimizer = tf.train.AdamOptimizer(learning_rate=0.0004)
    grads = optimizer.compute_gradients(cost)
    clipped_grads = [(tf.clip_by_value(grad_val, -1., 1.), var) for grad_val, var in grads]
    train = optimizer.apply_gradients(clipped_grads)
    return train

# data
x_train, x_test, t_train = load_dataset()
x_train, x_valid, t_train, t_valid = train_test_split(x_train, t_train, test_size=0.2, random_state=42)

# データ(レビュー)の長さでソート (長い順)
x_train_lens = [len(com) for com in x_train]
sorted_train_indexes = sorted(range(len(x_train_lens)), key=lambda x: -x_train_lens[x])
x_train = [x_train[ind] for ind in sorted_train_indexes]
t_train = [t_train[ind] for ind in sorted_train_indexes]

# fitting
n_epochs = 15
batch_size = 100
n_batches_train = len(x_train) // batch_size
n_batches_valid = len(x_valid) // batch_size
n_batches_test = len(x_test) // batch_size
tf.reset_default_graph()
with tf.Session() as sess:
    # data placeholder
    x = tf.placeholder(tf.int32, [None, None], name='x')
    t = tf.placeholder(tf.float32, [None, None], name='t')
    is_training = tf.placeholder(tf.bool)
    # parameter
    pad_index = 0 ## ほぼ固定
    emb_dim = 100
    hid_dim = 128
    num_words = max([max(s) for s in np.hstack((x_train, x_valid, x_test))])
    # write operation
    y = inference(x, hid_dim, emb_dim, pad_index, num_words, is_training)
    cost = calc_loss(y, t)
    train = training(cost)
    test = tf.round(y)

    init = tf.global_variables_initializer()
    sess.run(init)
    for epoch in range(n_epochs):
        # Train
        train_costs = []
        for i in range(n_batches_train):
            start = i * batch_size
            end = start + batch_size
            x_train_batch = np.array(pad_sequences(x_train[start:end], padding='post', value=pad_index))
            t_train_batch = np.array(t_train[start:end])[:, None]
            feed_dict = {
                x: x_train_batch, 
                t: t_train_batch,
                is_training: True
            }
            _, train_cost = sess.run([train, cost], feed_dict)
            train_costs.append(train_cost)
        
        # Valid
        valid_costs = []
        y_pred = []
        for i in range(n_batches_valid):
            start = i * batch_size
            end = start + batch_size
            x_valid_pad = np.array(pad_sequences(x_valid[start:end], padding='post', value=pad_index))
            t_valid_pad = np.array(t_valid[start:end])[:, None]
            feed_dict = {
                x: x_valid_pad, 
                t: t_valid_pad,
                is_training: False
            }
            pred, valid_cost = sess.run([test, cost], feed_dict)
            y_pred += pred.flatten().tolist()
            valid_costs.append(valid_cost)
        print('EPOCH: %i, Training Cost: %.3f, Validation Cost: %.3f, Validation F1: %.3f' % (epoch+1, np.mean(train_costs), np.mean(valid_costs), f1_score(t_valid, y_pred, average='macro')))

    # label保存
    y_test_pred = []
    for i in range(n_batches_test):
        start = i * batch_size
        end = start + batch_size
        x_test_pad = np.array(pad_sequences(x_test[start:end], padding='post', value=pad_index))
        feed_dict = { x: x_test_pad, is_training: False }
        pred = sess.run(test, feed_dict)
        y_test_pred += pred.flatten().tolist()
    submission = pd.Series(y_test_pred, name='label')
    submission.to_csv('./submission_pred.csv', header=True, index_label='id')
