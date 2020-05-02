import os
import numpy as np

# https://qiita.com/ttskng/items/2a33c1ca925e4501e609
def normalization(X):
    """
    normalization: data range changes 0~1 
    X_norm = (X - X_min) / (X_max - X_min)
    """
    return (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))

def standardization(X):
    """
    standardization: average = 1, variance = 0
    X_stand = (X - X_mean) / (X_std)
    """
    return (X - X.mean(axis=0)) / X.std(axis=0)

def loaddata(name, preprocessing='standardization'):
    """Loading learning data."""
    PATH = os.path.join(os.path.dirname(__file__), name)
    data = np.loadtxt(PATH, delimiter=",")
    trainY = data[:, 0]
    trainX = data[:, 1:]
    # preprocess
    trainX = standardization(trainX) if preprocessing == 'standardization' \
        else normalization(trainX)
    return trainX, trainY
