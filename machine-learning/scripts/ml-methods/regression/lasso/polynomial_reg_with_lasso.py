# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from data.loaddata import *


def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def plot_fig(trainX, trainY, testX, testY, name):
    """Making figure."""
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(trainX, trainY, c="r")
    ax.plot(testX, testY)
    base = os.path.join(os.path.dirname(__file__), 'png')
    fig.savefig(base + "/{}.png".format(name))


def sk_pr_lasso(trainX, trainY):
    """Polynomial regression by sk LASSO."""

    degree = 10
    trainXsave = trainX
    trainX = PolynomialFeatures(degree=degree).fit_transform(trainX)
    lasso = linear_model.Lasso(alpha=0.1, max_iter=1000, tol=0.0, fit_intercept=True)
    lasso.fit(trainX, trainY)
    print("Coeff.:", lasso.coef_)
    print("Intercept:", lasso.intercept_)

    testX = np.linspace(min(trainXsave), max(trainXsave), 500).reshape(-1, 1)
    testXsave = testX
    testX = PolynomialFeatures(degree=degree).fit_transform(testX)
    testY = lasso.predict(testX)
    plot_fig(trainXsave, trainY, testXsave, testY, "sk_pr_lasso")


def my_pr_lasso(trainX, trainY):
    """Your own linear regression for multi variable."""
    header("My own linear regression for multi variable (in L1 regularization)")

    # scikit learnと同じ値を利用
    alpha = 0.1
    degree = 10
    epoch = 1000

    # 内部で変換考慮してないので
    trainXsave = trainX
    trainX = PolynomialFeatures(degree=degree).fit_transform(trainX)
    my_pr_with_lasso = MyPolynomialRegWithLasso(alpha=alpha, epoch=epoch)
    my_pr_with_lasso.fit(trainX, trainY)
    print("Coeff.:", my_pr_with_lasso.coef_)
    print("Intercept:", my_pr_with_lasso.intercept_)

    testX = np.linspace(min(trainXsave), max(trainXsave), 500).reshape(-1, 1)
    testXsave = testX
    testX = PolynomialFeatures(degree=degree).fit_transform(testX)
    testY = my_pr_with_lasso.predict(testX)
    plot_fig(trainXsave, trainY, testXsave, testY, "my_pr_with_lasso")

# ref: https://github.com/satopirka/Lasso
class MyPolynomialRegWithLasso:
    def __init__(self, alpha=0.001, epoch=100, fit_intercept=True):
        self.alpha = alpha
        self.epoch = epoch
        self.fit_intercept = fit_intercept
        self.coef_ = None
        self.intercept_ = None

    def _soft_threashold(self, y, lamda):
        return np.sign(y) * np.maximum(np.abs(y) - lamda, 0.0)

    def fit(self, data, target):
        if self.fit_intercept:
            # beta0用に１列目に１を追加 (data: (20, 12))
            data = np.column_stack((np.ones(len(data)), data))
        
        # betaの初期化 (beta: (12,))
        beta = np.zeros(data.shape[1])
        # 切片について正則化の影響を受けないので別で計算する
        num_data = data.shape[0]
        if self.fit_intercept:
            beta[0] = np.sum(target - np.dot(data[:, 1:], beta[1:])) / num_data

        # 更新処理
        for iteration in range(self.epoch):
            start = 1 if self.fit_intercept else 0
            for j in range(start, len(beta)):
                tmp_beta = beta.copy()
                # 更新対象の係数を0にする
                tmp_beta[j] = 0.0
                # r_j: 20,1
                r_j = target - data @ tmp_beta
                # 更新量の計算 
                arg1 = (data[:, j] @ r_j)
                arg2 = self.alpha * num_data
                # データ全てを使って更新しているので二乗和で割る
                beta[j] = self._soft_threashold(arg1, arg2) / (data[:, j]**2).sum()

                if self.fit_intercept:
                    beta[0] = np.sum(target - np.dot(data[:, 1:], beta[1:])) / num_data

        if self.fit_intercept:
            self.intercept_ = beta[0]
            self.coef_ = beta[1:]
        else:
            self.coef_ = beta

    def predict(self, data):
        return (data @ self.coef_) + self.intercept_


if __name__ == '__main__':
    trainX, trainY = loaddata("polynomial_reg.csv")
    # sklearn
    sk_pr_lasso(trainX, trainY)
    # original
    my_pr_lasso(trainX, trainY)

