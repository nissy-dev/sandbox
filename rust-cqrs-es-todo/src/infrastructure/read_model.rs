use chrono::{DateTime, Utc};
use sqlx::PgPool;
use std::sync::Arc;
use uuid::Uuid;

/// クエリ用 Todo ビュー
#[derive(Debug, Clone)]
pub struct TodoReadView {
    pub id: Uuid,
    pub title: String,
    pub completed: bool,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, thiserror::Error)]
pub enum ReadModelError {
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),
}

/// プロジェクション: todo_read_views を upsert
pub async fn upsert_todo_view(
    pool: &PgPool,
    id: Uuid,
    title: &str,
    completed: bool,
    updated_at: DateTime<Utc>,
) -> Result<(), ReadModelError> {
    sqlx::query(
        r#"
        INSERT INTO todo_read_views (id, title, completed, updated_at)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (id) DO UPDATE SET
          title = EXCLUDED.title,
          completed = EXCLUDED.completed,
          updated_at = EXCLUDED.updated_at
        "#,
    )
    .bind(id)
    .bind(title)
    .bind(completed)
    .bind(updated_at)
    .execute(pool)
    .await?;
    Ok(())
}

/// 単体取得
pub async fn get_todo_by_id(
    pool: Arc<PgPool>,
    id: Uuid,
) -> Result<Option<TodoReadView>, ReadModelError> {
    let row = sqlx::query_as::<_, (Uuid, String, bool, DateTime<Utc>)>(
        "SELECT id, title, completed, updated_at FROM todo_read_views WHERE id = $1",
    )
    .bind(id)
    .fetch_optional(pool.as_ref())
    .await?;

    Ok(row.map(|(id, title, completed, updated_at)| TodoReadView {
        id,
        title,
        completed,
        updated_at,
    }))
}

/// 一覧取得（全件）
pub async fn list_todos(pool: Arc<PgPool>) -> Result<Vec<TodoReadView>, ReadModelError> {
    let rows = sqlx::query_as::<_, (Uuid, String, bool, DateTime<Utc>)>(
        "SELECT id, title, completed, updated_at FROM todo_read_views ORDER BY updated_at DESC",
    )
    .fetch_all(pool.as_ref())
    .await?;

    Ok(rows
        .into_iter()
        .map(|(id, title, completed, updated_at)| TodoReadView {
            id,
            title,
            completed,
            updated_at,
        })
        .collect())
}
