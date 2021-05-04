use std::fs::File;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};
use std::thread;
use std::time::Duration;

// 独自モジュール定義
extern crate hello;
use hello::ThreadPool;

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    // スレッドプールの実装
    let pool = ThreadPool::new(4);

    for stream in listener.incoming() {
        // for stream in listener.incoming().take(2) {
        let stream = stream.unwrap();
        // handle_connection_1(stream);
        // handle_connection_2(stream);

        // マルチスレッド化
        // ただ、以下だとスレッド数に制限がかけられない
        // thread::spawn(|| {
        //     handle_connection_2(stream);
        // });
        pool.execute(|| {
            handle_connection_2(stream);
        });
    }
}

// readするだけなのにmutableなのは、TcpStreamによって内部状態が変わる可能性があるから
fn handle_connection_1(mut stream: TcpStream) {
    // byteデータの初期化
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).unwrap();
    // HTTPの中身を確認
    // println!("Request: {}", String::from_utf8_lossy(&buffer[..]));

    // ただのレスポンス
    // let response = "HTTP/1.1 200 OK\r\n\r\n";
    // HTMLも含めたレスポンス
    let mut file = File::open("hello.html").unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();
    let response = format!("HTTP/1.1 200 OK\r\n\r\n{}", contents);

    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}

fn handle_connection_2(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).unwrap();

    let get = b"GET / HTTP/1.1\r\n";
    let sleep = b"GET /sleep HTTP/1.1\r\n";
    let (status_line, filename) = if buffer.starts_with(get) {
        ("HTTP/1.1 200 OK\r\n\r\n", "hello.html")
    } else if buffer.starts_with(sleep) {
        thread::sleep(Duration::from_secs(5));
        ("HTTP/1.1 200 OK\r\n\r\n", "hello.html")
    } else {
        ("HTTP/1.1 404 NOT FOUND\r\n\r\n", "404.html")
    };

    let mut file = File::open(filename).unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();
    let response = format!("{}{}", status_line, contents);

    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}
