import numpy as numpy
from collections import Counter
from random_forest.modules.decision_tree import *

class MyRandomForest:
    """My Random Forest"""
    def __init__(self, criterion='gini', n_components=10, max_depth=None):
        """初期化処理
        tree         : 各決定木を保存する
        criterion    : gain情報を計算する関数 (gini or entropy) 
        n_components : 決定木の数
        max_depth    : 最大深さ
        """
        self.tree          = []
        self.n_components  = n_components
        self.criterion     = criterion
        self.max_depth     = max_depth

    def fit(self, data, target):
        numdata = data.shape[0]
        for i in range(self.n_components):
            # 枝刈りはしない
            tree = MyDecisionTree(self.criterion, self.max_depth, False)
            # N個のデータから重複を許してN個取り出す
            index = np.random.choice(numdata, numdata)
            tree.fit(data[index], target[index])
            self.tree.append(tree)

    def predict(self, data):
        pred_list = []
        for tree in self.tree:
            pred_list.append(tree.predict(data))

        # 多数決をとってラベルを決める
        ans = []
        for all_ans in np.array(pred_list).T:
            vote = Counter(all_ans).most_common(1)[0][0]
            ans.append(vote)

        return ans
