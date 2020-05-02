# -*- coding: <utf-8> -*-
"""Classical Linear Regression."""

# for importing the data directory
import os, sys
sys.path.append(os.getcwd())

import numpy as np
from matplotlib import pyplot as plt
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from data.loaddata import *


def header(name):
    """Printing header."""
    print("")
    print("##################")
    print(name)
    print("##################")


def plot_fig_decision(trainX, vec, name):
    """Making figure with plots and decision surface."""
    trainX_0, trainX_1 = trainX[:50], trainX[50:]

    centre = (trainX_0.mean(axis=0) + trainX_1.mean(axis=0)) / 2
    x = np.array([min(trainX[:, 0]), max(trainX[:, 0])])
    grad = -vec[0] / vec[1]
    y = (x - centre[0]) * grad + centre[1]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(trainX_0[:, 0], trainX_0[:, 1], c="blue")
    ax.scatter(trainX_1[:, 0], trainX_1[:, 1], c="red")
    ax.plot(x, y, c="black")
    base = os.path.join(os.path.dirname(__file__), 'png')
    fig.savefig(base + "/{}.png".format(name))


def plot_fig_projection(trainX, vec, name):
    """Making figure with plots and projection surface."""
    trainX_0, trainX_1 = trainX[:50], trainX[50:]

    centre = (trainX_0.mean(axis=0) + trainX_1.mean(axis=0)) / 2
    x = np.array([centre[0]-0.3, centre[0]+0.3])
    grad = vec[1] / vec[0]
    y = (x - centre[0]) * grad + centre[1]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(trainX_0[:, 0], trainX_0[:, 1], c="blue")
    ax.scatter(trainX_1[:, 0], trainX_1[:, 1], c="red")
    ax.plot(x, y, c="black", linestyle="dashed")
    base = os.path.join(os.path.dirname(__file__), 'png')
    fig.savefig(base + "/{}.png".format(name))


def calcref(trainX, trainY):
    """Calclating reference by sklearn LDA."""
    header("sklearn LDA")

    lda = LDA(n_components=2)
    lda.fit(trainX, trainY)

    print("Coefficient:")
    print(lda.coef_)
    plot_fig_decision(trainX, lda.coef_[0], "sklearn_lda_decision")
    plot_fig_projection(trainX, lda.coef_[0], "sklearn_lda_projection")


def my_LDA(trainX, trainY):
    """Calculating original LDA."""
    header("Original LDA")

    # 1.fisher線形分別法による解法
    # まずクラスを分ける
    class_0 = trainX[np.where(trainY==0)]
    # class_a = trainX[trainY==0] // これの方がスマート
    class_1 = trainX[np.where(trainY==1)]
    # 各クラスの共分散行列を計算
    convmat_0 = np.cov(class_0, rowvar=0, bias=0)
    convmat_1 = np.cov(class_1, rowvar=0, bias=0)
    # 総クラス内分散を求める
    sw = convmat_0 + convmat_1
    # 各クラスの平均の差
    m = class_0.mean(axis=0) - class_1.mean(axis=0) 
    # coeffの算出
    my_fisher_coeff = np.dot(np.linalg.inv(sw), m)

    # 2.特異値分解による解法(あってないかもしれないです...)
    U, s, V = np.linalg.svd(trainX, full_matrices=True)
    # sに対する直行ベクトル(90度回転させる)
    my_svd_coeff = np.dot(np.array([[0, -1],[1, 0]]), s)

    # 3.scikit-learn (SVD以外)
    lda_eigen = LDA(solver='eigen', n_components=2)
    lda_eigen.fit(trainX, trainY)
    lda_lsqr = LDA(solver='lsqr', n_components=2)
    lda_lsqr.fit(trainX, trainY)

    # fisherの方がsklearnの値に近いのでこっちを採用
    coeff = my_fisher_coeff
    print("Coefficient:")
    print("Fisher: ", my_fisher_coeff)
    print("SVD: ", my_svd_coeff)
    print("Sklearn Eigen: ", lda_eigen.coef_[0])
    print("Sklearn lsqr: ", lda_lsqr.coef_[0])
    plot_fig_decision(trainX, coeff, "my_lda_decision")
    plot_fig_projection(trainX, coeff, "my_lda_projection")


if __name__ == '__main__':
    trainX, trainY = loaddata()
    # scikit-learn
    calcref(trainX, trainY)
    # original
    my_LDA(trainX, trainY)
