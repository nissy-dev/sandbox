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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import r2_score
from sklearn.metrics import f1_score
from random_forest.modules.decision_tree import *
from random_forest.modules.random_forest import *

def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def calcref(trainX, trainY, testX, testY):
    """Calclating reference by sklearn random forest"""
    header("sklearn random forest")

    model = RandomForestClassifier(random_state=2)
    model.fit(trainX, trainY)
    pred = model.predict(testX)

    print('Train score : {:.3f}'.format(r2_score(pred, testY)))
    print('Confusion matrix:\n{}'.format(confusion_matrix(pred, testY)))

def my_decision_tree(trainX, trainY, testX, testY):
    """Calculating original decision tree"""
    header("Original decision tree")

    model = MyDecisionTree(prune=False)
    model.fit(trainX, trainY)
    pred = model.predict(testX)

    print('Test score : {:.3f}'.format(r2_score(pred, testY)))
    print('Confusion matrix:\n{}'.format(confusion_matrix(pred, testY)))

def my_random_forest(trainX, trainY, testX, testY):
    """Calculating original random forest"""
    header("Original random forest")

    model = MyRandomForest()
    model.fit(trainX, trainY)
    pred = model.predict(testX)

    print('Test score : {:.3f}'.format(r2_score(pred, testY)))
    print('Confusion matrix:\n{}'.format(confusion_matrix(pred, testY)))


if __name__ == '__main__':
    iris = load_iris()
    trainX, testX, trainY, testY = train_test_split(iris.data, iris.target, test_size=0.2, random_state=123)
    # scikit-learn
    calcref(trainX, trainY, testX, testY)
    # original decision tree : overfit
    my_decision_tree(trainX, trainY, testX, testY)
    # original random forest
    my_random_forest(trainX, trainY, testX, testY)
