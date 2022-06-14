import pandas as pd
from os import path


def load_features(FEATURE_PATH, feats):
    dfs = [pd.read_feather(path.join(FEATURE_PATH, f'{f}_train.ftr')) for f in feats]
    X_train = pd.concat(dfs, axis=1)
    dfs = [pd.read_feather(path.join(FEATURE_PATH, f'{f}_test.ftr')) for f in feats]
    X_test = pd.concat(dfs, axis=1)
    return X_train, X_test
