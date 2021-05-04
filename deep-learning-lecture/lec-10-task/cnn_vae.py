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
def encoder(x, is_training):
    with tf.variable_scope('Encoder', reuse=tf.AUTO_REUSE):
        # convolution
        h = tf.keras.layers.Reshape((28, 28, 1))(x)
        # 28, 28, 32
        h = tf.layers.Conv2D(filters=32, kernel_size=3)(h)
        h = tf.layers.BatchNormalization()(h)
        h = tf.nn.leaky_relu(h)
        # 14, 14, 64
        h = tf.layers.Conv2D(filters=64, kernel_size=3, strides=2)(h)
        h = tf.layers.BatchNormalization()(h)
        h = tf.nn.leaky_relu(h)
        # 14, 14, 128
        h = tf.layers.Conv2D(filters=128, kernel_size=3)(h)
        h = tf.layers.BatchNormalization()(h)
        h = tf.nn.leaky_relu(h)
        # 7, 7, 256
        h = tf.layers.Conv2D(filters=256, kernel_size=3, strides=2)(h)
        h = tf.layers.BatchNormalization()(h)
        h = tf.nn.leaky_relu(h)
        # 潜在変数の次元に落とし込む
        h = tf.layers.Flatten()(h)
        h = tf.layers.Dense(units=1024, activation=tf.nn.relu)(h)
        mean = tf.layers.Dense(units=64)(h)
        var = tf.layers.Dense(units=64, activation=tf.nn.softplus)(h)

    return mean, var


def sampling_z(mean, var):
    epsilon = tf.random_normal(shape=tf.shape(mean))
    # 潜在変数zを連続な正規分布への変換する
    z = mean + tf.sqrt(var) * epsilon
    return z


#### Decoder ####
def decoder(z, is_training):
    with tf.variable_scope('Decoder', reuse=tf.AUTO_REUSE):
        # 次元を戻す
        h = tf.layers.Dense(units=7*7*256, activation=tf.nn.relu)(z)
        h = tf.keras.layers.Reshape((7, 7, 256))(h)
        # 14, 14, 128
        h = tf.layers.Conv2DTranspose(filters=128, kernel_size=3, strides=2, padding='SAME')(h)
        h = tf.layers.BatchNormalization()(h)
        h = tf.nn.leaky_relu(h)
        # 14, 14, 64
        h = tf.layers.Conv2DTranspose(filters=64, kernel_size=3, padding='SAME')(h)
        h = tf.layers.BatchNormalization()(h)
        h = tf.nn.leaky_relu(h)
        # 28, 28, 32
        h = tf.layers.Conv2DTranspose(filters=32, kernel_size=3,  strides=2, padding='SAME')(h)
        h = tf.layers.BatchNormalization()(h)
        h = tf.nn.leaky_relu(h)
        # 28, 28, 1
        h = tf.layers.Conv2DTranspose(filters=1, kernel_size=3, padding='SAME')(h)
        h = tf.nn.sigmoid(h)
        y = tf.keras.layers.Reshape((28*28*1,))(h)

    return y


def lower_bound(x, is_training):
    # Encoder
    mean, var = encoder(x, is_training)
    # 潜在変数zの分布を正規分布(ガウス分布)に寄せるための項
    KL = -0.5 * tf.reduce_mean(tf.reduce_sum(1 + tf_log(var) - mean**2 - var, axis=1))
    # 潜在変数Z
    z = sampling_z(mean, var)
    # Decoder
    y = decoder(z, is_training)
    # cross entropyで出力と入力の誤差を算出
    reconstruction = tf.reduce_mean(tf.reduce_sum(x * tf_log(y) + (1 - x) * tf_log(1 - y), axis=1))

    lower_bound = [-KL, reconstruction]
    return lower_bound


#### Objective function #####
def calc_cost(lower_bound):
    cost = -tf.reduce_sum(lower_bound)
    return cost


def calc_score(lower_bound):
    cost = lower_bound[1]
    return cost


#### Optimizer ####
def training(cost, learning_rate):
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train = optimizer.minimize(cost)
    return train


### Output ####
def predict(x, is_training):
    # with tf.variable_scope('Predict'):
    mean, var = encoder(x, is_training)
    # ここはmeanでいいの...??
    z = sampling_z(mean, var)
    y = decoder(z, is_training)
    return y


### Preprocessing ###
rng = np.random.RandomState(1234)
x_train, x_test = load_mnist()
x_train, x_valid = train_test_split(x_train, test_size=0.05)


# fitting
n_epochs = 15
batch_size = 100
n_batches = x_train.shape[0] // batch_size
n_batches_valid = x_valid.shape[0] // batch_size
tf.reset_default_graph()
with tf.Session() as sess:
    # define placeholder
    x = tf.placeholder(tf.float32, [None, 28*28*1])
    is_training = tf.placeholder(tf.bool)
    learning_rate = tf.placeholder(tf.float32)
    # write operation
    lower_bound = lower_bound(x, is_training)
    cost = calc_cost(lower_bound)
    valid = -cost
    train = training(cost, learning_rate)
    score = calc_score(lower_bound)
    sampling = predict(x, is_training)
    saver = tf.train.Saver()

    init = tf.global_variables_initializer()
    sess.run(init)
#     saver.restore(sess, "model.ckpt")
    for epoch in range(n_epochs):
        rng.shuffle(x_train)
        lower_bound_all = []
        for batch in range(n_batches):
            start = batch * batch_size
            end = start + batch_size
            # train
            feed_dict={
                x: x_train[start:end],
                learning_rate: 0.001 if epoch < 10 else 0.001 / 5
            }
            _, lowerbound = sess.run([train, lower_bound], feed_dict)
            lower_bound_all.append(lowerbound)

        # valid
        lower_bound_valid = []
        for batch in range(n_batches_valid):
            start = batch * batch_size
            end = start + batch_size
            # train
            feed_dict={ x: x_valid[start:end] }
            lower_bound_valid_tmp = sess.run(valid, feed_dict)
            lower_bound_valid.append(lower_bound_valid_tmp)

        # print
        lower_bound_all = np.mean(lower_bound_all, axis=0)
        lower_bound_valid = np.mean(lower_bound_valid, axis=0)
        print('EPOCH:%d, Train Lower Bound:%lf, (%lf, %lf), Valid Lower Bound:%lf' %
            (epoch+1, np.sum(lower_bound_all), lower_bound_all[0], lower_bound_all[1], lower_bound_valid))
        
#     saver.save(sess, "model.ckpt")
    feed_dict = { x: x_test, is_training: False }
    sample = sess.run(sampling, feed_dict)
    test_score = sess.run(score, feed_dict)
    print(test_score)
    with open('./submission.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(sample.reshape(-1, 28*28).tolist())
