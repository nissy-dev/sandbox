use std::io::{Error, Read, Write};
use std::net::{Ipv4Addr, SocketAddrV4, TcpListener, TcpStream};
use std::thread;
use std::time::Duration;

fn main() -> Result<(), Error> {
    let socket = SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 8080);
    let listener = TcpListener::bind(socket)?;
    let mut connection_cnt = 0;
    for stream in listener.incoming() {
        let stream = stream.unwrap();
        connection_cnt += 1;
        println!("{} Connection established!", connection_cnt);

        // レスポンスの返却
        handle_connection(stream);
    }
    Ok(())
}

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).unwrap();
    let request_str = String::from_utf8_lossy(&buffer);
    let request: Vec<&str> = request_str.split("\r\n").collect();

    // 以下リクエストをさばく
    let response_ok = String::from("HTTP/1.1 200 OK\r\n\r\n");
    match request[0] {
        "GET /echo HTTP/1.1" => {
            let body = "Hello, World!\r\n";
            let response = response_ok + body;
            stream.write(response.as_bytes()).unwrap();
            stream.flush().unwrap();
        }
        "GET /sleep HTTP/1.1" => {
            thread::sleep(Duration::from_secs(2));
            let body = "Server just fell asleep for a moment...\r\n";
            let response = response_ok + body;
            stream.write(response.as_bytes()).unwrap();
            stream.flush().unwrap();
        }
        _ => println!("Empty Response..."),
    }
}
