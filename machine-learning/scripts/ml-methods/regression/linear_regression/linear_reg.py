# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
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


def calcref(trainX, trainY):
    """Calclating reference by sklearn LinearRegression."""
    header("sklearn linear regression")

    sklr = linear_model.LinearRegression(fit_intercept=True)
    sklr.fit(trainX, trainY)

    print("Coeff.:", sklr.coef_)
    print("Intercept:", sklr.intercept_)


def my_linear_regression(trainX, trainY):
    """Calculating original linear regression."""
    header("Original linear regression")

    W = np.dot(np.linalg.inv(trainX.T @ trainX), (trainX.T @ trainY))
    trainX_ave = np.average(trainX, axis=0)
    trainY_ave = np.average(trainY)
    intercept = trainY_ave - W.dot(trainX_ave)

    print("Coeff.:", W)
    print("Intercept:",  intercept)

if __name__ == '__main__':
    trainX, trainY = loaddata("linear_reg.csv")
    # sklearn
    calcref(trainX, trainY)
    # original
    my_linear_regression(trainX, trainY)
