package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"os"
	"strconv"
	"time"

	"github.com/nissy-dev/grpc-tutorial/go/deepthought"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/status"
)

func main() {
	var err error

	// 少なくとも接続するサーバーのアドレスは必要
	if len(os.Args) < 2 {
		err = errors.New("At least one argument is required....")
	}

	addr := os.Args[1]
	// keep-aliveを設定し、接続先がまだ存在していることを確認する
	kp := keepalive.ClientParameters{
		Time: 1 * time.Minute,
	}
	// grpc.WithInsecure() を指定することで、TLS ではなく平文で接続
	// 通信内容が保護できないし、不正なサーバーに接続しても検出できないので本当はダメ
	conn, err := grpc.Dial(addr, grpc.WithInsecure(), grpc.WithKeepaliveParams(kp))
	// 使い終わったら Close しないとコネクションがリークします
	defer conn.Close()

	if len(os.Args) == 3 {
		err = callBoot(conn)
	} else if len(os.Args) == 4 {
		err = callInfer(conn)
	}

	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func callBoot(conn *grpc.ClientConn) error {
	// 自動生成された RPC クライアントを conn から作成
	// gRPC は HTTP/2 の stream を用いるため、複数のクライアントが同一の conn を使えます。
	// また RPC クライアントのメソッドも複数同時に呼び出し可能です。
	// see https://github.com/grpc/grpc-go/blob/master/Documentation/concurrency.md
	cc := deepthought.NewComputeClient(conn)

	// Boot を 2.5 秒後にクライアントからキャンセルするコード
	ctx, cancel := context.WithCancel(context.Background())
	go func(cancel func()) {
		time.Sleep(2500 * time.Millisecond)
		cancel()
	}(cancel)

	// 自動生成された Boot RPC 呼び出しコードを実行
	req, err := strconv.ParseBool(os.Args[2])
	if err != nil {
		return err
	}

	stream, err := cc.Boot(ctx, &deepthought.BootRequest{Silent: req})
	if err != nil {
		return err
	}

	// ストリームから読み続ける
	for {
		resp, err := stream.Recv()
		if err != nil {
			// io.EOF は stream の正常終了を示す値
			if err == io.EOF {
				break
			}
			// status パッケージは error と gRPC status の相互変換を提供
			// `status.Code` は gRPC のステータスコードを取り出す
			// see https://pkg.go.dev/google.golang.org/grpc/status
			if status.Code(err) == codes.Canceled {
				// キャンセル終了ならループを脱出
				break
			}
			return fmt.Errorf("receiving boot response: %w", err)
		}
		fmt.Printf("Boot (message): %s\n", resp.Message)
		fmt.Printf("Boot (timestamp): %s\n", resp.Timestamp)
	}

	return nil
}

func callInfer(conn *grpc.ClientConn) error {
	// コマンドラインから必要なデータを取得
	req := os.Args[2]
	timeOut, err := strconv.Atoi(os.Args[3])
	if err != nil {
		return err
	}

	// 自動生成された RPC クライアントを conn から作成
	cc := deepthought.NewComputeClient(conn)

	// Timeout時間を指定しているコード
	ctx, cancel := context.WithTimeout(
		context.Background(),
		time.Duration(timeOut)*time.Millisecond,
	)
	defer cancel()

	// 自動生成された Infer RPC 呼び出しコードを実行
	resp, err := cc.Infer(ctx, &deepthought.InferRequest{Query: req})
	if resp != nil {
		fmt.Printf("Infer Answer: %d\n", resp.Answer)
		// fmt.Printf("Infer Description: %s\n", resp.Description)
	}

	return err
}
