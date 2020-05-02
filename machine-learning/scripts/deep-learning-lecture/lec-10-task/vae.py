import csv
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def load_mnist():
    # 学習データ
    x_train = np.load('./x_train.npy')
    # テストデータ
    x_test = np.load('./x_test.npy')

    x_train = (x_train.reshape(-1, 784) / 255).astype(np.float32)
    x_test = (x_test.reshape(-1, 784) / 255).astype(np.float32)

    return (x_train, x_test)


def tf_log(x):
    return tf.log(tf.clip_by_value(x, 1e-10, x))


#### Encoder ####
def encoder(x):
    with tf.variable_scope('Encoder', reuse=tf.AUTO_REUSE):
        h = tf.layers.Dense(units=256, activation=tf.nn.relu)(x)
        h = tf.layers.Dense(units=256, activation=tf.nn.relu)(h)
        h = tf.layers.Dense(units=512, activation=tf.nn.relu)(h)
        h = tf.layers.Dense(units=512, activation=tf.nn.relu)(h)
        # 潜在変数の次元
        mean = tf.layers.Dense(units=64)(h)
        var = tf.layers.Dense(units=64, activation=tf.nn.softplus)(h)

    return mean, var


def sampling_z(mean, var):
    epsilon = tf.random_normal(shape=tf.shape(mean))
    # 潜在変数zを連続な正規分布への変換する
    z = mean + tf.sqrt(var) * epsilon
    return z


#### Decoder ####
def decoder(z):
    with tf.variable_scope('Decoder', reuse=tf.AUTO_REUSE):
        h = tf.layers.Dense(units=256, activation=tf.nn.relu)(z)
        h = tf.layers.Dense(units=256, activation=tf.nn.relu)(h)
        h = tf.layers.Dense(units=512, activation=tf.nn.relu)(h)
        h = tf.layers.Dense(units=512, activation=tf.nn.relu)(h)
        y = tf.layers.Dense(units=784, activation=tf.nn.sigmoid)(h)

    return y


def lower_bound(x):
    # Encoder
    mean, var = encoder(x)
    # 潜在変数zの分布を正規分布(ガウス分布)に寄せるための項
    KL = -0.5 * tf.reduce_mean(tf.reduce_sum(1 + tf_log(var) - mean**2 - var, axis=1))
    # 潜在変数Z
    z = sampling_z(mean, var)
    # Decoder
    y = decoder(z)
    # cross entropyで出力と入力の誤差を算出
    reconstruction = tf.reduce_mean(tf.reduce_sum(x * tf_log(y) + (1 - x) * tf_log(1 - y), axis=1))

    lower_bound = [-KL, reconstruction]
    return lower_bound


#### Objective function #####
def calc_cost(lower_bound):
    cost = -tf.reduce_sum(lower_bound)
    return cost


#### Optimizer ####
def training(cost):
    optimizer = tf.train.AdamOptimizer()
    train = optimizer.minimize(cost)
    return train


### Output ####
def predict(x):
    # with tf.variable_scope('Predict'):
    mean, var = encoder(x)
    # ここはmeanでいいの...??
    y = decoder(mean)
    return y


#### Preprocessing #####
rng = np.random.RandomState(1234)
x_train, x_test = load_mnist()
x_train, x_valid = train_test_split(x_train, test_size=0.2)


# fitting
n_epochs = 10
batch_size = 100
n_batches = x_train.shape[0] // batch_size
tf.reset_default_graph()
with tf.Session() as sess:
    # define placeholder
    x = tf.placeholder(tf.float32, [None, 784])
    # write operation
    lower_bound = lower_bound(x)
    cost = calc_cost(lower_bound)
    valid = -cost
    train = training(cost)
    sampling = predict(x)

    init = tf.global_variables_initializer()
    sess.run(init)
    for epoch in range(n_epochs):
        rng.shuffle(x_train)
        lower_bound_all = []
        for batch in range(n_batches):
            start = batch * batch_size
            end = start + batch_size
            # train
            feed_dict={
                x: x_train[start:end]
            }
            _, lowerbound = sess.run([train, lower_bound], feed_dict)
            lower_bound_all.append(lowerbound)

        # valid
        feed_dict={ x: x_valid }
        lower_bound_valid = sess.run(valid, feed_dict)

        # print
        lower_bound_all = np.mean(lower_bound_all, axis=0)
        print('EPOCH:%d, Train Lower Bound:%lf, (%lf, %lf), Valid Lower Bound:%lf' %
            (epoch+1, np.sum(lower_bound_all), lower_bound_all[0], lower_bound_all[1], lower_bound_valid))

    feed_dict = { x: x_test }
    sample = sess.run(sampling, feed_dict)
    with open('./submission.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(sample.reshape(-1, 28*28).tolist())

