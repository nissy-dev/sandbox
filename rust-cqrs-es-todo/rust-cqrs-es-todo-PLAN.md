# Rust CQRS + Event Sourcing + DDD Todo サンプル（PostgreSQL 採用）

## 方針

- **フレームワーク不使用**: `cqrs-es` 等は使わず、Aggregate・Event Store・Command/Query を自前でトレイトと型で表現する。
- **永続化**: **PostgreSQL** を Event 用・Read 用の両方に採用。クラスタ化・レプリケーションの拡張が可能。Rust からは **sqlx**（postgres ドライバ、生 SQL、ORM なし）で接続する。
- **DDD の用語をそのままコードに反映**: 集約（Aggregate）、ドメインイベント、コマンド、Event Store を明示的なモジュールで分ける。

## 永続化の選定（PostgreSQL で統一）

| 用途        | 選定                               | 備考                                                                                                     |
| ----------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Event 用 DB | **PostgreSQL**（`sqlx` postgres）  | 1 インスタンス内で **別スキーマ**（例: `events`）または専用テーブル。append-only テーブルで順序保証。    |
| Read 用 DB  | **PostgreSQL**（同一インスタンス） | 別スキーマ（例: `read_model`）または同一 DB 内の `todo_read_views` テーブル。プロジェクションで upsert。 |

- **接続**: 同一 PostgreSQL サーバーに 1 接続プール（`sqlx::PgPool`）で接続し、Event 用は `events` テーブル、Read 用は `todo_read_views` を参照する。必要ならスキーマを分けて `events.events` / `read_model.todo_read_views` とする。
- **ランタイム**: sqlx は非同期のため、CLI は `tokio` の `#[tokio::main]` で実行し、CommandHandler / QueryHandler は async で実装する。

## 使用するクレート

| 用途         | クレート                                                                 | 備考                                                          |
| ------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------- |
| シリアライズ | `serde`, `serde_json`                                                    | イベント・コマンドの直列化                                    |
| ID           | `uuid` (v4)                                                              | 集約 ID、イベント ID                                          |
| エラー       | `thiserror`                                                              | ドメインエラー・検証エラー                                    |
| DB           | `sqlx` (features: `runtime-tokio`, `postgres`, `uuid`, `chrono`, `json`) | 生 SQL、接続プール、マイグレーションはアプリ起動時 DDL でよい |
| 非同期       | `tokio` (features: `macros`)                                             | CLI のエントリ用                                              |

## 推奨ディレクトリ構成

```
sandbox/rust-cqrs-es-todo/
├── Cargo.toml
├── README.md
├── docker-compose.yml       # PostgreSQL 起動用（任意）
└── src/
    ├── main.rs              # #[tokio::main] CLI
    ├── lib.rs
    ├── domain/
    │   ├── mod.rs
    │   ├── todo.rs
    │   ├── events.rs
    │   └── commands.rs
    ├── application/
    │   ├── mod.rs
    │   ├── command_handler.rs
    │   └── query_handler.rs
    └── infrastructure/
        ├── mod.rs
        ├── event_store.rs   # EventStore トレイト + PostgresEventStore
        ├── read_model.rs    # todo_read_views の upsert/select（PgPool 使用）
        └── schema.rs        # CREATE TABLE（PostgreSQL 用 DDL）
```

- **接続先**: 環境変数 `DATABASE_URL`（例: `postgres://user:pass@localhost:5432/cqrs_todo`）で指定。README に Docker での起動例を記載する。

## Event 用テーブル（PostgreSQL）

- **スキーマ**: append-only。複合主キーで集約ごとの順序を保証。

```sql
CREATE TABLE IF NOT EXISTS events (
  aggregate_id UUID NOT NULL,
  sequence BIGINT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (aggregate_id, sequence)
);

CREATE INDEX IF NOT EXISTS idx_events_aggregate_id ON events(aggregate_id);
```

## Read 用テーブル（PostgreSQL）

```sql
CREATE TABLE IF NOT EXISTS todo_read_views (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_todo_read_views_completed ON todo_read_views(completed);
```

## 2 つのストアの関係

```mermaid
flowchart LR
  subgraph write [書き込み側]
    Command[Command]
    EventStore[(events)]
    Projection[Projection]
    ReadTable[(todo_read_views)]
    Command --> EventStore
    EventStore --> Projection
    Projection --> ReadTable
  end
  subgraph read [読み取り側]
    Query[Query]
    ReadTable
    Query --> ReadTable
  end
```

- 同一 PostgreSQL 内の **events** テーブル（真実のソース）と **todo_read_views** テーブル（プロジェクション結果）。クエリは `todo_read_views` のみ参照。

## ドメイン設計（変更なし）

- **集約ルート**: `Todo`（id, title, completed）
- **イベント**: `TodoCreated`, `TodoTitleChanged`, `TodoCompleted`
- **コマンド**: `CreateTodo`, `ChangeTitle`, `CompleteTodo`

## 実装のポイント

1. **EventStore トレイト**: `fn load_events(&self, aggregate_id: &Uuid) -> Result<Vec<Event>>`, `fn append(&self, aggregate_id: Uuid, events: &[Event]) -> Result<()>`。実装は `PostgresEventStore`（`PgPool` を保持し、`events` テーブルに INSERT / SELECT）。
2. **read_model.rs**: `PgPool` を受け、プロジェクション時に `todo_read_views` を INSERT ... ON CONFLICT (id) DO UPDATE。クエリ時に SELECT。
3. **起動時**: `DATABASE_URL` でプールを組み立て、`schema.rs` の DDL を 1 回実行（IF NOT EXISTS で冪等）。
4. **CLI**: `tokio::main` で async main、`create "title"`, `complete <id>`, `list` 等をパースして CommandHandler / QueryHandler を呼ぶ。

## 進め方の提案

1. **domain**: `events.rs`, `commands.rs`, `todo.rs` でイベント・コマンド・集約を定義し、`apply` / `execute` を実装。
2. **infrastructure**: `schema.rs` で PostgreSQL 用 DDL。`event_store.rs` で `EventStore` トレイト + `PostgresEventStore`。`read_model.rs` で `todo_read_views` の upsert/select。
3. **application**: `CommandHandler`（Event DB への append とプロジェクションで Read テーブル更新）、`QueryHandler`（Read テーブルのみ参照）を async で実装。
4. **main**: CLI からコマンド/クエリを呼び出し、動作確認。`docker-compose.yml` と README で PostgreSQL の起動方法を記載する。

## 補足

- **マイグレーション**: 専用クレートは使わず、起動時に上記 DDL を実行する形でよい。必要なら後から `sqlx migrate` を導入可能。
- **プロジェクション**: コマンドハンドラ内でイベントを append した直後に、そのイベント列を apply した結果で `todo_read_views` を upsert する同期プロジェクションで十分。
