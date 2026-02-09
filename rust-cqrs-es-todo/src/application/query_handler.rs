use crate::infrastructure::{get_todo_by_id, list_todos, ReadModelError, TodoReadView};
use std::sync::Arc;
use uuid::Uuid;
use sqlx::PgPool;

/// 単体取得（Read 用 DB のみ参照）
pub async fn get_todo(pool: Arc<PgPool>, id: Uuid) -> Result<Option<TodoReadView>, ReadModelError> {
    get_todo_by_id(pool, id).await
}

/// 一覧取得（Read 用 DB のみ参照）
pub async fn list_all_todos(pool: Arc<PgPool>) -> Result<Vec<TodoReadView>, ReadModelError> {
    list_todos(pool).await
}
