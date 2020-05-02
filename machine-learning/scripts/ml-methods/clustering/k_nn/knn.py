# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn.model_selection import train_test_split
from collections import Counter
from sklearn.neighbors import KNeighborsClassifier
from data.loaddata import *


def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def calcref(X, Y):
    """Calclating reference by sklearn knn."""
    header("sklearn knn")

    X_train, X_test, Y_train, Y_test = \
        train_test_split(X, Y, test_size = 0.2, random_state=1, stratify=Y)
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, Y_train)
    pred = knn.predict(X_test)

    print("Accuracy:")
    print(metrics.accuracy_score(Y_test, pred))
    print("Confusion matrix:")
    print(metrics.confusion_matrix(Y_test, pred))


def my_knn(X, Y):
    """Calculating original knn."""
    header("Original knn")

    # 自分の実装
    X_train, X_test, Y_train, Y_test = \
        train_test_split(X, Y, test_size = 0.2, random_state=1, stratify=Y)
    knn = MyKnn()
    knn.fit(trainX, trainY)
    pred = knn.predict(X_test)

    print("Accuracy:")
    print(metrics.accuracy_score(Y_test, pred))
    print("Confusion matrix:")
    print(metrics.confusion_matrix(Y_test, pred))


class MyKnn:
    def __init__(self, n_neighbors=3):
        self.n_neighbors = n_neighbors
        self._train = None
        self._target = None

    def __cal__distance(self, p0, p1):
        return np.sum((p0 - p1) ** 2)

    def fit(self, data, target):
        # あらかじめ計算できるものがない...
        self._train = data
        self._target = target

    def predict(self, test):
        labels = []
        for data in test:
            # 距離の計算
            distances = np.array([self.__cal__distance(p, data) for p in self._train])
            # 近い順からn_neighbors個集める
            indexes = distances.argsort()[:self.n_neighbors]
            # n_neighbors個の中から多数決でラベルを決定
            label = Counter(self._target[indexes]).most_common(1)[0][0]
            labels.append(label)

        return labels


if __name__ == '__main__':
    trainX, trainY = loaddata()
    # sklearn
    calcref(trainX, trainY)
    # original
    my_knn(trainX, trainY)
