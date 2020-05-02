import numpy as np

### 分類の良し悪しを判断する基準となる関数 (損失関数みたいなもの) ###

def calc_gini(target):
    """
    calculate gini impurity
    target : 各データの分類ラベル

    小さいほどラベルのばらつきが小さくなりNodeに1つのラベルが多く占める
    """
    classes = np.unique(target)
    numdata = target.shape[0]

    gini = 1.0
    for c in classes:
        gini -= (float(len(target[target == c])) / numdata) ** 2.0
    return gini


def calc_entropy(target):
    """
    calculate entropy
    target : 各データの分類ラベル

    小さいほどラベルのばらつきが小さくなりNodeに1つのラベルが多く占める
    """
    classes = np.unique(target)
    numdata = target.shape[0]

    entropy = 0.0
    for c in classes:
        p = float(len(target[target == c])) / numdata
        if p != 0.0:
            entropy -= p * np.log2(p)
    return entropy
