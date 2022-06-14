# メモ

## 時系列データ処理

### 信号処理 (スペクトルとか)

#### 前処理

ノイズを除去して平滑化を行うのが基本

- フィルタ方法の基本 (いっぱいある...)
  - 移動平均フィルター
    - 解説 : http://www.mech.tohoku-gakuin.ac.jp/rde/contents/sendai/mechatro/archive/RMSeminar_No07_s8.pdf
  - メディアン フィルター
  - Savitzky-Golay フィルター
    - 多項式をノイズ データの各フレームに近似する上で、最小二乗誤差を最小にする
    - 通常、ノイズを含むがノイズのない部分の周波数範囲が広い信号の平滑化に使用
    - 解説 : https://jp.mathworks.com/help/signal/ref/sgolay.html
  - Hampel フィルター
    - データを小さく（窓サイズ）で区分けして、3σ 法で外れ値（スパイク）を検出する
    - 解説 : https://cpp-learning.com/hampel-filter/
- fft によるフィルタリング
  - ローパスフィルタ
  - ハイパスフィルタ
  - fft を使う時は、周期性があることが重要
    - 窓関数を使った平滑化・不連続性の緩和
    - https://www.logical-arts.jp/archives/124
  - チュートリアル : https://nykergoto.hatenablog.jp/entry/2019/07/09/FFT_%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%9F%E6%99%82%E7%B3%BB%E5%88%97%E3%83%87%E3%83%BC%E3%82%BF%E8%A7%A3%E6%9E%90

#### 特徴量エンジニアリング

- ラグ特徴量
- 微分特徴量
- 窓関数による集約の特徴量
- tsfresh が便利らしい
  - 一気に特徴量を作ってくれるライブラリ
  - https://tsfresh.readthedocs.io/en/latest/index.html
