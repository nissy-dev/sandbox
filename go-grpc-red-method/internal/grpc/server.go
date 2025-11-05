package grpc

import (
	"context"
	"fmt"
	"log/slog"
	"net"

	grpcprom "github.com/grpc-ecosystem/go-grpc-middleware/providers/prometheus"
	_grpc "google.golang.org/grpc"
)

type Server struct {
	port   uint16
	server *_grpc.Server
}

func NewServer(port uint16) *Server {
	grpcServerMetrics := grpcprom.NewServerMetrics(grpcprom.WithServerHandlingTimeHistogram())
	// ログの設定は不要だけど、参考に実装しておく
	grpcServer := _grpc.NewServer()
	grpcServerMetrics.InitializeMetrics(grpcServer)
	return &Server{
		port:   port,
		server: grpcServer,
	}
}

func (s *Server) Serve(ctx context.Context) error {
	address := fmt.Sprintf(":%d", s.port)
	listener, err := net.Listen("tcp", address)
	if err != nil {
		return fmt.Errorf("grpc: failed to listen: %v", err)
	}

	go func() {
		<-ctx.Done()
		slog.Info("shutting down gRPC server...")
		s.server.GracefulStop()
		slog.Info("grpc server stopped")
	}()

	slog.Info(fmt.Sprintf("gRPC server started on %s", address))
	return s.server.Serve(listener)
}

func (s *Server) RegisterService(sd *_grpc.ServiceDesc, ss any) {
	s.server.RegisterService(sd, ss)
}
