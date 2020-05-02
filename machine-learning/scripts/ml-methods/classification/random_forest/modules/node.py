import numpy as numpy
from random_forest.modules.functions import *

# ref: http://codecrafthouse.jp/p/2014/09/decision-tree/
# ref: http://darden.hatenablog.com/entry/2016/12/15/222447
class Node:
    def __init__(self, criterion="gini", max_depth=None):
        """初期化処理
        left       : 左の子ノード（しきい値未満）
        right      : 右の子ノード（しきい値以上）
        feature    : 分割する特徴番号 (どの特徴量で分割するのか)
        threshold  : 分割するしきい値
        label      : 割り当てられたクラス番号
        numdata    : 割り当てられたデータ数
        info_gain  : 分割指数
        criterion  : 分割指数を計算する関数
        depth      : 自分のノードの深さ
        max_depth  : 最大深さ
        """
        self.left = None
        self.right = None
        self.feature = None
        self.threshold = None
        self.label = None
        self.numdata = None
        self.info_gain = 0.0
        self.criterion = criterion
        self.max_depth = max_depth

    def criterion_func(self, target):
        if self.criterion == "gini":
            val = calc_gini(target)
        elif self.criterion == "entropy":
            val = calc_entropy(target)

        return val

    def calc_delta_info_gain(self, target_l, target_r):
        """不純度の差分計算
        target_l : 左の子ノードのデータの分類クラス
        target_r : 右の子ノードのデータの分類クラス
        """
        # 分割後の不純度から分割指数を計算
        gini_l = self.criterion_func(target_l)
        gini_r = self.criterion_func(target_r)
        ## left nodeに流れたデータの割合
        pl = float(target_l.shape[0]) / self.numdata
        ## right nodeに流れたデータの割合
        pr = float(target_r.shape[0]) / self.numdata
        return pl * gini_l + pr * gini_r

    def fit(self, data, target, depth):
        """木の構築を行う
        data   : ノードに与えられたデータ
        target : データの分類クラス
        depth  : ノードの深さ
        """
        self.depth = depth
        self.numdata = data.shape[0]
        num_features = data.shape[1]

        # 全データが同一クラスとなったら分割終了
        if len(np.unique(target)) == 1:
            self.label = target[0]
            return

        # 自分のクラスを設定(各データの多数決)
        # Node内データが同一のクラスにならなかった場合は多数決をとってラベルを決める
        class_cnt = {i: len(target[target==i]) for i in np.unique(target)}
        self.label = max(class_cnt.items(), key=lambda x:x[1])[0]

        # 自分の不純度を計算しておく
        parent_info_gain = self.criterion_func(target)
        for f in range(num_features):
            # 分割の閾値候補(points)の計算
            data_f = np.unique(data[:, f]) # f番目の特徴量（重複排除）
            # 各特徴量の中間の値を計算
            # [0, 1, 2, 3, 4, 5] -> [0.5  1.5  2.5  3.5  4.5]
            points = (data_f[:-1] + data_f[1:]) / 2.0 

            # 各分割を試す
            for threshold in points:
                # しきい値で2グループに分割
                target_l = target[data[:, f] <  threshold]
                target_r = target[data[:, f] >= threshold]
                child_info_gain = self.calc_delta_info_gain(target_l, target_r)
                info_gain = parent_info_gain - child_info_gain

                # より良い分割であれば記憶しておく
                ## 差分(info_gain)が大きほど良い分割
                if self.info_gain < info_gain:
                    self.info_gain = info_gain
                    self.feature   = f
                    self.threshold = threshold

        # 不純度が減らなければ終了
        if self.info_gain == 0:
            return

        # 最大深さに達したら終了
        if self.depth == self.max_depth:
            return

        # 左右の子を作って再帰的に分割させる
        data_l   =   data[data[:, self.feature] <  self.threshold]
        target_l = target[data[:, self.feature] <  self.threshold]
        self.left = Node()
        self.left.fit(data_l, target_l, self.depth + 1)

        data_r   =   data[data[:, self.feature] >= self.threshold]
        target_r = target[data[:, self.feature] >= self.threshold]
        self.right = Node()
        self.right.fit(data_r, target_r, self.depth + 1)

    def predict(self, input_data):
        """入力データ（単一）の分類先クラスを返す"""
        # 自分が節の場合は再帰的に条件判定
        if self.feature != None:
            if input_data[self.feature] < self.threshold:
                return self.left.predict(input_data)
            else:
                return self.right.predict(input_data)
        # 自分が葉の場合は自分の分類クラスを返す
        else:
            return self.label

    def prune(self, criterion, numall):
        """木の剪定を行う(過学習の防止, 特徴量選択)
        criterion  : 剪定条件（この数以下は剪定対象）
        numall     : 全ノード数
        """
        # 自分が葉ノードであれば終了
        if self.feature == None:
            return

        # 子ノードの剪定
        self.left.prune(criterion, numall)
        self.right.prune(criterion, numall)

        # 子ノードが両方葉であれば剪定チェック
        if self.left.feature == None and self.right.feature == None:
            # 分割の貢献度：gain_info * (データ数の割合)
            result = self.info_gain * float(self.numdata) / numall
            # 貢献度が条件に満たなければ剪定する
            if result < criterion:
                self.feature = None
                self.left = None
                self.right = None
