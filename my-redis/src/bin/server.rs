use bytes::Bytes;
use mini_redis::{Connection, Frame};
use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
};
use tokio::net::{TcpListener, TcpStream};

type DB = Arc<Mutex<HashMap<String, Bytes>>>;

#[tokio::main]
async fn main() {
    // リスナーをこのアドレスにバインドする
    let listener = TcpListener::bind("127.0.0.1:6379").await.unwrap();
    let db: DB = Arc::new(Mutex::new(HashMap::new()));

    loop {
        // タプルの2つ目の要素は、新しいコネクションのIPとポートの情報を含んでいる
        let (socket, _) = listener.accept().await.unwrap();
        // それぞれのインバウンドソケットに対して新しいタスクを spawn する
        // ソケットは新しいタスクに move され、そこで処理される

        let db = db.clone();
        tokio::spawn(async move {
            process(socket, db).await;
        });
    }
}

async fn process(socket: TcpStream, db: DB) {
    use mini_redis::Command::{self, Get, Set};

    // `mini-redis` が提供するコネクションによって、ソケットから来るフレームをパースする
    let mut connection = Connection::new(socket);

    while let Some(frame) = connection.read_frame().await.unwrap() {
        let response = match Command::from_frame(frame).unwrap() {
            Set(cmd) => {
                let mut db = db.lock().unwrap();
                db.insert(cmd.key().to_string(), cmd.value().clone());
                Frame::Simple("OK".to_string())
            }
            Get(cmd) => {
                let db = db.lock().unwrap();
                if let Some(value) = db.get(cmd.key()) {
                    Frame::Bulk(value.clone())
                } else {
                    Frame::Null
                }
            }
            cmd => panic!("unimplemented {:?}", cmd),
        };

        // クライアントへのレスポンスを書き込む
        connection.write_frame(&response).await.unwrap();
    }
}
