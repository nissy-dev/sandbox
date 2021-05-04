use std::sync::mpsc;
use std::sync::Arc;
use std::sync::Mutex;
use std::thread;

pub struct ThreadPool {
  workers: Vec<Worker>,
  sender: mpsc::Sender<Message>,
}

impl ThreadPool {
  /// 新しいThreadPoolを生成する。
  ///
  /// sizeがプールのスレッド数です。
  ///
  /// # パニック
  ///
  /// sizeが0なら、`new`関数はパニックします。
  ///
  /// Create a new ThreadPool.
  ///
  /// The size is the number of threads in the pool.
  ///
  /// # Panics
  ///
  /// The `new` function will panic if the size is zero.
  pub fn new(size: usize) -> ThreadPool {
    assert!(size > 0);
    let (sender, receiver) = mpsc::channel();
    let receiver = Arc::new(Mutex::new(receiver));
    let mut workers = Vec::with_capacity(size);

    for id in 0..size {
      // ワーカーを経由してスレッドを生成し、ベクタに格納する
      workers.push(Worker::new(id, Arc::clone(&receiver)));
    }

    ThreadPool { workers, sender }
  }

  pub fn execute<F>(&self, f: F)
  where
    F: FnOnce() + Send + 'static,
  {
    let job = Box::new(f);
    self.sender.send(Message::NewJob(job)).unwrap();
  }
}

trait FnBox {
  // selfの所有権を奪う
  fn call_box(self: Box<Self>);
}

impl<F: FnOnce()> FnBox for F {
  fn call_box(self: Box<F>) {
    (*self)()
  }
}

type Job = Box<FnBox + Send + 'static>;

struct Worker {
  id: usize,
  thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
  fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Message>>>) -> Worker {
    // let thread = thread::spawn(|| {
    //   receiver;
    // });

    // let thread = thread::spawn(move || loop {
    //   let job = receiver.lock().unwrap().recv().unwrap();
    //   println!("Worker {} got a job; executing.", id);
    //   (*job)();
    // });

    let thread = thread::spawn(move || loop {
      let message = receiver.lock().unwrap().recv().unwrap();
      println!("Worker {} got a job; executing.", id);
      match message {
        Message::NewJob(job) => {
          println!("Worker {} got a job; executing.", id);
          job.call_box();
        }
        Message::Terminate => {
          println!("Worker {} was told to terminate.", id);
          break;
        }
      }
    });

    Worker {
      id,
      thread: Some(thread),
    }
  }
}

enum Message {
  NewJob(Job),
  Terminate,
}

impl Drop for ThreadPool {
  fn drop(&mut self) {
    println!("Sending terminate message to all workers.");

    for _ in &mut self.workers {
      self.sender.send(Message::Terminate).unwrap();
    }

    println!("Shutting down all workers.");
    for worker in &mut self.workers {
      println!("Shutting down worker {}", worker.id);
      if let Some(thread) = worker.thread.take() {
        thread.join().unwrap();
      }
    }
  }
}
