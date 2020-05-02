# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from copy import deepcopy
from matplotlib import pyplot as plt
from sklearn import linear_model, preprocessing


def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def loaddata():
    x1 = np.random.rand(20) * 10
    # x2: x1の２倍
    x2 = x1 * 2
    x3 = np.random.uniform(-5, 5, 20)
    x4 = np.random.uniform(-3, 2, 20)
    trainX = np.array(np.array([x1, x2, x3, x4]).T)
    trainY = np.random.randint(0, 40, 20)
    return trainX, trainY


def sk_lasso(trainX, trainY):
    """confirm deleting the colinearity by LASSO."""
    header("Confirm deleting the colinearity by LASSO.")

    clf_lasso = linear_model.Lasso(alpha=1.0)
    clf_lasso.fit(trainX, trainY)
    print("Coeff.:", clf_lasso.coef_)
    print("Intercept:", clf_lasso.intercept_)


if __name__ == '__main__':
    trainX, trainY = loaddata()
    # sklearn
    sk_lasso(trainX, trainY)
