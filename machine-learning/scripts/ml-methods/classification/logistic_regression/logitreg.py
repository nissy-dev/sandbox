# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from matplotlib import pyplot as plt
from math import ceil

from sklearn.linear_model import LogisticRegression
from data.loaddata import *


def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def plot_fig(trainX, vec, intercept, name):
    """Making figure with plots and projection surface."""
    trainX_0, trainX_1 = trainX[:50], trainX[50:]

    grad = vec[1] / vec[0]
    x = np.array([-0.3, 0.3])
    y = x * grad + intercept

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(trainX_0[:, 0], trainX_0[:, 1], c="blue")
    ax.scatter(trainX_1[:, 0], trainX_1[:, 1], c="red")
    ax.plot(x, y, c="black", linestyle="dashed")
    ax.set_ylim([-3.0, 2.0])
    base = os.path.join(os.path.dirname(__file__), 'png')
    fig.savefig(base + "/{}.png".format(name))


def calcref(trainX, trainY):
    """Calclating reference by sklearn logistic regression."""
    header("sklearn logistic regression")

    lr = LogisticRegression(fit_intercept=True)
    lr.fit(trainX, trainY)
    result = lr.predict(trainX)
    poss = lr.predict_proba(trainX)

    print("Coefficient:")
    print(lr.coef_)
    print("intercept_")
    print(lr.intercept_)
    print("Decision")
    print(result)
    print("Possibility")
    print(poss[0])
    plot_fig(trainX, lr.coef_[0], lr.intercept_[0], "sklearn_logit_reg")


def my_logit_reg(trainX, trainY):
    """Calculating original logistic regression."""
    header("Original logistic regression")

    # 勾配降下法
    gd_lr = MyLogisticRegression(eta=0.0001, epoch=30000)
    gd_lr.fit_gd(trainX, trainY)
    coeff, intercept = gd_lr.result()
    probability = gd_lr.probability(trainX)

    # ミニバッチ確率的勾配降下法
    msgd_lr = MyLogisticRegression(epoch=30000, batch_size=50)
    msgd_lr.fit_msgd(trainX, trainY)
    c, i = msgd_lr.result()
    p = msgd_lr.probability(trainX)

    print("\nGD")
    print("================================================")
    print("Coefficient:")
    print(coeff)
    print("intercept_")
    print(intercept)
    print("Probability")
    print(probability[0])
    plot_fig(trainX, coeff, intercept, "gd_reg")
    print("\nMSGD")
    print("================================================")
    print("Coefficient:")
    print(c)
    print("intercept_")
    print(i)
    print("Probability")
    print(p[0])
    plot_fig(trainX, c, i, "msgd_reg")


class MyLogisticRegression:
    def __init__ (self, eta=0.01, epoch=10000, batch_size=0):
        self.eta = eta                  # learning_rate
        self.epoch = epoch              # epoch
        self.batch_size = batch_size    # batch_size
        self.w_list = []                # weight list
        self.loss_list = []             # loss function list

    def __shuffle(self, x, t):
        index = np.random.permutation(len(x))
        return x[index], t[index]

    def __predict(self, x, W):
        return 1 / (1 + np.exp(- np.dot(x, W)))

    def __loss(self, activate, t):
        t_reshape = t[:, np.newaxis]
        return - np.sum(t_reshape * np.log(activate) + (1 - t_reshape) * np.log(1 - activate))

    def __gradient(self, x, t, activate):
        return - np.dot(x.T, (t[:, np.newaxis] - activate))

    # x:input t:label
    def fit_gd(self, x, t):
        x = np.insert(x, 0, 1, axis=1)   # バイアス用に全ての行に１を加える
        W = np.ones((3, 1))              # 重みの初期値
        self.w_list = []
        self.loss_list = []
        self.w_list.append(W)

        # 勾配法で学習(全データを毎回計算)
        for i in range(self.epoch):
            activate = self.__predict(x, W)
            loss = self.__loss(activate, t)
            W -= self.eta * self.__gradient(x, t, activate)
            self.w_list.append(W)
            self.loss_list.append(loss)

    def fit_msgd(self, x, t):
        x = np.insert(x, 0, 1, axis=1)   # バイアス用に全ての行に１を加える
        W = np.ones((3, 1))              # 重みの初期値
        self.w_list = []
        self.loss_list = []
        self.w_list.append(W)

        # ミニバッチ確率的勾配降下法で学習(ランダムで取り出したデータを毎回計算)
        # epoch回数をデータ数で割ってloop回数を算出
        for i in range(ceil(self.epoch / t.shape[0])):
            # データをシャッフル
            randx, randt = self.__shuffle(x, t)

            for j in range(ceil(x.shape[0] / self.batch_size)):
                # batchごとに, シャッフルのされたリストからデータをとりだす
                tmp_x, tmp_t = randx[j*self.batch_size:(j+1)*self.batch_size - 1], \
                                randt[j*self.batch_size:(j+1)*self.batch_size - 1]
                activate = self.__predict(tmp_x, W)
                loss = self.__loss(activate, tmp_t)
                W -= self.eta * self.__gradient(tmp_x, tmp_t, activate)
                self.w_list.append(W)
                self.loss_list.append(loss)

    # return coeff, intercept
    def result(self):
        w = self.w_list[-1].T[0]
        return w[1:3], w[0]

    # calculate probability
    def probability(self, x):
        x = np.insert(x, 0, 1, axis=1)
        p = self.__predict(x, self.w_list[-1]) # label:1となる確率
        return np.concatenate([1-p, p], axis=1)

if __name__ == '__main__':
    trainX, trainY = loaddata()
    # scikit-learn
    calcref(trainX, trainY)
    # original
    my_logit_reg(trainX, trainY)
