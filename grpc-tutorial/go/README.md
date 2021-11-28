# Go 実装

## コンパイル

```bash
// gRPCのコンパイル
$ ./grpc_compile.sh

// Go(server, client)のコンパイル
$ ./go_compile.sh
```

## サーバー・クライアントの使い方

```bash
// server
$ ./bin/server

// client
$ ./bin/client 127.0.0.1:13333 Life 800
```
