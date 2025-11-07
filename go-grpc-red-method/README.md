# Go gRPC サーバーで RED 指標のモニタリングを整備する

https://zenn.dev/nissy_dev/scraps/24bafcf85a9d07

## ダッシュボードを見る手順

```sh
// server の起動
make run

// grafana と prometheus のセットアップ
make setup-infra

// k6 で負荷をかける
make k6-load-test
```
