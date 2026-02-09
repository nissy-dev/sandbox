use crate::domain::{Todo, TodoEvent, TodoSnapshot};
use async_trait::async_trait;
use sqlx::PgPool;
use std::sync::Arc;
use uuid::Uuid;

/// Event Store トレイト
#[async_trait]
pub trait EventStore: Send + Sync {
    async fn load_events(&self, aggregate_id: Uuid) -> Result<Vec<TodoEvent>, EventStoreError>;
    async fn append(&self, aggregate_id: Uuid, events: &[TodoEvent]) -> Result<i64, EventStoreError>;
    async fn load_aggregate_with_snapshot(&self, aggregate_id: Uuid) -> Result<Todo, EventStoreError>;
    async fn save_snapshot(&self, aggregate_id: Uuid, sequence: i64, snapshot: &TodoSnapshot) -> Result<(), EventStoreError>;
}

#[derive(Debug, thiserror::Error)]
pub enum EventStoreError {
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),
    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}

/// PostgreSQL による Event Store 実装
pub struct PostgresEventStore {
    pool: Arc<PgPool>,
}

impl PostgresEventStore {
    pub fn new(pool: Arc<PgPool>) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl EventStore for PostgresEventStore {
    async fn load_events(&self, aggregate_id: Uuid) -> Result<Vec<TodoEvent>, EventStoreError> {
        let rows = sqlx::query_as::<_, (i64, String, serde_json::Value)>(
            "SELECT sequence, event_type, payload FROM events WHERE aggregate_id = $1 ORDER BY sequence",
        )
        .bind(aggregate_id)
        .fetch_all(self.pool.as_ref())
        .await?;

        let mut result = Vec::with_capacity(rows.len());
        for (_seq, event_type, payload) in rows {
            let event: TodoEvent = serde_json::from_value(payload)?;
            result.push(event);
        }
        Ok(result)
    }

    async fn append(&self, aggregate_id: Uuid, events: &[TodoEvent]) -> Result<i64, EventStoreError> {
        if events.is_empty() {
            // 既存のイベントがない場合は0を返す
            let max_seq: Option<i64> = sqlx::query_scalar(
                "SELECT MAX(sequence) FROM events WHERE aggregate_id = $1",
            )
            .bind(aggregate_id)
            .fetch_optional(self.pool.as_ref())
            .await?;
            return Ok(max_seq.unwrap_or(0));
        }

        let mut tx = self.pool.begin().await?;
        let next_seq: Option<i64> = sqlx::query_scalar(
            "SELECT COALESCE(MAX(sequence), 0) + 1 FROM events WHERE aggregate_id = $1",
        )
        .bind(aggregate_id)
        .fetch_optional(&mut *tx)
        .await?;

        let start_seq = next_seq.unwrap_or(1);
        let mut last_seq = start_seq;

        for (i, event) in events.iter().enumerate() {
            let sequence = start_seq + i as i64;
            last_seq = sequence;
            let event_type = event.type_name();
            let payload = serde_json::to_value(event)?;

            sqlx::query(
                "INSERT INTO events (aggregate_id, sequence, event_type, payload, created_at) VALUES ($1, $2, $3, $4, NOW())",
            )
            .bind(aggregate_id)
            .bind(sequence)
            .bind(event_type)
            .bind(payload)
            .execute(&mut *tx)
            .await?;
        }

        tx.commit().await?;
        Ok(last_seq)
    }

    async fn load_aggregate_with_snapshot(&self, aggregate_id: Uuid) -> Result<Todo, EventStoreError> {
        // 1. 最新のスナップショットを取得
        let snapshot_row = sqlx::query_as::<_, (i64, serde_json::Value)>(
            r#"
            SELECT sequence, state
            FROM snapshots
            WHERE aggregate_id = $1
            ORDER BY sequence DESC
            LIMIT 1
            "#
        )
        .bind(aggregate_id)
        .fetch_optional(self.pool.as_ref())
        .await?;

        let (mut todo, start_sequence) = match snapshot_row {
            Some((seq, state)) => {
                // スナップショットから復元
                let snapshot: TodoSnapshot = serde_json::from_value(state)?;
                let todo = Todo::from_snapshot(snapshot);
                (todo, seq + 1) // スナップショット以降のイベントから読み込む
            }
            None => {
                // スナップショットがない場合は空の集約から開始
                (Todo::new_empty(aggregate_id), 0)
            }
        };

        // 2. スナップショット以降のイベントを読み込む
        let event_rows = sqlx::query_as::<_, (i64, serde_json::Value)>(
            r#"
            SELECT sequence, payload
            FROM events
            WHERE aggregate_id = $1 AND sequence >= $2
            ORDER BY sequence
            "#
        )
        .bind(aggregate_id)
        .bind(start_sequence)
        .fetch_all(self.pool.as_ref())
        .await?;

        // 3. イベントを適用
        for (_seq, payload) in event_rows {
            let event: TodoEvent = serde_json::from_value(payload)?;
            todo.apply(&event);
        }

        Ok(todo)
    }

    async fn save_snapshot(&self, aggregate_id: Uuid, sequence: i64, snapshot: &TodoSnapshot) -> Result<(), EventStoreError> {
        let state_json = serde_json::to_value(snapshot)?;

        sqlx::query(
            r#"
            INSERT INTO snapshots (aggregate_id, sequence, aggregate_type, state, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (aggregate_id, sequence) DO NOTHING
            "#
        )
        .bind(aggregate_id)
        .bind(sequence)
        .bind("Todo")
        .bind(state_json)
        .execute(self.pool.as_ref())
        .await?;

        Ok(())
    }
}
