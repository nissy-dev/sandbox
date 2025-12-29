package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	fmt.Println("=== Go Concurrency Patterns Comparison ===")

	// 1. Mutex を使った実装
	fmt.Println("1. Mutex-based Counter")
	runMutexCounter()

	// 2. Channel を使った実装
	fmt.Println("2. Channel-based Counter")
	runChannelCounter()

	// 3. Actor Model を使った実装
	fmt.Println("3. Actor Model Counter")
	runActorCounter()
}

// ============================================================
// 1. Mutex を使った実装
// ============================================================
// シンプルだが、ロックの粒度や順序に注意が必要
// デッドロックのリスクがある

type MutexCounter struct {
	mu    sync.Mutex
	value int
}

func (c *MutexCounter) Increment() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value++
}

func (c *MutexCounter) Decrement() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value--
}

func (c *MutexCounter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}

func runMutexCounter() {
	counter := &MutexCounter{}
	var wg sync.WaitGroup

	start := time.Now()

	// 1000個のgoroutineで同時にインクリメント
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Increment()
		}()
	}

	wg.Wait()
	elapsed := time.Since(start)

	fmt.Printf("  Final value: %d (expected: 1000)\n", counter.Value())
	fmt.Printf("  Time: %v\n", elapsed)
}

// ============================================================
// 2. Channel を使った実装
// ============================================================
// Go らしいアプローチ。"Don't communicate by sharing memory; share memory by communicating"
// 明示的なロックが不要

type ChannelCounter struct {
	// channel は FIFO キューなので、レースコンディションは発生しない
	ch    chan func()
	value int
}

func NewChannelCounter() *ChannelCounter {
	c := &ChannelCounter{
		ch: make(chan func()),
	}
	go c.run()
	return c
}

func (c *ChannelCounter) run() {
	for fn := range c.ch {
		fn()
	}
}

func (c *ChannelCounter) Increment() {
	done := make(chan struct{})
	c.ch <- func() {
		c.value++
		close(done)
	}
	<-done
}

func (c *ChannelCounter) Decrement() {
	done := make(chan struct{})
	c.ch <- func() {
		c.value--
		close(done)
	}
	<-done
}

func (c *ChannelCounter) Value() int {
	result := make(chan int)
	c.ch <- func() {
		result <- c.value
	}
	return <-result
}

func (c *ChannelCounter) Close() {
	close(c.ch)
}

func runChannelCounter() {
	counter := NewChannelCounter()
	var wg sync.WaitGroup

	start := time.Now()

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Increment()
		}()
	}

	wg.Wait()
	elapsed := time.Since(start)

	fmt.Printf("  Final value: %d (expected: 1000)\n", counter.Value())
	fmt.Printf("  Time: %v\n", elapsed)

	counter.Close()
}

// ============================================================
// 3. Actor Model を使った実装
// ============================================================
// 各Actorは独自の状態を持ち、メッセージを通じてのみ通信
// Erlang/Akka スタイル

// Message は Actor に送信するメッセージの型
type Message interface{}

// IncrementMsg はインクリメントを要求するメッセージ
type IncrementMsg struct{}

// DecrementMsg はデクリメントを要求するメッセージ
type DecrementMsg struct{}

// GetValueMsg は現在の値を取得するメッセージ
type GetValueMsg struct {
	Reply chan int
}

// StopMsg は Actor を停止するメッセージ
type StopMsg struct{}

// Actor はメッセージを受け取って処理する
type Actor struct {
	mailbox chan Message
}

// NewActor は新しい Actor を作成
func NewActor(handler func(msg Message) bool) *Actor {
	a := &Actor{
		mailbox: make(chan Message, 100), // バッファ付きチャネル
	}
	go func() {
		// mailbox が close するまではメッセージを処理し続ける
		for msg := range a.mailbox {
			if !handler(msg) {
				break
			}
		}
	}()
	return a
}

// Send は Actor にメッセージを送信
func (a *Actor) Send(msg Message) {
	a.mailbox <- msg
}

// CounterActor は Counter の Actor 実装
type CounterActor struct {
	actor *Actor
}

func NewCounterActor() *CounterActor {
	var value int

	handler := func(msg Message) bool {
		switch m := msg.(type) {
		case IncrementMsg:
			value++
		case DecrementMsg:
			value--
		case GetValueMsg:
			m.Reply <- value
		case StopMsg:
			return false
		}
		return true
	}

	return &CounterActor{
		actor: NewActor(handler),
	}
}

func (c *CounterActor) Increment() {
	c.actor.Send(IncrementMsg{})
}

func (c *CounterActor) Decrement() {
	c.actor.Send(DecrementMsg{})
}

func (c *CounterActor) Value() int {
	reply := make(chan int)
	c.actor.Send(GetValueMsg{Reply: reply})
	return <-reply
}

func (c *CounterActor) Stop() {
	c.actor.Send(StopMsg{})
}

func runActorCounter() {
	counter := NewCounterActor()
	var wg sync.WaitGroup

	start := time.Now()

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Increment()
		}()
	}

	wg.Wait()

	// Actor の mailbox が処理されるのを少し待つ
	time.Sleep(10 * time.Millisecond)

	elapsed := time.Since(start)

	fmt.Printf("  Final value: %d (expected: 1000)\n", counter.Value())
	fmt.Printf("  Time: %v\n", elapsed)

	counter.Stop()
}
