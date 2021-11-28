# grpc-tutorial

## 依存バイナリのインストール

`protoc` は、asdf でインストールしている前提。

```bash
$ GOBIN=$(pwd)/bin go install github.com/pseudomuto/protoc-gen-doc/cmd/protoc-gen-doc@v1.5.0
$ GOBIN=$(pwd)/bin go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.26.0
$ GOBIN=$(pwd)/bin go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.1.0
```
