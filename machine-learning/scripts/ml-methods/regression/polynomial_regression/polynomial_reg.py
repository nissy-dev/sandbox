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


def sk_polynomial_reg(trainX, trainY):
    """Polynomial regression by sk classical linear regression."""
    header("sklearn Poly-classical-linear")

    degree = 10
    trainXsave = trainX
    trainX = PolynomialFeatures(degree=degree).fit_transform(trainX)
    lr = linear_model.LinearRegression(fit_intercept=True)
    lr.fit(trainX, trainY)

    print("Coeff.:", lr.coef_)
    print("Intercept:", lr.intercept_)

    testX = np.linspace(min(trainXsave), max(trainXsave), 500).reshape(-1, 1)
    testXsave = testX
    testX = PolynomialFeatures(degree=degree).fit_transform(testX)
    testY = lr.predict(testX)
    plot_fig(trainXsave, trainY, testXsave, testY, "sk_polynomial_reg")


def my_polynomial_reg(trainX, trainY):
    """Your own linear regression for multi variable."""
    header("My own linear regression for multi variable")

    degree = 10
    # なんで変換しなくてもいいのか...? => 内部でやっているから
    my_pr = PolynomialRegression(degree=degree)
    my_pr.fit(trainX, trainY)
    print("Coeff.:", my_pr.coef_)
    print("Intercept:", my_pr.intercept_)

    testX = np.linspace(min(trainX), max(trainX), 500).reshape(-1, 1)
    testXsave = testX
    testX = PolynomialFeatures(degree=degree).fit_transform(testX)
    testY = my_pr.predict(testX)
    plot_fig(trainX, trainY, testXsave, testY, "my_polynomial_reg")


class PolynomialRegression:
    def __init__(self, degree=1):
        self.degree = degree
        self.coef_ = None
        self.intercept_ = None

    def _create_phi(self, data):
        phi = lambda x: [x ** i for i in range(self.degree + 1)]
        return np.array([phi(i) for i in data]).reshape(len(data), -1)

    def fit(self, data, target):
        phi_arr = self._create_phi(data)
        w = np.dot(np.linalg.inv(phi_arr.T @ phi_arr), (phi_arr.T @ target))
        # 先頭に0を追加
        self.coef_ = np.insert(w[1:], 0, 0)
        self.intercept_ = w[0]

    def predict(self, data):
        return (data @ self.coef_) + self.intercept_


if __name__ == '__main__':
    trainX, trainY = loaddata("polynomial_reg.csv")
    # sklearn
    sk_polynomial_reg(trainX, trainY)
    # original
    my_polynomial_reg(trainX, trainY)
