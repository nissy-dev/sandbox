# Dimensionality reduction

次元削減・・・計算効率を改善するために使用される

目次

* [線形判別分析](#線形判別分析)
* [主成分分析](#主成分分析)

sklearn reference  
[https://scikit-learn.org/stable/modules/classes.html#module-sklearn.decomposition](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.decomposition)

# 線形判別分析
Linear Discriminant Analysis (LDA)

## 実装
```
$ python lda/lda.py
```

## 理論

1. 射影後の各クラス間の分散を最大化(各クラスの重心間の距離を最大化) => クラス間はよく離れる
2. 射影後のクラス内の分散の最小化 => それぞれのクラス内のデータは凝集

各クラス間の分散 ： <img src="https://latex.codecogs.com/svg.latex?w^{T}&space;S_B&space;w^{T}&space;=&space;w^{T}(m_1&space;-&space;m_2)(m_1&space;-&space;m_2)^{T}w^{T}" title="w^{T} S_B w^{T} = w^{T}(m_1 - m_2)(m_1 - m_2)^{T}w^{T}" />  
クラス内の分散 ： <img src="https://latex.codecogs.com/svg.latex?s^2&space;=&space;w^{T}S_Ww" title="s^2 = w^{T}S_Ww" /> <img src="https://latex.codecogs.com/svg.latex?S_W&space;=&space;\sum&space;{(x_n-m_1)^2}&space;&plus;&space;\sum&space;{(x_n-m_2)^2}" title="S_W = \sum {(x_n-m_1)^2} + \sum {(x_n-m_2)^2}" />   

1, 2を同時に満たすような状況を求めるとなると、結局以下の式を最大化することになる。

<img src="https://latex.codecogs.com/svg.latex?J(W)&space;=&space;\frac&space;{w^{T}S_Bw}&space;{w^{T}S_Ww}" title="J(W) = \frac {w^{T}S_Bw} {w^{T}S_Ww}" />

この解は、ラグランジェの未定乗数法で解くと以下になる。

<img src="https://latex.codecogs.com/svg.latex?w&space;=&space;S_w^{-1}&space;(m_1&space;-m_2)" title="w = S_w^{-1} (m_1 -m_2)" />

よって解析的に求まる。  
<br />
また特異値分解でも算出可能。(特徴量の次元が大きい時には、かなり有利になる)  
**固有値分解は一旦データを正方行列に直して計算を行う一方で, 特異値分解はデータの形を保ったままに次元削減が可能。**

## 特徴

* 教師がラベルが必要
* **ラベルが最も分離されるように射影を最適化する**

## 参考文献
* [https://www.hellocybernetics.tech/entry/2016/08/07/054847](https://www.hellocybernetics.tech/entry/2016/08/07/054847)

# 主成分分析
Principal Component Analysis (PCA)

## 実装
```
$ python pca/pca.py
```

## 理論

1. 全データの重心を探す (平均値を求める)
2. 重心からデータの分散が最大化するような方向を探す
3. 2.で求めた方向を基底として、直交する軸方向に対して分散が最大になる方向を探す
4. 3.をくり返す

数式的には、ラグランジェの未定乗数法を用いて射影後の共分散行列を最大化する`W`を求める。  
以下の式を微分した式が0になるような`W`が解である  
<br />
<img src="https://latex.codecogs.com/svg.latex?L(W)&space;=&space;w^{T}\sum&space;w&space;-&space;\lambda&space;(w^{T}w&space;-&space;I)" title="L(W) = w^{T}\sum w - \lambda (w^{T}w - I)" /><br />
<img src="https://latex.codecogs.com/svg.latex?\sum&space;=&space;\frac{1}{N-1}(X-\mu)(X-\mu)^{T}" title="\sum = \frac{1}{N-1}(X-\mu)(X-\mu)^{T}" /><br />
<br />
これは、結局射影後の分散共分散(Σ)の固有値問題に帰着する。

また、各軸の寄与率も算出することが可能で、**寄与率は各軸がどれだけデータを説明できているのかを表す指標。**

## 特徴
* 教師がラベルが不要
* **分散が最大になるように射影を最適化する**
* 2次元に落とし込み、外れサンプルを探す
* 画像処理で、白色化(`標準化+各成分の無相関化`)する際にも使用されることもある  
→ とは言っても、実際はZCAの解釈性が高いのであまり使われない

ref : [https://www.slideshare.net/shuheisowa/ss-67524364](https://www.slideshare.net/shuheisowa/ss-67524364)


## 参考文献
* [https://speakerdeck.com/hkaneko/zhu-cheng-fen-fen-xi-principal-component-analysis-pca](https://speakerdeck.com/hkaneko/zhu-cheng-fen-fen-xi-principal-component-analysis-pca)
* [https://logics-of-blue.com/principal-components-analysis/](https://logics-of-blue.com/principal-components-analysis/)
* [https://ohke.hateblo.jp/entry/2017/12/14/230500](https://ohke.hateblo.jp/entry/2017/12/14/230500)