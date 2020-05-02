# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from matplotlib import pyplot as plt
from math import ceil

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.metrics import r2_score
from sklearn.metrics import f1_score


def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def calcref(trainX, trainY, testX, testY):
    """Calclating reference by sklearn svm."""
    header("sklearn svm")

    model = SVC()
    model.fit(trainX, trainY)
    pred = model.predict(testX)

    print('Test score : {:.3f}'.format(r2_score(pred, testY)))
    print('Confusion matrix:\n{}'.format(confusion_matrix(pred, testY)))


def my_svm(trainX, trainY, testX, testY):
    """Calculating original svm"""
    header("Original svm")
    return 


if __name__ == '__main__':
    iris = load_iris()
    trainX, testX, trainY, testY = train_test_split(iris.data, iris.target, test_size=0.2, random_state=123)
    # scikit-learn
    calcref(trainX, trainY, testX, testY)
    # original
    my_svm(trainX, trainY, testX, testY)
