import numpy as np
from random_forest.modules.node import *

class MyDecisionTree:
    """CARTによる分類木学習器"""
    def __init__(self, criterion='gini', max_depth=5, prune=True):
        """初期化処理
        root      : 決定木のルートノード
        criterion : gain情報を計算する関数 (gini or entropy) 
        max_depth : 最大深さ
        prune     : 枝刈りをするか
        """
        self.root          = None
        self.criterion     = criterion
        self.max_depth     = max_depth
        self.prune         = prune

    def fit(self, data, target):
        """学習を行い決定木を構築する
        data   : 学習データ
        target : 各データの分類クラス
        """
        self.root = Node()
        self.root.fit(data, target, 0)
        if self.prune == True:
            # 枝かりの閾値 (大きいほど木が浅くなる)
            threshold = 0.1
            self.root.prune(threshold, self.root.numdata)

        pass

    def predict(self, data):
        """分類クラスの予測を行う
        data : テストデータ
        """
        ans = []
        for d in data:
            ans.append(self.root.predict(d))
        return np.array(ans)
