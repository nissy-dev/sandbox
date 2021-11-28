# web

## 環境構築

```
$ npm install

// gRPC-WebがM1用のバイナリをリリースしていないことから、dockerコンテナを用意する
$ docker build . --platform linux/x86_64 -t grpc-web
```

## コンパイル

```bash
// gRPCのコンパイル
$ ./grpc_compile.sh
```
