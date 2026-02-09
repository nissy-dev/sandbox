# CQRS のデータの流れ

このドキュメントでは、このプロジェクトにおける CQRS（Command Query Responsibility Segregation）のデータの流れを解説します。

## CQRS とは

CQRS は、データの**書き込み（Command）**と**読み込み（Query）**の責務を分離するアーキテクチャパターンです。

- **Command 側**: ビジネスロジックの実行とイベントの保存に特化
- **Query 側**: 読み取り専用の最適化されたデータ構造から高速にデータを取得

## アーキテクチャ概要

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │────────▶│  Command     │────────▶│ Event Store │
│  (CLI/API)  │         │  Handler     │         │  (events)   │
└─────────────┘         └──────────────┘         └─────────────┘
                              │                          │
                              │                          │
                              ▼                          ▼
                        ┌──────────────┐         ┌─────────────┐
                        │  Projection  │────────▶│ Read Model  │
                        │  (同期更新)   │         │(read_views) │
                        └──────────────┘         └─────────────┘
                                                         │
                                                         │
                        ┌─────────────┐                 │
                        │   Query     │◀────────────────┘
                        │   Handler   │
                        └─────────────┘
```

## Command（書き込み）の流れ

### 1. コマンドの受信

```rust
// main.rs から
let cmd = TodoCommand::CreateTodo {
    id: Uuid::new_v4(),
    title: "Buy milk".to_string(),
};
handle_command(&store, pool, cmd).await?;
```

### 2. 集約の復元

`command_handler.rs` の `handle_command` 関数で処理が開始されます：

```rust
// スナップショットから集約を復元
let mut todo = store.load_aggregate_with_snapshot(aggregate_id).await?;
```

**処理内容：**
1. 最新のスナップショットを取得（存在する場合）
2. スナップショットから集約の状態を復元
3. スナップショット以降のイベントを読み込む
4. イベントを順次適用して現在の状態を再構築

### 3. ビジネスロジックの実行

```rust
// コマンドを実行して新しいイベントを生成
let new_events = todo.execute(command)?;
```

**ドメインロジック（`domain/todo.rs`）:**
- `CreateTodo`: Todo が既に作成されていないかチェック → `TodoCreated` イベントを生成
- `ChangeTitle`: Todo が存在し、未完了かチェック → `TodoTitleChanged` イベントを生成
- `CompleteTodo`: Todo が存在し、未完了かチェック → `TodoCompleted` イベントを生成

### 4. イベントの永続化

```rust
// イベントを Event Store に保存
let final_sequence = store.append(aggregate_id, &new_events).await?;
```

**Event Store（`infrastructure/event_store.rs`）:**
- `events` テーブルにイベントを保存
- 各イベントには `aggregate_id`、`sequence`（シーケンス番号）、`event_type`、`payload`（JSON）が含まれる
- トランザクションで一括保存

### 5. プロジェクション（Read モデルの更新）

```rust
// 新しいイベントを適用
for event in &new_events {
    todo.apply(event);
}

// Read モデルを更新
upsert_todo_view(pool.as_ref(), todo.id, &todo.title, todo.completed, now).await?;
```

**プロジェクション（`infrastructure/read_model.rs`）:**
- `todo_read_views` テーブルを更新（INSERT ... ON CONFLICT DO UPDATE）
- クエリ用に最適化された構造で保存
- コマンド処理と同期して更新（同期プロジェクション）

### 6. スナップショットの作成（オプション）

```rust
// 100イベントごとにスナップショットを作成
if final_sequence > 0 && final_sequence % SNAPSHOT_INTERVAL == 0 {
    let snapshot = todo.to_snapshot(final_sequence);
    store.save_snapshot(aggregate_id, final_sequence, &snapshot).await?;
}
```

詳細は [snapshots.md](./snapshots.md) を参照してください。

## Query（読み込み）の流れ

### 1. クエリの受信

```rust
// main.rs から
let todos = list_all_todos(pool).await?;
```

### 2. Read モデルからの取得

```rust
// query_handler.rs または read_model.rs
let rows = sqlx::query_as::<_, (Uuid, String, bool, DateTime<Utc>)>(
    "SELECT id, title, completed, updated_at FROM todo_read_views ORDER BY updated_at DESC",
)
.fetch_all(pool.as_ref())
.await?;
```

**特徴：**
- Event Store を経由しない
- 最適化された `todo_read_views` テーブルから直接取得
- 高速な読み取りが可能

## データベーステーブル

### events テーブル（Write 側）

```sql
CREATE TABLE events (
  aggregate_id UUID NOT NULL,
  sequence BIGINT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (aggregate_id, sequence)
);
```

- **真実のソース**: すべての変更履歴が保存される
- **イミュータブル**: 一度保存されたイベントは変更されない
- **時系列順**: `sequence` で順序が保証される

### todo_read_views テーブル（Read 側）

```sql
CREATE TABLE todo_read_views (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMPTZ NOT NULL
);
```

- **プロジェクション結果**: イベントから生成された現在の状態
- **クエリ最適化**: インデックスを追加して高速化可能
- **同期更新**: コマンド処理時に自動更新

## メリット

### 1. 責務の分離

- **Write 側**: ビジネスロジックと整合性の保証に集中
- **Read 側**: クエリパフォーマンスの最適化に集中

### 2. スケーラビリティ

- Read と Write を独立してスケール可能
- 読み取りが多いシステムでは Read 側だけをスケールアウト

### 3. 柔軟性

- 複数の Read モデルを作成可能（検索用、レポート用など）
- イベントから再構築可能なので、後から Read モデルを追加できる

### 4. パフォーマンス

- Write 側: イベントの追加のみ（高速）
- Read 側: 最適化されたテーブル構造（高速）

## 実装のポイント

### 同期プロジェクション

このプロジェクトでは、コマンド処理と同時に Read モデルを更新しています（同期プロジェクション）。

**メリット：**
- 実装がシンプル
- 即座に Read モデルが更新される

**デメリット：**
- コマンド処理のレイテンシが増加する可能性
- プロジェクションの失敗がコマンド処理に影響する

**代替案：**
- 非同期プロジェクション（メッセージキューを使用）
- イベントソーサーから非同期で Read モデルを更新

### エラーハンドリング

- ドメインエラー: `TodoError`（ビジネスルール違反）
- Event Store エラー: `EventStoreError`（データベースエラー、シリアライゼーションエラー）
- Read Model エラー: `ReadModelError`（データベースエラー）

各エラーは適切に処理され、クライアントに返されます。

## まとめ

CQRS により、書き込みと読み込みを分離することで：

1. **ビジネスロジックの明確化**: Command 側でドメインロジックが明確になる
2. **パフォーマンスの向上**: Read 側を最適化できる
3. **スケーラビリティ**: 独立してスケール可能
4. **柔軟性**: 複数の Read モデルを作成可能

このプロジェクトでは、Event Sourcing と組み合わせることで、完全な変更履歴を保持しながら、高速な読み取りを実現しています。
