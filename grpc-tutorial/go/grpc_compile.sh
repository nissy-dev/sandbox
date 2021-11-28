protoc -I ../protos --go_out=module=github.com/nissy-dev/grpc-tutorial/go:. deepthought.proto
protoc -I ../protos --go-grpc_out=module=github.com/nissy-dev/grpc-tutorial/go:. deepthought.proto
