package main

import (
	"container/heap"
	"fmt"
	"math/rand"
	"time"
)

const nWorker = 10
const nRequester = 15

type Request struct {
	fn func() int // The operation to perform.
	c  chan int   // The channel to return the result.
}

func operation() int {
	n := rand.Int63n(10)
	time.Sleep(time.Duration(nWorker * n))
	return int(n)
}

// Request を送信し、結果を受信する
func requester(work chan<- Request, i int) {
	c := make(chan int)
	for {
		time.Sleep(time.Duration(rand.Int63n(int64(nWorker * 2 * time.Second))))
		work <- Request{operation, c}
		result := <-c
		fmt.Printf("Request %v, Result %v\n", i, result)
	}
}

type Worker struct {
	requests chan Request
	pending  int
	index    int
}

// Request を受信し処理を行い、処理の完了を通知する
func (w *Worker) work(done chan *Worker) {
	for {
		req := <-w.requests
		req.c <- req.fn()
		done <- w
	}
}

type Pool []*Worker

func (p Pool) Len() int { return len(p) }

func (p Pool) Less(i, j int) bool {
	return p[i].pending < p[j].pending
}

func (p Pool) Swap(i, j int) {
	p[i], p[j] = p[j], p[i]
	p[i].index = i
	p[j].index = j
}

func (p *Pool) Pop() any {
	old := *p
	n := len(old)
	item := old[n-1]
	old[n-1] = nil  // don't stop the GC from reclaiming the item eventually
	item.index = -1 // for safety
	*p = old[0 : n-1]
	return item
}

func (p *Pool) Push(x any) {
	n := len(*p)
	item := x.(*Worker)
	item.index = n
	*p = append(*p, item)
}

type Balancer struct {
	pool Pool
	done chan *Worker
}

// Requester と Worker の橋渡しを行う (これがまさにロードバランサー)
func (b *Balancer) balance(work chan Request) {
	for {
		select {
		case req := <-work: // requester から request が来た場合
			b.dispatch(req)
		case w := <-b.done: // worker から処理が終わった通知が来た場合
			b.completed(w)
		}
	}
}

// Worker へ request を送信する
func (b *Balancer) dispatch(req Request) {
	w := heap.Pop(&b.pool).(*Worker)
	w.requests <- req
	w.pending++
	heap.Push(&b.pool, w)
}

// 処理で利用した Worker の初期化
func (b *Balancer) completed(w *Worker) {
	w.pending--
	heap.Remove(&b.pool, w.index)
	heap.Push(&b.pool, w)
}

func main() {
	work := make(chan Request)
	for i := 0; i < nRequester; i++ {
		go requester(work, i+1)
	}

	done := make(chan *Worker, nWorker)
	b := &Balancer{make(Pool, 0, nWorker), done}
	for i := 0; i < nWorker; i++ {
		w := &Worker{requests: make(chan Request, nRequester)}
		heap.Push(&b.pool, w)
		go w.work(b.done)
	}
	b.balance(work)
}
