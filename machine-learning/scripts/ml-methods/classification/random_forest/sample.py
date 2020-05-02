# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from matplotlib import pyplot as plt
from math import ceil

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import r2_score
from sklearn.metrics import f1_score
from data.loaddata import *
from random_forest.modules.decision_tree import *

def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def calcref(trainX, trainY):
    """Calclating reference by sklearn random forest"""
    header("sklearn random forest")

    model = RandomForestClassifier()
    model.fit(trainX, trainY)
    pred = model.predict(trainX)

    print('Train score : {:.3f}'.format(r2_score(pred, trainY)))
    print('Confusion matrix:\n{}'.format(confusion_matrix(trainY, pred)))
    print('f1 score: {:.3f}'.format(f1_score(trainY, pred)))

def my_decision_tree(trainX, trainY):
    """Calculating original random forest."""
    header("Original random forest")

    model = MyDecisionTree()
    model.fit(trainX, trainY)
    pred = model.predict(trainX)

    print('Train score : {:.3f}'.format(r2_score(pred, trainY)))
    print('Confusion matrix:\n{}'.format(confusion_matrix(trainY, pred)))
    print('f1 score: {:.3f}'.format(f1_score(trainY, pred)))

if __name__ == '__main__':
    trainX, trainY = loaddata()
    # scikit-learn
    calcref(trainX, trainY)
    # original
    my_decision_tree(trainX, trainY)
