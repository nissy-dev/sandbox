use crate::domain::{TodoCommand, TodoError};
use crate::infrastructure::{EventStore, EventStoreError, PostgresEventStore, ReadModelError, upsert_todo_view};
use chrono::Utc;
use std::sync::Arc;
use sqlx::PgPool;

/// スナップショットを作成する間隔（イベント数）
const SNAPSHOT_INTERVAL: i64 = 100;

#[derive(Debug, thiserror::Error)]
pub enum CommandHandlerError {
    #[error("domain error: {0}")]
    Domain(#[from] TodoError),
    #[error("event store error: {0}")]
    EventStore(#[from] EventStoreError),
    #[error("read model error: {0}")]
    ReadModel(#[from] ReadModelError),
}

/// コマンドを処理: スナップショットから集約を復元し、イベントを Event Store に append し、プロジェクションで Read テーブルを更新
pub async fn handle_command(
    store: &PostgresEventStore,
    pool: Arc<PgPool>,
    command: TodoCommand,
) -> Result<(), CommandHandlerError> {
    let aggregate_id = command.aggregate_id();
    
    // スナップショットから集約を復元（スナップショットがない場合は空の集約から開始）
    let mut todo = store.load_aggregate_with_snapshot(aggregate_id).await?;

    // コマンドを実行して新しいイベントを生成
    let new_events = todo.execute(command)?;
    if new_events.is_empty() {
        return Ok(());
    }

    // イベントを保存し、最終的なシーケンス番号を取得
    let final_sequence = store.append(aggregate_id, &new_events).await?;

    // 新しいイベントを適用して集約の状態を更新
    for event in &new_events {
        todo.apply(event);
    }

    // スナップショット作成条件: SNAPSHOT_INTERVAL ごと（例：100イベントごと）
    if final_sequence > 0 && final_sequence % SNAPSHOT_INTERVAL == 0 {
        let snapshot = todo.to_snapshot(final_sequence);
        if let Err(e) = store.save_snapshot(aggregate_id, final_sequence, &snapshot).await {
            // スナップショット保存の失敗は警告のみ（コマンド処理は続行）
            eprintln!("Warning: Failed to save snapshot: {}", e);
        }
    }

    // プロジェクション: 新しいイベントを apply した状態で todo_read_views を upsert
    let now = Utc::now();
    upsert_todo_view(
        pool.as_ref(),
        todo.id,
        &todo.title,
        todo.completed,
        now,
    )
    .await?;

    Ok(())
}
