# スナップショット機能

このドキュメントでは、Event Sourcing におけるスナップショット機能の実装と動作について解説します。

## スナップショットとは

スナップショットは、集約の**特定時点での状態**を保存したものです。Event Sourcing では、すべての変更がイベントとして保存されるため、集約を復元するには全イベントを読み込んで適用する必要があります。

**問題点：**
- イベント数が増えると、復元処理が遅くなる
- メモリ使用量が増加する
- データベースの読み込み負荷が増加する

**解決策：**
- 定期的にスナップショットを作成
- スナップショットから復元を開始し、その後のイベントのみを適用

## スナップショットの構造

### TodoSnapshot

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TodoSnapshot {
    pub id: Uuid,
    pub title: String,
    pub completed: bool,
    pub version: i64, // イベントのシーケンス番号
}
```

スナップショットには以下が含まれます：
- **集約の状態**: 現在の id, title, completed
- **バージョン**: どのイベントまで適用したかを示すシーケンス番号

## データベーススキーマ

### snapshots テーブル

```sql
CREATE TABLE snapshots (
  aggregate_id UUID NOT NULL,
  sequence BIGINT NOT NULL,
  aggregate_type TEXT NOT NULL,
  state JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (aggregate_id, sequence)
);

CREATE INDEX idx_snapshots_latest 
ON snapshots(aggregate_id, sequence DESC);
```

**特徴：**
- `aggregate_id` と `sequence` の複合主キー
- `state` は JSONB 形式で集約の状態を保存
- 最新のスナップショットを高速に取得するためのインデックス

## スナップショットの作成

### 作成タイミング

このプロジェクトでは、**100イベントごと**に自動でスナップショットを作成します。

```rust
// command_handler.rs
const SNAPSHOT_INTERVAL: i64 = 100;

// スナップショット作成条件
if final_sequence > 0 && final_sequence % SNAPSHOT_INTERVAL == 0 {
    let snapshot = todo.to_snapshot(final_sequence);
    store.save_snapshot(aggregate_id, final_sequence, &snapshot).await?;
}
```

**作成条件：**
- イベントのシーケンス番号が 100 の倍数のとき
- 例: 100, 200, 300, 400, ...

### 作成処理の流れ

1. **コマンド実行**: 新しいイベントが生成される
2. **イベント保存**: Event Store にイベントを保存
3. **状態更新**: イベントを適用して集約の状態を更新
4. **スナップショット作成**: 条件を満たす場合、現在の状態をスナップショットとして保存

```rust
// event_store.rs
async fn save_snapshot(
    &self,
    aggregate_id: Uuid,
    sequence: i64,
    snapshot: &TodoSnapshot,
) -> Result<(), EventStoreError> {
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
```

## スナップショットからの復元

### 復元処理の流れ

```rust
// event_store.rs
async fn load_aggregate_with_snapshot(
    &self,
    aggregate_id: Uuid,
) -> Result<Todo, EventStoreError> {
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
```

### 処理ステップ

1. **スナップショット取得**: 最新のスナップショットを取得
2. **状態復元**: スナップショットから集約の状態を復元
3. **イベント読み込み**: スナップショット以降のイベントのみを読み込む
4. **イベント適用**: 読み込んだイベントを順次適用して最新の状態に更新

### 例：イベント数が 250 の場合

```
イベント: [1, 2, 3, ..., 100, 101, ..., 200, 201, ..., 250]
スナップショット: [100, 200]

復元処理:
1. スナップショット 200 を取得（sequence=200 の状態）
2. イベント 201-250 を読み込む（50個）
3. イベント 201-250 を適用

結果: 全250個のイベントを読み込む代わりに、50個のイベントのみを読み込む
```

## パフォーマンスの改善

### 改善前（スナップショットなし）

```
イベント数: 1000
読み込むイベント数: 1000
処理時間: O(n) - イベント数に比例
```

### 改善後（スナップショットあり）

```
イベント数: 1000
スナップショット: sequence=1000
読み込むイベント数: 0（スナップショットのみ）
処理時間: O(1) - ほぼ定数時間
```

### 中間的なケース

```
イベント数: 1050
スナップショット: sequence=1000
読み込むイベント数: 50（1001-1050）
処理時間: O(m) - m はスナップショット以降のイベント数
```

**最大読み込みイベント数**: `SNAPSHOT_INTERVAL - 1`（このプロジェクトでは最大99個）

## スナップショットの管理

### 古いスナップショットの削除

スナップショットも蓄積されるため、定期的にクリーンアップすることを推奨します。

```sql
-- 最新の2個以外のスナップショットを削除
DELETE FROM snapshots
WHERE (aggregate_id, sequence) NOT IN (
    SELECT aggregate_id, sequence
    FROM (
        SELECT aggregate_id, sequence,
               ROW_NUMBER() OVER (PARTITION BY aggregate_id ORDER BY sequence DESC) as rn
        FROM snapshots
    ) ranked
    WHERE rn <= 2
);
```

**保持戦略：**
- 最新の N 個のスナップショットを保持（例: 2-3個）
- 古いスナップショットは削除またはアーカイブ

### スナップショット作成の失敗

スナップショット作成に失敗しても、コマンド処理は継続されます：

```rust
if let Err(e) = store.save_snapshot(aggregate_id, final_sequence, &snapshot).await {
    // スナップショット保存の失敗は警告のみ（コマンド処理は続行）
    eprintln!("Warning: Failed to save snapshot: {}", e);
}
```

**理由：**
- スナップショットは最適化のための機能
- イベントは既に保存されているため、次回の復元時に再作成可能

## スナップショット間隔の調整

`SNAPSHOT_INTERVAL` を調整することで、スナップショットの作成頻度を変更できます。

```rust
// command_handler.rs
const SNAPSHOT_INTERVAL: i64 = 100; // 100イベントごと
```

**考慮事項：**

1. **小さな値（例: 10）**
   - メリット: 復元が高速
   - デメリット: スナップショットが多く作成される（ストレージ使用量増加）

2. **大きな値（例: 1000）**
   - メリット: ストレージ使用量が少ない
   - デメリット: 復元時に多くのイベントを読み込む必要がある

3. **推奨値**
   - 一般的には 50-200 の範囲が推奨
   - このプロジェクトでは 100 を使用

## まとめ

スナップショット機能により：

1. **パフォーマンス向上**: 集約の復元が高速化される
2. **スケーラビリティ**: イベント数が増えても性能が維持される
3. **メモリ効率**: 読み込むイベント数が削減される
4. **柔軟性**: 間隔を調整して最適化可能

Event Sourcing の長所（完全な変更履歴）を保ちながら、パフォーマンスの問題を解決する重要な機能です。
