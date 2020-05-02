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


def sk_pr_ridge(trainX, trainY):
    """Polynomial regression by sk Ridge."""

    degree = 10
    alpha = 0.02
    trainXsave = trainX
    trainX = PolynomialFeatures(degree=degree).fit_transform(trainX)
    ridge = linear_model.Ridge(alpha=alpha, fit_intercept=True)
    ridge.fit(trainX, trainY)
    print("Coeff.:", ridge.coef_)
    print("Intercept:", ridge.intercept_)

    testX = np.linspace(min(trainXsave), max(trainXsave), 500).reshape(-1, 1)
    testXsave = testX
    testX = PolynomialFeatures(degree=degree).fit_transform(testX)
    testY = ridge.predict(testX)
    plot_fig(trainXsave, trainY, testXsave, testY, "sk_pr_ridge")


def my_pr_ridge(trainX, trainY):
    """Your own linear regression for multi variable."""
    header("My own linear regression for multi variable (in L2 regularization)")

    # scikit learnと同じ値を利用
    degree = 10
    alpha = 0.02
    trainXsave = trainX
    trainX = PolynomialFeatures(degree=degree).fit_transform(trainX)
    my_pr_with_ridge = MyPolynomialRegWithRidge(alpha=alpha)
    my_pr_with_ridge.fit(trainX, trainY)
    print("Coeff.:", my_pr_with_ridge.coef_)
    print("Intercept:", my_pr_with_ridge.intercept_)

    testX = np.linspace(min(trainXsave), max(trainXsave), 500).reshape(-1, 1)
    testXsave = testX
    testX = PolynomialFeatures(degree=degree).fit_transform(testX)
    testY = my_pr_with_ridge.predict(testX)
    plot_fig(trainXsave, trainY, testXsave, testY, "my_pr_with_ridge")


class MyPolynomialRegWithRidge:
    def __init__(self, alpha=0.01, fit_intercept=True):
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.coef_ = None
        self.intercept_ = None

    def fit(self, data, target):
        # 解析解が存在する
        w = np.dot(np.linalg.inv(np.dot(data.T, data) + self.alpha * np.eye(data.shape[1])),
            np.dot(data.T, target))

        if self.fit_intercept:
            self.intercept_ = w[0]
            self.coef_ = np.insert(w[1:], 0, 0)
        else:
            self.coef_ = w

    def predict(self, data):
        return (data @ self.coef_) + self.intercept_


if __name__ == '__main__':
    trainX, trainY = loaddata("polynomial_reg.csv")
    # sklearn
    sk_pr_ridge(trainX, trainY)
    # original
    my_pr_ridge(trainX, trainY)

