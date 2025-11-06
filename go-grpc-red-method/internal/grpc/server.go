package grpc

import (
	"context"
	"fmt"
	"log/slog"
	"net"

	grpcprom "github.com/grpc-ecosystem/go-grpc-middleware/providers/prometheus"
	"github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors"
	"github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/logging"
	"github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/selector"
	_grpc "google.golang.org/grpc"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection/grpc_reflection_v1"
)

// InterceptorLogger adapts slog logger to interceptor logger.
// This code is simple enough to be copied and not imported.
func InterceptorLogger(l *slog.Logger) logging.Logger {
	return logging.LoggerFunc(func(ctx context.Context, lvl logging.Level, msg string, fields ...any) {
		l.Log(ctx, slog.Level(lvl), msg, fields...)
	})
}

func shouldLog(_ context.Context, callMeta interceptors.CallMeta) bool {
	switch callMeta.FullMethod() {
	case grpc_health_v1.Health_Check_FullMethodName:
	case grpc_health_v1.Health_Watch_FullMethodName:
	case grpc_reflection_v1.ServerReflection_ServerReflectionInfo_FullMethodName:
		return false
	}
	return true
}

type Server struct {
	port   uint16
	server *_grpc.Server
}

func NewServer(port uint16) (*Server, *grpcprom.ServerMetrics) {
	logger := slog.Default()

	grpcServerMetrics := grpcprom.NewServerMetrics(grpcprom.WithServerHandlingTimeHistogram())
	// ログの設定は不要だけど、参考に実装しておく
	grpcServer := _grpc.NewServer(
		_grpc.ChainUnaryInterceptor(
			selector.UnaryServerInterceptor(
				grpcServerMetrics.UnaryServerInterceptor(),
				selector.MatchFunc(shouldLog),
			),
			selector.UnaryServerInterceptor(
				logging.UnaryServerInterceptor(InterceptorLogger(logger)),
				selector.MatchFunc(shouldLog),
			),
		),
		// stream interceptor も同様に設定可能
	)
	grpcServerMetrics.InitializeMetrics(grpcServer)
	return &Server{
		port:   port,
		server: grpcServer,
	}, grpcServerMetrics
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

func (s *Server) GetServiceInfo() map[string]_grpc.ServiceInfo {
	return s.server.GetServiceInfo()
}
