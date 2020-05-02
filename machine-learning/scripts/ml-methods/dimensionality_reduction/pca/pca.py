# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from matplotlib import pyplot as plt
from sklearn import decomposition
from data.loaddata import *

def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def plot_fig(trainX, vec, name):
    """Making figure with plots and projection surface."""
    trainX_0, trainX_1 = trainX[:50], trainX[50:]

    centre = (trainX_0.mean(axis=0) + trainX_1.mean(axis=0)) / 2
    grad = vec[1] / vec[0]
    x = np.array([min(trainX[:, 0]), max(trainX[:, 0])])
    y = (x - centre[0]) * grad + centre[1]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(trainX_0[:, 0], trainX_0[:, 1], c="blue")
    ax.scatter(trainX_1[:, 0], trainX_1[:, 1], c="red")
    ax.plot(x, y, c="black", linestyle="dashed")
    base = os.path.join(os.path.dirname(__file__), 'png')
    fig.savefig(base + "/{}.png".format(name))


def calcref(trainX):
    """Calclating reference by sklearn PCA."""
    header("sklearn PCA")

    pca = decomposition.PCA(n_components=2)
    pca.fit(trainX)
    transformed = pca.transform(trainX)

    print("Components:")
    print(pca.components_)
    print("Explained ratio:")
    print(pca.explained_variance_ratio_)
    print("Transformed data:")
    print(transformed[0:2])
    plot_fig(trainX, pca.components_[0], "sklearn_pca_projection")


def my_PCA(trainX):
    """Calculating original PCA."""
    header("Original PCA")

    # np.covを使用する
    # w,v = np.linalg.eig(np.cov(trainX, rowvar=False))
    # np.covを使用しない
    # npは整数同士を割ると整数を返すので, floatを挟む
    w,v = np.linalg.eig(np.dot(trainX.T, trainX)/float(trainX.shape[0]-1))
    # 固有値の降順でindexを取得 
    w_index = np.argsort(w)[::-1]
    # 寄与率の計算
    explaned_ratio = w[w_index]/np.sum(w)
    # 固有ベクトルをindexを元にソート
    my_components = v[:, w_index]
    # 逆写像後のデータ
    trainX_inverse = np.dot(trainX, my_components)

    components = my_components[0]

    print("Components:")
    print(my_components)
    print("Explained ratio:")
    print(explaned_ratio)
    print("Transformed data:")
    print(trainX_inverse[0:2])
    plot_fig(trainX, components, "my_pca_projection")


if __name__ == '__main__':
    trainX, trainY = loaddata()
    # skleran
    calcref(trainX)
    # original
    my_PCA(trainX)
