use std::{
    collections::HashMap,
    future::Future,
    mem,
    pin::Pin,
    sync::{
        mpsc::{channel, Sender},
        Arc, Mutex,
    },
    task::{Context, Poll, RawWaker, RawWakerVTable, Waker},
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};

// executer
fn block_on<F: Future>(mut future: F) -> F::Output {
    // reactor と executer とのやり取りを担う waker を作成する
    let mywaker = Arc::new(MyWaker {
        thread: thread::current(),
    });
    let waker = mywaker_into_waker(Arc::into_raw(mywaker));

    // waker は context 経由で reactor に渡される
    let mut cx = Context::from_waker(&waker);

    // Rust では、一般的に非同期処理をハンドルする際に generator と同様の実装方針をとる
    // この際に、future は自己参照を持つことになるが、pin することで安全に参照を保持できる
    let mut future = unsafe { Pin::new_unchecked(&mut future) };

    // future を poll し、完了するまでループする
    let val = loop {
        match Future::poll(future.as_mut(), &mut cx) {
            Poll::Ready(val) => break val,
            // pending のときは、thread::park でスレッドをブロックする
            Poll::Pending => thread::park(),
        };
    };
    val
}

#[derive(Debug)]
struct MyWaker {
    thread: thread::Thread,
}

fn mywaker_wake(s: &MyWaker) {
    let waker_ptr: *const MyWaker = s;
    let waker_arc = unsafe { Arc::from_raw(waker_ptr) };
    // block しているスレッドを再開する
    waker_arc.thread.unpark();
}

const VTABLE: RawWakerVTable = unsafe {
    RawWakerVTable::new(
        |s| mywaker_clone(&*(s as *const MyWaker)),   // clone
        |s| mywaker_wake(&*(s as *const MyWaker)),    // wake
        |s| (*(s as *const MyWaker)).thread.unpark(), // wake by ref (don't decrease refcount)
        |s| drop(Arc::from_raw(s as *const MyWaker)), // decrease refcount
    )
};

fn mywaker_clone(s: &MyWaker) -> RawWaker {
    let arc = unsafe { Arc::from_raw(s) };
    std::mem::forget(arc.clone()); // increase ref count
    RawWaker::new(Arc::into_raw(arc) as *const (), &VTABLE)
}

fn mywaker_into_waker(s: *const MyWaker) -> Waker {
    let raw_waker = RawWaker::new(s as *const (), &VTABLE);
    unsafe { Waker::from_raw(raw_waker) }
}

#[derive(Clone)]
struct Task {
    id: usize,
    reactor: Arc<Mutex<Box<Reactor>>>,
    data: u64,
}

impl Task {
    fn new(reactor: Arc<Mutex<Box<Reactor>>>, data: u64, id: usize) -> Self {
        Task { id, reactor, data }
    }
}

impl Future for Task {
    type Output = usize;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let mut r = self.reactor.lock().unwrap();

        if r.is_ready(self.id) {
            *r.tasks.get_mut(&self.id).unwrap() = TaskState::Finished;
            Poll::Ready(self.id)
        } else if r.tasks.contains_key(&self.id) {
            // １つ前の poll の処理が終わる前に、再び poll が呼ばれる場合をケアしている
            // それぞれの Future に対応する state は常に最新になるようにしている
            // 古い context に対応する waker は drop されているかもしれない
            r.tasks
                .insert(self.id, TaskState::NotReady(cx.waker().clone()));
            Poll::Pending
        } else {
            r.register(self.data, cx.waker().clone(), self.id);
            Poll::Pending
        }
    }
}

enum TaskState {
    Finished,
    NotReady(Waker),
    Ready,
}

#[derive(Debug)]
enum Event {
    Close,
    Timeout(u64, usize),
}

struct Reactor {
    dispatcher: Sender<Event>,
    handle: Option<JoinHandle<()>>,
    tasks: HashMap<usize, TaskState>,
}

impl Reactor {
    fn new() -> Arc<Mutex<Box<Self>>> {
        let (tx, rx) = channel::<Event>();
        let reactor = Arc::new(Mutex::new(Box::new(Reactor {
            dispatcher: tx,
            handle: None,
            tasks: HashMap::new(),
        })));

        let reactor_clone = Arc::downgrade(&reactor);

        // Reactorの処理のスレッドを作成する
        let handle = thread::spawn(move || {
            let mut handles = vec![];

            for event in rx {
                println!("REACTOR: {:?}", event);
                let reactor = reactor_clone.clone();
                match event {
                    Event::Close => break,
                    Event::Timeout(duration, id) => {
                        // timer の実装
                        let event_handle = thread::spawn(move || {
                            thread::sleep(Duration::from_secs(duration));
                            let reactor = reactor.upgrade().unwrap();
                            reactor.lock().map(|mut r| r.wake(id)).unwrap();
                        });
                        handles.push(event_handle);
                    }
                }
            }
            handles
                .into_iter()
                .for_each(|handle| handle.join().unwrap());
        });
        reactor.lock().map(|mut r| r.handle = Some(handle)).unwrap();
        reactor
    }

    fn register(&mut self, duration: u64, waker: Waker, id: usize) {
        if self.tasks.insert(id, TaskState::NotReady(waker)).is_some() {
            panic!("Tried to insert a task with id: '{}', twice!", id);
        }
        self.dispatcher.send(Event::Timeout(duration, id)).unwrap();
    }

    fn is_ready(&self, id: usize) -> bool {
        self.tasks
            .get(&id)
            .map(|state| match state {
                TaskState::Ready => true,
                _ => false,
            })
            .unwrap_or(false)
    }

    fn wake(&mut self, id: usize) {
        self.tasks
            .get_mut(&id)
            .map(|state| {
                // state を Ready に入れ替えて、NotReady だった場合は wake を呼び出す
                match mem::replace(state, TaskState::Ready) {
                    TaskState::NotReady(waker) => waker.wake(),
                    TaskState::Finished => panic!("Called 'wake' twice on task: {}", id),
                    _ => unreachable!(),
                }
            })
            .unwrap();
    }
}

impl Drop for Reactor {
    fn drop(&mut self) {
        // reactor が drop されるときに、reactor のスレッドも停止させる
        self.dispatcher.send(Event::Close).unwrap();
        self.handle.take().map(|h| h.join().unwrap()).unwrap();
    }
}

// 実装したランタイムを動かしてみる
fn main() {
    let start = Instant::now();
    let reactor = Reactor::new();

    let future1 = Task::new(reactor.clone(), 1, 1);
    let future2 = Task::new(reactor.clone(), 2, 2);

    let fut1 = async {
        let val = future1.await;
        println!("Got {} at time: {:.2}.", val, start.elapsed().as_secs_f32());
    };
    let fut2 = async {
        let val = future2.await;
        println!("Got {} at time: {:.2}.", val, start.elapsed().as_secs_f32());
    };

    let mainfut = async {
        fut1.await;
        fut2.await;
    };

    block_on(mainfut);
}
