# Classification

目次

* [ロジスティック回帰](#ロジスティック回帰)
* [ランダムフォレスト](#ランダムフォレスト)
* [サポートベクターマシーン](#サポートベクターマシーン)
 
# ロジスティック回帰
## 実装
```
$ python logistic_regression/logitreg.py
```

## 理論
* Affin変換した値 (`Wx+b`) をSigmoid関数に渡し、その出力が0.5以上なら`1`、それ以外は`0`と予想するモデル
* 対数尤度を最大化(クロスエントロピーの最小化)する方法で、最適な`W`, `b`を決定する  
→ 勾配法を利用して最適化は行われる  
→ クロスエントロピーは凸関数であり、**局所解=最適解**が保証される

Sigmoid関数 ： <img src="https://latex.codecogs.com/svg.latex?L&space;=&space;tlogy&space;-&space;(1-t)log(1-y)" title="L = tlogy - (1-t)log(1-y)" />

クロスエントロピー (確率: y, 正解ラベル: t)  
2値分類  :  
<img src="https://latex.codecogs.com/svg.latex?L&space;=&space;-tlogy&space;-&space;(1-t)log(1-y)" title="L = -tlogy - (1-t)log(1-y)" /><br />
多値分類  :  
<img src="https://latex.codecogs.com/svg.latex?L&space;=&space;-\sum&space;t_i&space;logy_i" title="L = -\sum t_i logy_i" />

## 尤度とは？
ある事象が起きた時を考える。その事象が起きた時の前提条件を考える時に、その青木た事象の結果から見た時の与えられた前提条件の確からしさを返す関数のこと。

**要は、「Wを適当に与えた時の予想ラベルが真の条件を元にしてどれだけ正しいのか」を返す関数を損失関数に使用しているということ。**

クロスエントロピーは、対数尤度にマイナスをかけたものである。

## NNモデルとLogistic回帰モデルの比較
ref: https://www.renom.jp/ja/notebooks/tutorial/basic_algorithm/lossfunction/notebook.html

|  モデル              |  Activation  |  Loss             |
| ------------------  | -----------  | ----------------- |
|  ２値分類 (Logistic) |  sigmoid     |  cross entropy    |
|  多値分類 (NN)       |  softmax     |  cross entropy    |
|  回帰 (NN)          |  -           |  **MSE(2乗和誤差)** |

# ランダムフォレスト 
## 実装

```
$ python random_forest/sample.py
$ python random_forest/iris.py
```

## 理論

1. 作成する決定木の分だけ、重複を許してデータをサンプリング (bootstrap sampling)
2. それぞれのデータを利用して、決定木を作成する
3. それぞれの決定木の予想結果の多数決で出力を決定する


## 決定木
特徴量の値を閾値と用いてデータを分割する木構造を作成する。  
木構造の成長は、基本的には、ノードの要素が1つになるか同じラベルになるかのいずれかまで行う。

また、分割する際の特徴量の値は、以下のように決定する。

1. 各特徴量の値を元に、分割の候補値を算出する(中点が候補になる)  
→ 特徴量の値 [0, 1, 2, 3, 4, 5] -> 分割候補 [0.5  1.5  2.5  3.5  4.5]
2. 各特徴量の分割候補を元に分割を行う
3. gain informationを最小になる特徴量・および分割の値を決定  
→ gain information = 分割がうまくできているかどうか測る指標(ジニ係数, エントロピー)

決定木は、通常では過学習している状態。なので、**枝かりをして汎用性を高める。**(枝かりも実装済み)  
Random forestでは、複数の決定木を用いることで過学習の影響を無くしている。

## 特徴
* チューニングに必要なパラメータが少ない
* 特徴量の重要度などを算出できることができ、解釈性が高い
* 木ごとの並列計算が可能
* 説明変数が多数であってもうまく働く
* **Feature Scaling(正規化, 標準化)がそこまで必要ではない**

# サポートベクターマシーン

## 実装
```
$ python svm/svm.py
```

## 理論
