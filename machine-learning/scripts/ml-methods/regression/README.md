# Regression

線形回帰・・・PLS, Random Forest  
非線形回帰・・・SVM, Gaussian Process, Random Forest

目次

* [線形回帰](#線形回帰)
* [多項式回帰](#多項式回帰)
* [Lasso](#Lasso)
* [Ridge](#Ridge)
* [ガウス過程回帰](#ガウス過程回帰)

# 線形回帰

線形回帰は、ただの最小2乗法なので省略

## 実装

```
$ python linear_regression/linear_reg.py
```

# 多項式回帰
Polynominal regression

## 実装
```
$ python polynominal_regression/polynominal_reg.py
```

## 理論

線形回帰と実はほとんど変わらない。

多項式回帰なので、回帰式を以下のように設定する。  
<br />
<img src="https://latex.codecogs.com/svg.latex?f(x)&space;=&space;\sum&space;w_n&space;x^{n-1}" title="f(x) = \sum w_n x^{n-1}" /><br />

この時, 目的関数は２乗和誤差を採用し以下のようになる。  
<br />
<img src="https://latex.codecogs.com/svg.latex?loss&space;=&space;\sum&space;{(Y_i&space;-&space;f(X_i))}" title="loss = \sum {(Y_i - f(X_i))}" />

この式を最少にする`w`の解は, 上式を`w`で微分することで算出される以下の式より計算出来る。  
<br />
<img src="https://latex.codecogs.com/svg.latex?w=&space;(\Phi&space;^{T}&space;\Phi&space;&plus;&space;\lambda&space;I)^{-1}&space;\Phi&space;^{T}&space;Y" title="w= (\Phi ^{T} \Phi + \lambda I)^{-1} \Phi ^{T} Y" /><br />
<br />
<img src="https://latex.codecogs.com/svg.latex?\Phi&space;=&space;\begin{pmatrix}&space;\phi_0(X_1)&space;&&space;\phi_1(X_1)&space;&\cdots&space;&&space;\phi_M(X_1)&space;\\&space;\phi_0(X_2)&space;&&space;\phi_1(X_2)&space;&\cdots&space;&&space;\phi_M(X_2)&space;\\&space;\vdots&space;&&space;\vdots&space;&&space;\ddots&space;&&space;\vdots&space;\\&space;\phi_0(X_N)&space;&&space;\phi_1(X_N)&space;&\cdots&space;&&space;\phi_M(X_N)&space;\\&space;\end{pmatrix}" title="\Phi = \begin{pmatrix} \phi_0(X_1) & \phi_1(X_1) &\cdots & \phi_M(X_1) \\ \phi_0(X_2) & \phi_1(X_2) &\cdots & \phi_M(X_2) \\ \vdots & \vdots & \ddots & \vdots \\ \phi_0(X_N) & \phi_1(X_N) &\cdots & \phi_M(X_N) \\ \end{pmatrix}" /><br />
<br />
<img src="https://latex.codecogs.com/svg.latex?\phi&space;_n&space;(x)&space;=&space;x^{n},&space;M&space;=&space;degree" title="\phi _n (x) = x^{n}, M = degree" /><br />

## 参考文献
* [https://qiita.com/NNNiNiNNN/items/d87990a6eef72a3815a3](https://qiita.com/NNNiNiNNN/items/d87990a6eef72a3815a3)

# Lasso

L1正則化と呼ばれる。

## 実装

```
$ python lasso/polynomial_reg_with_lasso.py

// confirm the collinearity
$ python lasso/collinearity.py
```

## 理論

* 損失関数に **L1ノルム(各項の絶対値の和)** を加えて最小化する手法。
* 解析解が存在しないため、座標降下法などのアルゴリズムによって最小化する。(詳しくはコード参照)  
→ L1ノルムを加えるので、微分が簡単にできない

## 特徴

* スパースな解が得られる (係数が0になるような解)  
→ 次元削減に繋がる
* 共線性を持つ説明変数でも線形な回帰が可能になる

## 参考文献
* [実装・アルゴリズム](https://satopirka.com/2017/10/lasso%E3%81%AE%E7%90%86%E8%AB%96%E3%81%A8%E5%AE%9F%E8%A3%85--%E3%82%B9%E3%83%91%E3%83%BC%E3%82%B9%E3%81%AA%E8%A7%A3%E3%81%AE%E6%8E%A8%E5%AE%9A%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0-/)


# Ridge

L2正則化と呼ばれる。

## 実装

```
$ python ridge/polynomial_reg_with_ridge.py
```

## 理論

* 損失関数に **L2ノルム(ユークリッド長さ、各項の2乗和のルート)** を加えて最小化する手法。
* Ridgeの場合は解析解が存在する。(詳しくはコード参照)

## 特徴

* 過学習を抑えることが可能になる
* 共線性を持つ説明変数でも線形な回帰が可能になる

## 参考文献
* [Ridge 理論](https://satopirka.com/2017/10/%E9%87%8D%E5%9B%9E%E5%B8%B0%E3%83%A2%E3%83%87%E3%83%AB%E3%81%AE%E7%90%86%E8%AB%96%E3%81%A8%E5%AE%9F%E8%A3%85--%E3%81%AA%E3%81%9C%E6%AD%A3%E5%89%87%E5%8C%96%E3%81%8C%E5%BF%85%E8%A6%81%E3%81%8B-/)

# ガウス過程回帰

## 実装

```
$ python gaussian_process/gp.py
```

## 理論


## 特徴

