from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# NaNを返すのを防ぐ
def tf_log(x):
    return tf.log(tf.clip_by_value(x, 1e-10, x))

class Dense:
    def __init__(self, in_dim, out_dim, function=lambda x: x):
        # use He
        stddev = tf.sqrt(2.0 / in_dim)
        self.W = tf.Variable(tf.truncated_normal(shape=(in_dim, out_dim), stddev=stddev))
        self.b = tf.Variable(tf.zeros(out_dim))
        self.params = [self.W, self.b]
        self.function = function

    def __call__(self, h_prev):
        # h_prev: 前の層のforwardの値
        self.h_prev = h_prev
        return self.function(tf.matmul(self.h_prev, self.W) + self.b)

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

class MultilayerPerceptron:
    def __init__(self, layers, lr=0.001, optimizer=None):
        self.layers = layers
        self.optimizer = optimizer
        self.lr = lr

    def inference(self, input_placeholder):
        """
        Builds the model as far as required for running the network
        forward to make predictions
        """
        x = input_placeholder
        for layer in layers:
            x = layer(x)
        return x
    
    def calc_loss(self, predicted_value, label_placeholder):
        """
        Adds to the inference model the layers required to generate loss
        """
        cross_entropy = - tf.reduce_mean(tf.reduce_sum(label_placeholder * tf_log(predicted_value), axis=1)) 
        return cross_entropy
    
    def train(self,  input_placeholder, label_placeholder):
        # forward 
        y = self.inference(input_placeholder)
        loss = self.calc_loss(y, label_placeholder)
        params_list = []
        for layer in self.layers:
            params_list.extend(layer.params)
        
        # backward
        grads = tf.gradients(loss, params_list)
        if self.optimizer is None:
            updates = []
            for param, grad in zip(params_list, grads):
                updates.append(param.assign_sub(self.lr * grad))
        else:
            updates = self.optimizer.update(params_list, grads)

        return updates

    def valid(self, input_placeholder, label_placeholder):
        y = self.inference(input_placeholder)
        loss = self.calc_loss(y, label_placeholder)
        return y, loss

class Adam:
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.99):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.t = 0
        
    def update(self, params, grads):
        updates = []
        self.t += 1
        for param, grad in zip(params, grads):
            m = tf.Variable(tf.zeros_like(param, dtype=tf.float32), name='m')
            v = tf.Variable(tf.zeros_like(param, dtype=tf.float32), name='v')
            updates.append(m.assign(self.beta1 * m + (1 - self.beta1) * grad))
            updates.append(v.assign(self.beta2 * v + (1 - self.beta2) * grad**2))
            with tf.control_dependencies(updates):
                mhat = m / (1 - self.beta1 ** self.t)
                vhat = v / (1 - self.beta2 ** self.t)
                updates.append(param.assign_sub(self.lr * mhat / (tf.sqrt(vhat) + 1e-8)))

        return updates

# preparing
x_train, y_train, x_test = load_fashionmnist()
x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=10000)

# fitting
epoch = 25
batch_size = 100
train_size = x_train.shape[0]
iteration = int(train_size / batch_size)
tf.reset_default_graph()
with tf.Session() as sess:
    # valiables
    input_placeholder = tf.placeholder(tf.float32, (None, 784))
    label_placeholder = tf.placeholder(tf.float32, (None, 10))
    is_training = tf.placeholder(tf.bool)
    dropout_keep_prob = 0.5
    layers = [
        Dense(784, 2000, tf.nn.relu),
        Dropout(dropout_keep_prob),
        Dense(2000, 1000, tf.nn.relu),
        Dropout(dropout_keep_prob),
        Dense(1000, 500, tf.nn.relu),
        Dropout(dropout_keep_prob),
        Dense(500, 10, tf.nn.softmax)
    ]
    # prepare operation
    optimizer = Adam(lr=0.00009)
    model = MultilayerPerceptron(layers=layers, optimizer=optimizer)
    updates = model.train(input_placeholder, label_placeholder)
    valid = model.valid(input_placeholder, label_placeholder)
    predict = model.inference(input_placeholder)
    train = tf.group(*updates)

    # execute operation 
    sess.run(tf.global_variables_initializer())
    for i in range(epoch):
        rand_index = np.random.permutation(np.arange(train_size)).reshape(-1, batch_size)
        for j in range(iteration):
            feed_dict = {
                input_placeholder: x_train[rand_index[j]],
                label_placeholder: y_train[rand_index[j]],
                is_training: True,
            }
            # train
            sess.run(train, feed_dict)

        # valid
        feed_dict = { 
            input_placeholder: x_valid,
            label_placeholder: y_valid,
            is_training: False
        }
        y_pred, cost_valid_ = sess.run(valid, feed_dict)
        print('EPOCH: {}, Valid Cost: {:.3f}, Valid Accuracy: {:.3f}'.format(
            i + 1,
            cost_valid_,
            accuracy_score(y_valid.argmax(axis=1), y_pred.argmax(axis=1))
        ))
    
    # label保存
    feed_dict = { input_placeholder: x_test, is_training: False }
    y_test_pred = sess.run(predict, feed_dict)
    y_pred = y_test_pred.argmax(axis=1)
    submission = pd.Series(y_pred, name='label')
