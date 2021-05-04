import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def load_cifar10():
    # 学習データ
    x_train = np.load('./data/x_train.npy')
    t_train = np.load('./data/t_train.npy')
    # テストデータ
    x_test = np.load('./data/x_test.npy')

    x_train = x_train.astype('float32') / 255
    x_test = x_test.astype('float32') / 255
    t_train = np.eye(10)[t_train.astype('int32').flatten()]
    return (x_train, x_test, t_train)

def tf_log(x):
    return tf.log(tf.clip_by_value(x, 1e-10, x))

### モデルの構築 ###
def inference(x, is_training):
    # x: input_placefloder
    # Conv1
    h = tf.layers.Conv2D(filters=32, kernel_size= [3, 3], padding='SAME')(x)
    h = tf.layers.BatchNormalization()(h, training=is_training)
    h = tf.nn.relu(h)
    h = tf.layers.Conv2D(filters=32, kernel_size= [3, 3], padding='SAME')(h)
    h = tf.layers.BatchNormalization()(h, training=is_training)
    h = tf.nn.relu(h)
    h = tf.layers.MaxPooling2D(pool_size=[2, 2], strides=2)(h)
    h = tf.layers.dropout(h, 0.25, training=is_training)
    # Conv2
    h = tf.layers.Conv2D(filters=64, kernel_size= [3, 3], padding='SAME')(h)
    h = tf.layers.BatchNormalization()(h, training=is_training)
    h = tf.nn.relu(h)
    h = tf.layers.Conv2D(filters=64, kernel_size= [3, 3], padding='SAME')(h)
    h = tf.layers.BatchNormalization()(h, training=is_training)
    h = tf.nn.relu(h)
    h = tf.layers.MaxPooling2D(pool_size=[2, 2], strides=2)(h)
    h = tf.layers.dropout(h, 0.25, training=is_training)
    # Conv3
    h = tf.layers.Conv2D(filters=128, kernel_size= [3, 3], padding='SAME')(h)
    h = tf.layers.BatchNormalization()(h, training=is_training)    
    h = tf.nn.relu(h)
    h = tf.layers.Conv2D(filters=128, kernel_size= [3, 3], padding='SAME')(h)
    h = tf.layers.BatchNormalization()(h, training=is_training)
    h = tf.nn.relu(h)
    h = tf.layers.MaxPooling2D(pool_size=[2, 2], strides=2)(h)
    h = tf.layers.dropout(h, 0.25, training=is_training)
    # FC
    h = tf.layers.Flatten()(h)
    h = tf.layers.Dense(units=1024, activation=tf.nn.relu)(h)
    h = tf.layers.dropout(h, 0.5, training=is_training)
    y = tf.layers.Dense(units=10, activation=tf.nn.softmax)(h)
    return y

def calc_loss(y, t):
    # y: predicted_value, t: label_value
    cross_entropy = - tf.reduce_mean(tf.reduce_sum(t * tf_log(y), axis=1)) 
    return cross_entropy

def training(loss):
    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    train_op = tf.train.AdamOptimizer().minimize(loss)
    train = tf.group([train_op, update_ops])
    return train

### 前処理 ###
def gcn(x):
    mean = np.mean(x, axis=(1, 2, 3), keepdims=True)
    std = np.std(x, axis=(1, 2, 3), keepdims=True)
    return (x - mean)/std

class ZCAWhitening:
    def __init__(self, epsilon=1e-4):
        self.epsilon = epsilon
        self.mean = None
        self.ZCA_matrix = None

    def fit(self, x):
        x = x.reshape(x.shape[0], -1)
        self.mean = np.mean(x, axis=0)
        x -= self.mean
        cov_matrix = np.dot(x.T, x) / x.shape[0]
        A, d, _ = np.linalg.svd(cov_matrix)
        self.ZCA_matrix = np.dot(np.dot(A, np.diag(1. / np.sqrt(d + self.epsilon))), A.T)

    def transform(self, x):
        shape = x.shape
        x = x.reshape(x.shape[0], -1)
        x -= self.mean
        x = np.dot(x, self.ZCA_matrix.T)
        return x.reshape(shape)
    
random_state = 42
rng = np.random.RandomState(1234)

#### data argumentaion #####
x_train, x_test, t_train = load_cifar10()
# horizontally flipping
x_train_hflip = x_train[:, :, ::-1, :]
x_train = np.append(x_train, x_train_hflip, axis=0)
t_train = np.append(t_train, t_train, axis=0)
# vertically flipping
x_train_vflip = x_train[:, ::-1, :, :]
x_train = np.append(x_train, x_train_vflip, axis=0)
t_train = np.append(t_train, t_train, axis=0)
# random cropping 
# 縦横にpaddingいれる
padded = np.pad(x_train, ((0, 0), (4, 4), (4, 4), (0, 0)), mode='constant')
crops = rng.randint(8, size=(len(x_train), 2))
# 0~8でランダムに平行移動...?
x_train_cropped = [padded[i, c[0]:(c[0]+32), c[1]:(c[1]+32), :] for i, c in enumerate(crops)]
x_train_cropped = np.array(x_train_cropped)
x_train = np.append(x_train, x_train_cropped, axis=0)
t_train = np.append(t_train, t_train, axis=0)

# split
x_train, x_valid, t_train, t_valid = train_test_split(x_train, t_train, test_size=10000, random_state=random_state)

# zca whitening & global contrast normalization
zca = ZCAWhitening()
zca.fit(x_train)
x_train_zca = zca.transform(gcn(x_train))
t_train_zca = t_train[:]
x_valid_zca = zca.transform(gcn(x_valid))
t_valid_zca = t_valid[:]
x_test_zca = zca.transform(gcn(x_test))

# fitting
loss_list_valid = []
n_epochs = 60
batch_size = 100
n_batches = x_train.shape[0] // batch_size
tf.reset_default_graph()
with tf.Session() as sess:
    # write operation
    x = tf.placeholder(tf.float32, [None, 32, 32, 3])
    t = tf.placeholder(tf.float32, [None, 10])
    is_training = tf.placeholder(tf.bool)
    y = inference(x, is_training)
    loss = calc_loss(y, t)
    train = training(loss)

    init = tf.global_variables_initializer()
    sess.run(init)
    for epoch in range(n_epochs):
        x_train, t_train = shuffle(x_train_zca, t_train_zca, random_state=random_state)
        for batch in range(n_batches):
            start = batch * batch_size
            end = start + batch_size
            # train
            feed_dict={
                x: x_train[start:end],
                t: t_train[start:end],
                is_training: True
            }
            sess.run([train], feed_dict)

        # valid
        feed_dict={ x: x_valid_zca, t: t_valid_zca, is_training: False }
        y_pred, cost_valid = sess.run([y, loss], feed_dict)
        loss_list_valid.append(cost_valid)
        print('EPOCH: {}, Valid Cost: {:.3f}, Valid Accuracy: {:.3f}'.format(
            epoch,
            cost_valid,
            accuracy_score(t_valid.argmax(axis=1), y_pred.argmax(axis=1))
        ))
        
    # label保存
    feed_dict = { x: x_test_zca, is_training: False }
    y_test_pred = sess.run(y, feed_dict)
    y_pred = y_test_pred.argmax(axis=1)
    submission = pd.Series(y_pred, name='label')
    submission.to_csv('./submission_pred.csv', header=True, index_label='id')
    