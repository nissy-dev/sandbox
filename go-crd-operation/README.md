# Go CRD Operation

## セットアップ

```bash
# kind と kubectl のインストール
brew install kind kubectl

# クラスタのセットアップ
make setup-cluster

# CRD の適用
make apply-crd
```

## 使い方

```bash
# アプリケーションのビルドと実行
make run

# すべてを一度に実行
make all
```

## クリーンアップ

```bash
# ビルド成果物の削除
make clean

# クラスタの削除
make teardown-cluster
```

## CRD について

このプロジェクトでは `MyResource` という CRD を定義しています。

### リソースの仕様

- **Group**: `example.com`
- **Version**: `v1`
- **Kind**: `MyResource`
- **Plural**: `myresources`
- **Short name**: `mr`

### フィールド

- `spec.field1` (string): 文字列フィールド
- `spec.field2` (integer): 整数フィールド
- `status.state` (string): リソースの状態
