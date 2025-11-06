package metrics

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"golang.org/x/sync/errgroup"
)

var shutdownTimeout = 5 * time.Second

type promLogger struct{}

func (l *promLogger) Println(v ...interface{}) {
	slog.Error("prometheus client error", "error", fmt.Sprint(v...))
}

type Server struct {
	server *http.Server
}

func NewServer(port uint16) (*Server, *prometheus.Registry) {
	mux := http.NewServeMux()
	registry := prometheus.NewRegistry()
	mux.Handle("/metrics", promhttp.HandlerFor(
		// custom metrics を実装する場合はこの Registry に登録する
		registry,
		promhttp.HandlerOpts{
			// errorlog を slog に対応させる
			ErrorLog: &promLogger{},
			// metrics 収集は多少失敗しても良いので ContinueOnError を指定する
			ErrorHandling: promhttp.ContinueOnError,
		},
	))
	server := &http.Server{
		Addr:    fmt.Sprintf(":%d", port),
		Handler: mux,
	}
	return &Server{server: server}, registry
}

func (s *Server) Serve(ctx context.Context) error {
	eg, egCtx := errgroup.WithContext(ctx)

	eg.Go(func() error {
		slog.Info(fmt.Sprintf("metrics server started on %s", s.server.Addr))
		if err := s.server.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
			return fmt.Errorf("metrics: failed to start the server %v", err)
		}
		return nil
	})

	eg.Go(func() error {
		<-egCtx.Done()
		slog.Info("shutting down metrics server...")
		ctx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
		defer cancel()

		if err := s.server.Shutdown(ctx); err != nil {
			return fmt.Errorf("metrics: failed to shutdown the server: %v", err)
		}
		slog.Info("metrics server stopped")
		return nil
	})

	return eg.Wait()
}
