# Go Concurrency Patterns

Go における並行処理パターンの比較学習用プロジェクト。

## 3 つのアプローチ

### 1. Mutex (相互排他ロック)

```go
type MutexCounter struct {
    mu    sync.Mutex
    value int
}

func (c *MutexCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}
```

**メリット:**

- シンプルで理解しやすい
- パフォーマンスが良い（オーバーヘッドが少ない）

**デメリット:**

- デッドロックのリスク（複数のロックを取得する順序に注意が必要）
- ロックの粒度を適切に設計する必要がある
- 状態が共有されるため、バグが発生しやすい

---

### 2. Channel

```go
type ChannelCounter struct {
    ch    chan func()
    value int
}

func (c *ChannelCounter) Increment() {
    done := make(chan struct{})
    c.ch <- func() {
        c.value++
        close(done)
    }
    <-done
}
```

**メリット:**

- Go らしいアプローチ（"Don't communicate by sharing memory; share memory by communicating"）
- 明示的なロックが不要
- select と組み合わせてタイムアウトやキャンセルが簡単

**デメリット:**

- Mutex より若干オーバーヘッドがある
- チャネルのデッドロック（送信側・受信側の不一致）に注意

---

### 3. Actor Model

```go
type CounterActor struct {
    actor *Actor
}

func (c *CounterActor) Increment() {
    c.actor.Send(IncrementMsg{})
}
```

**メリット:**

- 状態の完全なカプセル化
- メッセージパッシングによる疎結合
- スケーラビリティが高い（分散システムにも適用可能）
- Erlang/Akka のような堅牢な並行処理モデル

**デメリット:**

- 実装が複雑
- メッセージの型定義が必要
- オーバーヘッドがある

---

## 実行方法

```bash
go run main.go
```

## 出力例

```
=== Go Concurrency Patterns Comparison ===

1. Mutex-based Counter
  Final value: 1000 (expected: 1000)
  Time: 1.234ms

2. Channel-based Counter
  Final value: 1000 (expected: 1000)
  Time: 2.345ms

3. Actor Model Counter
  Final value: 1000 (expected: 1000)
  Time: 1.567ms
```

## 使い分けの指針

| パターン | 適したケース                           |
| -------- | -------------------------------------- |
| Mutex    | シンプルな共有状態、パフォーマンス重視 |
| Channel  | Goroutine 間の通信、タイムアウト処理   |
| Actor    | 複雑な状態管理、分散システム、障害耐性 |

## 参考

- [Go Concurrency Patterns](https://go.dev/blog/pipelines)
- [Share Memory By Communicating](https://go.dev/blog/codelab-share)
- [The Actor Model](https://www.brianstorti.com/the-actor-model/)
