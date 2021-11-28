package main

import (
	"fmt"
	"net"
	"os"
	"time"

	// protoc で自動生成されたパッケージ
	"github.com/nissy-dev/grpc-tutorial/go/deepthought"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"

	// middleware
	grpc_zap "github.com/grpc-ecosystem/go-grpc-middleware/logging/zap"
)

const portNumber = 13333

func main() {
	// zapと呼ばれるloggerの準備
	zapLogger, _ := zap.NewDevelopment()

	// デフォルトの5分より短い間隔で何度もPINGフレームを送ると、エラーが発生する
	// 以下の設定を行うことで、5分以上の間隔でPINGフレームを送ることができるようになる
	kep := keepalive.EnforcementPolicy{
		MinTime: 10 * time.Second,
	}
	serv := grpc.NewServer(
		grpc.StreamInterceptor(grpc_zap.StreamServerInterceptor(zapLogger)),
		grpc.UnaryInterceptor(grpc_zap.UnaryServerInterceptor(zapLogger)),
		grpc.KeepaliveEnforcementPolicy(kep),
	)

	// 実装した Server を登録
	deepthought.RegisterComputeServer(serv, &Server{})

	// 待ち受けソケットを作成
	l, err := net.Listen("tcp", fmt.Sprintf(":%d", portNumber))
	if err != nil {
		fmt.Println("failed to listen:", err)
		os.Exit(1)
	}

	// gRPC サーバーでリクエストの受付を開始
	// l は Close されてから戻るので、main 関数での Close は不要
	serv.Serve(l)
}
