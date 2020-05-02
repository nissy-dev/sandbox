from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def softmax(x):
    x -= x.max(axis=1, keepdims=True)
    x_exp = np.exp(x)
    return x_exp / np.sum(x_exp, axis=1, keepdims=True)

# logの中身が0になるのを防ぐ
def np_log(x):
    return np.log(np.clip(a=x, a_min=1e-10, a_max=x))

# 学習データと検証データに分割
x_train, y_train, x_test = load_fashionmnist()
x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.2)

class SoftmaxRegression:
    def __init__(self, eps=0.001, optimizer=None):
        # weights
        self.eps = eps
        self.params = {}
        self.params['W'] = np.random.uniform(low=-0.08, high=0.08, size=(784, 10)).astype('float32')
        self.params['b'] = np.zeros(shape=(10,)).astype('float32')
        self.optimizer = optimizer
        
    def forward(self, x):
        return softmax(np.matmul(x, self.params['W']) + self.params['b'])

    def gradient(self, x, y, t, batch_size):
        grads = {}
        delta = y - t
        grads['W'] = np.matmul(x.T, delta) / batch_size 
        grads['b'] = np.matmul(np.ones(shape=(batch_size, )), delta) / batch_size
        return grads

    def update(self, params, grads):
        # update parameter
        if self.optimizer is None:
            for key in params.keys():
                self.params[key] -= self.eps * grads[key]
        else:
            self.optimizer.update(params, grads)
        
    def loss(self, y, t):
        return (- t * np_log(y)).sum(axis=1).mean()

    def train(self, x, t):
        batch_size = x.shape[0]
        # 順伝播
        y = self.forward(x)
        # 逆伝播
        grads = self.gradient(x, y, t, batch_size)
        self.update(self.params, grads)

    def valid(self, x, t):
        y = self.forward(x)
        loss = self.loss(y, t)
        return loss, y

class Adam:
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.99):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.m = None
        self.v = None
        self.t = 0
        
    def update(self, params, grads):
        if self.m is None:
            self.m = {}
            for key, val in params.items():
                self.m[key] = np.zeros_like(val)

        if self.v is None:
            self.v = {}
            for key, val in params.items():
                self.v[key] = np.zeros_like(val)

        self.t += 1
        for key in params.keys():
            self.m[key] = self.beta1 * self.m[key] + (1 - self.beta1) * grads[key]
            self.v[key] = self.beta2 * self.v[key] + (1 - self.beta2) * (grads[key] ** 2)
            mhat = self.m[key] / (1 - self.beta1 ** self.t)
            vhat = self.v[key] / (1 - self.beta2 ** self.t)
            params[key] -= self.lr * mhat / (np.sqrt(vhat) + 1e-8)

# hyper parameter
epoch = 500
batch_size = 1000
lr = 0.0001
optimizer = Adam(lr=lr)
softmax_regression = SoftmaxRegression(optimizer=optimizer)

# learning
train_size = x_train.shape[0]
iteration = int(train_size / batch_size)
for i in range(epoch):
    # オンライン学習
    rand_index = np.random.permutation(np.arange(train_size)).reshape(-1, batch_size)
    for j in range(iteration):
        softmax_regression.train(x_train[rand_index[j]], y_train[rand_index[j]])

# label保存
y_pred = softmax_regression.forward(x_test).argmax(axis=1)

submission = pd.Series(y_pred, name='label')
submission.to_csv('/root/userspace/chap03/submission_pred.csv', header=True, index_label='id')
