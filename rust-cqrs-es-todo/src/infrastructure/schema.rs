use sqlx::PgPool;

/// 起動時に DDL を実行（冪等）
pub async fn run_migrations(pool: &PgPool) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS events (
          aggregate_id UUID NOT NULL,
          sequence BIGINT NOT NULL,
          event_type TEXT NOT NULL,
          payload JSONB NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          PRIMARY KEY (aggregate_id, sequence)
        );
        "#,
    )
    .execute(pool)
    .await?;

    sqlx::query("CREATE INDEX IF NOT EXISTS idx_events_aggregate_id ON events(aggregate_id);")
        .execute(pool)
        .await?;

    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS todo_read_views (
          id UUID PRIMARY KEY,
          title TEXT NOT NULL,
          completed BOOLEAN NOT NULL DEFAULT FALSE,
          updated_at TIMESTAMPTZ NOT NULL
        );
        "#,
    )
    .execute(pool)
    .await?;

    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_todo_read_views_completed ON todo_read_views(completed);",
    )
    .execute(pool)
    .await?;

    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS snapshots (
          aggregate_id UUID NOT NULL,
          sequence BIGINT NOT NULL,
          aggregate_type TEXT NOT NULL,
          state JSONB NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          PRIMARY KEY (aggregate_id, sequence)
        );
        "#,
    )
    .execute(pool)
    .await?;

    sqlx::query(
        "CREATE INDEX IF NOT EXISTS idx_snapshots_latest ON snapshots(aggregate_id, sequence DESC);",
    )
    .execute(pool)
    .await?;

    Ok(())
}
