from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def softmax(x):
    x -= x.max(axis=1, keepdims=True)
    x_exp = np.exp(x)
    return x_exp / np.sum(x_exp, axis=1, keepdims=True)

# softmaxの微分
def deriv_softmax(x):
    return softmax(x) * (1 - softmax(x))

def relu(x):
    return np.maximum(x, 0)

# reluの微分
def deriv_relu(x):
    return (x > 0).astype(x.dtype)

# logの中身が0になるのを防ぐ
def np_log(x):
    return np.log(np.clip(a=x, a_min=1e-10, a_max=x))

# 全結合ニューラルネットワーク
class Dense:
    def __init__(self, in_dim, out_dim, function, deriv_function):
        self.params = {}
        # use He
        self.params['W'] = (np.sqrt(2.0 / in_dim) * np.random.randn(in_dim, out_dim)).astype('float64')
        self.params['b'] = np.zeros(out_dim).astype('float64')
        self.function = function # forward function
        self.deriv_function = deriv_function # backward function

        # saving this layer value
        self.grads = {}
        self.u = None # (batch_size, out_dim)
        self.delta = None # (batch_size, out_dim)
        # saving prev layer value
        self.h_prev = None # (batch_size, in_dim)
        
    def forward(self, h_prev):
        # h_prev: 前の層のforwardの値
        self.h_prev = h_prev
        self.u = np.matmul(self.h_prev, self.params['W']) + self.params['b']
        return self.function(self.u)

    def backward(self, delta, W):
        # delta: (順伝播方向から見て)後の層のdelta (size: (batch_size, ?))
        # W: (順伝播方向から見て)後の層のW (size: (out_dim, ?))
        self.delta = self.deriv_function(self.u) * np.matmul(delta, W.T)
        return self.delta

    def gradient(self):
        batch_size = self.delta.shape[0]
        # (in_dim, batch_size) × (batch_size, out_dim) = (in_dim, out_dim)
        self.grads['W'] =  np.matmul(self.h_prev.T, self.delta) / batch_size
        # (1, batch_size) × (batch_size, out_dim) = (1, out_dim)
        self.grads['b'] =  np.matmul(np.ones(batch_size), self.delta) / batch_size
        return self.grads

class MultilayerPerceptron:
    def __init__(self, layers, lr=0.001, optimizer=None):
        self.layers = layers
        self.optimizer = optimizer
        self.lr = lr

    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x
        
    def backward(self, delta):
        W = None
        for i, layer in enumerate(self.layers[::-1]):
            if i == 0: # 出力層
                layer.delta = delta
                layer.gradient()
            else: # 出力層以外
                delta = layer.backward(delta, W) # backward
                layer.gradient()

            W = layer.params['W']

    def update(self):
        for i, layer in enumerate(self.layers):
            if self.optimizer is None:
                layer.params['W'] -= self.lr * layer.grads['W']
                layer.params['b'] -= self.lr * layer.grads['b']
            else:
                self.optimizer.update(layer.params, layer.grads, i)

    def loss(self, y, t):
        return (- t * np_log(y)).sum(axis=1).mean()

    def train(self, x, t):
        y = self.forward(x)
        delta = y - t
        self.backward(delta)
        # update params
        self.update()

    def valid(self, x, t):
        y = self.forward(x)
        loss = self.loss(y, t)
        return loss, y

class MSGD:
    def __init__(self, lr=0.01, momentum=0.9):
        self.lr = lr
        self.momentum = momentum
        self.w = {}
        
    def update(self, params, grads, layer_number):
        for key, val in params.items():
            w_key = key + str(layer_number)
            if not (w_key in self.w):
                self.w[w_key] = np.zeros_like(val)

            self.w[w_key] = - self.lr * grads[key] + self.momentum * self.w[w_key]
            params[key] += self.w[w_key]

# 学習データと検証データに分割
x_train, y_train, x_test = load_fashionmnist()
x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.2)

# hyper parameter
epoch = 20
batch_size = 300
optimizer = MSGD(lr=0.008)
layers = [
    Dense(784, 2000, relu, deriv_relu),
    Dense(2000, 1000, relu, deriv_relu),
    Dense(1000, 500, relu, deriv_relu),
    Dense(500, 10, softmax, deriv_softmax)
]
mlp = MultilayerPerceptron(layers=layers, optimizer=optimizer)

# learning
train_size = x_train.shape[0]
iteration = int(train_size / batch_size)
for i in range(epoch):
    rand_index = np.random.permutation(np.arange(train_size)).reshape(-1, batch_size)
    for j in range(iteration):
        mlp.train(x_train[rand_index[j]], y_train[rand_index[j]])

# label保存
y_pred = mlp.forward(x_test).argmax(axis=1)
submission = pd.Series(y_pred, name='label')
submission.to_csv('/root/userspace/chap04/sample_submission_pred.csv', header=True, index_label='id')
