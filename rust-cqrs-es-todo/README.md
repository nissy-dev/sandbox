# Rust CQRS + Event Sourcing + DDD Todo サンプル

CQRS（Command Query Responsibility Segregation）と Event Sourcing、DDD を Rust で実装した Todo サンプル。永続化は PostgreSQL（sqlx）を使用。

## 前提

- [mise](https://mise.jdx.dev/)（Rust のバージョン管理）または Rust 1.70+
- PostgreSQL（Docker で起動する場合: `docker compose up -d`）

## セットアップ

### Rust のセットアップ（mise）

このディレクトリには `.mise.toml` があり、Rust のバージョンを固定している。mise を使う場合:

```bash
cd rust-cqrs-es-todo
mise install   # Rust（stable）をインストール
mise trust     # 必要に応じて .mise.toml を信頼
cargo --version
```

以降、このディレクトリに cd すると mise が自動で Rust を有効にする。

### PostgreSQL の起動（Docker）

```bash
docker compose up -d
```

接続文字列（デフォルト）:

```
postgres://postgres:postgres@localhost:5432/cqrs_todo
```

### 環境変数（任意）

- `DATABASE_URL`: 上記以外を使う場合に指定

## ビルド・実行

```bash
cargo build --release
cargo run -- create "my first todo"
cargo run -- list
cargo run -- get <id>
cargo run -- complete <id>
cargo run -- title <id> "new title"
```

## CLI コマンド

| コマンド                 | 説明                            |
| ------------------------ | ------------------------------- |
| `create [title]`         | 新規 Todo 作成                  |
| `list`                   | 全件一覧（Read 用 DB から取得） |
| `get <id>`               | 1 件取得                        |
| `complete <id>`          | 完了にする                      |
| `title <id> <new_title>` | タイトル変更（未完了のみ）      |

## 構成

- **domain**: 集約（Todo）、イベント、コマンド、スナップショット
- **application**: CommandHandler（コマンド → イベント保存 → プロジェクション）、QueryHandler（Read 用テーブル参照）
- **infrastructure**: Event Store（PostgreSQL `events` テーブル）、Read モデル（`todo_read_views`）、スナップショット（`snapshots`）、スキーマ DDL

起動時に `events`、`todo_read_views`、`snapshots` テーブルが存在しなければ自動作成される。

## スナップショット機能

イベントが無限に蓄積される問題を解決するため、スナップショット機能を実装しています。

- **自動作成**: 各集約に対して100イベントごとにスナップショットを自動作成
- **高速復元**: 集約を復元する際、最新のスナップショットから開始し、その後のイベントのみを適用
- **パフォーマンス向上**: イベント数が増えても、復元処理が高速に保たれます

スナップショットは `snapshots` テーブルに保存され、集約の状態（id, title, completed）とイベントのシーケンス番号を含みます。

## ドキュメント

詳細な解説は `docs` ディレクトリを参照してください：

- [CQRS のデータの流れ](./docs/cqrs-data-flow.md) - CQRS のアーキテクチャとデータの流れの詳細解説
- [スナップショット機能](./docs/snapshots.md) - スナップショットの実装と動作の詳細解説
