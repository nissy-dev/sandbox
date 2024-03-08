use mini_redis::client;
use tokio::sync::{mpsc, oneshot};

use bytes::Bytes;
use tokio_stream::StreamExt;

type Responder<T> = oneshot::Sender<mini_redis::Result<T>>;

#[derive(Debug)]
enum Command {
    Get {
        key: String,
        resp: Responder<Option<Bytes>>,
    },
    Set {
        key: String,
        val: Bytes,
        resp: Responder<()>,
    },
}

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(32);
    let tx2 = tx.clone();

    let task1 = tokio::spawn(async move {
        let (resp_tx, resp_rx) = oneshot::channel();
        let cmd = Command::Get {
            key: "hello".to_string(),
            resp: resp_tx,
        };

        tx.send(cmd).await.unwrap();

        // レスポンスが来るのを待つ
        let res = resp_rx.await;
        println!("GOT = {:?}", res);
    });

    let task2 = tokio::spawn(async move {
        let (resp_tx, resp_rx) = oneshot::channel();
        let cmd = Command::Set {
            key: "foo".to_string(),
            val: "bar".into(),
            resp: resp_tx,
        };

        tx2.send(cmd).await.unwrap();
        // レスポンスが来るのを待つ
        let res = resp_rx.await;
        println!("GOT = {:?}", res);
    });

    // `rx` の所有権をタスクへとムーブするために `move` キーワードを付ける
    let manager = tokio::spawn(async move {
        // サーバーへのコネクションを確立する
        let mut client = client::connect("127.0.0.1:6379").await.unwrap();

        // メッセージの受信を開始
        while let Some(cmd) = rx.recv().await {
            match cmd {
                Command::Get { key, resp } => {
                    let res = client.get(&key).await;
                    // Result 型が帰ってくるが、エラーのハンドリングはしない
                    let _ = resp.send(res);
                }
                Command::Set { key, val, resp } => {
                    let res = client.set(&key, val).await;
                    let _ = resp.send(res);
                }
            }
        }
    });

    task1.await.unwrap();
    task2.await.unwrap();
    manager.await.unwrap();

    tokio::spawn(async { publish().await });

    subscribe().await.unwrap();

    println!("DONE");
}

async fn publish() -> mini_redis::Result<()> {
    let mut client = client::connect("127.0.0.1:6379").await?;

    // いくつかのデータを発行する
    client.publish("numbers", "1".into()).await?;
    client.publish("numbers", "two".into()).await?;
    client.publish("numbers", "3".into()).await?;
    client.publish("numbers", "four".into()).await?;
    client.publish("numbers", "five".into()).await?;
    client.publish("numbers", "6".into()).await?;
    Ok(())
}

async fn subscribe() -> mini_redis::Result<()> {
    let client = client::connect("127.0.0.1:6379").await?;
    let subscriber = client.subscribe(vec!["numbers".to_string()]).await?;
    let messages = subscriber.into_stream();

    tokio::pin!(messages);

    while let Some(msg) = messages.next().await {
        println!("got = {:?}", msg);
    }

    Ok(())
}
