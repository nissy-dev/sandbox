package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/nissy-dev/sandbox/go-grpc-red-method/internal/grpc"
	"github.com/nissy-dev/sandbox/go-grpc-red-method/internal/metrics"
	"github.com/nissy-dev/sandbox/go-grpc-red-method/internal/service"
	pb "github.com/nissy-dev/sandbox/go-grpc-red-method/proto/gen/go/proto"
	"google.golang.org/grpc/reflection"

	"golang.org/x/sync/errgroup"
)

// logger を引き回したいときは context を利用する方法がある
// cf: https://blog.cybozu.io/entry/2024/08/07/080000
// context を解釈する custom handler を作るという方法もある
// cf: https://speakerdeck.com/arthur1/kamakura-go-6-slog?slide=29
func init() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{AddSource: true}))
	slog.SetDefault(logger)
}

var stopSignals = []os.Signal{syscall.SIGINT, syscall.SIGTERM}

func main() {
	signalCtx, cancel := signal.NotifyContext(context.Background(), stopSignals...)
	defer cancel()

	grpcServer, grpcServerMetrics := grpc.NewServer(8080)
	metricsServer, prometheusRegistry := metrics.NewServer(8081)
	// gRPC server の metrics を Prometheus registry に登録する
	prometheusRegistry.MustRegister(grpcServerMetrics)

	sampleService := service.NewSampleService()
	pb.RegisterSampleServiceServer(grpcServer, sampleService)

	// reflection を有効化しておく
	reflection.Register(grpcServer)

	eg, egCtx := errgroup.WithContext(signalCtx)
	eg.Go(func() error {
		return grpcServer.Serve(egCtx)
	})

	eg.Go(func() error {
		return metricsServer.Serve(egCtx)
	})

	if err := eg.Wait(); err != nil {
		os.Exit(1)
	}
}
