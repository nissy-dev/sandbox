package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"log/slog"
	"mime/multipart"
	"net/http"
	_ "net/http/pprof"
	"os"
	"os/exec"
	"os/signal"
	"syscall"
	"time"

	"golang.org/x/sync/errgroup"
)

func saveFileToTempDir(file multipart.File, filename string) (*os.File, error) {
	tmpFile, err := os.CreateTemp("", filename)
	if err != nil {
		return nil, err
	}
	if _, err := io.Copy(tmpFile, file); err != nil {
		return nil, err
	}
	return tmpFile, nil
}

func unTarFile(tmpFilePath string, destPath string) error {
	if err := os.MkdirAll(destPath, 0755); err != nil {
		return err
	}
	return exec.Command("tar", "-zxvf", tmpFilePath, "-C", destPath).Run()
}

type MultiPartFileUploadHandler struct{}

func (h *MultiPartFileUploadHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	destPath := r.FormValue("unpack-dir")
	file, handler, err := r.FormFile("file")
	if destPath == "" || err != nil {
		slog.Error(fmt.Sprintf("Invalid request body: %v", err))
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer file.Close()

	tmpFile, err := saveFileToTempDir(file, handler.Filename)
	if err != nil {
		slog.Error(fmt.Sprintf("Failed to save file to temp directory: %v", err))
		http.Error(w, "Failed to save file to temp directory", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tmpFile.Name())

	slog.Info(fmt.Sprintf("Create tmp file successfully: %s\n", tmpFile.Name()))

	if err := unTarFile(tmpFile.Name(), destPath); err != nil {
		slog.Error(fmt.Sprintf("Failed to untar file: %v", err))
		http.Error(w, "Failed to untar file", http.StatusInternalServerError)
		return
	}
	slog.Info(fmt.Sprintf("Untar tmp file successfully: %s\n", destPath))
	fmt.Fprintf(w, "Upload data successfully to %s\n", destPath)
}

type FileUploadHandler struct {
	ctx context.Context
}

func (h *FileUploadHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	unpackDir := r.Header.Get("Unpack-Dir")
	if unpackDir == "" {
		http.Error(w, "Header Unpack-Dir is missing", http.StatusBadRequest)
		return
	}

	cmd := exec.Command("tar", "-zxf", "-", "-C", unpackDir)
	reader, err := cmd.StdinPipe()
	defer reader.Close()
	if err != nil {
		http.Error(w, "Failed to create pipe", http.StatusInternalServerError)
		return
	}

	g, _ := errgroup.WithContext(h.ctx)

	g.Go(func() error {
		defer reader.Close()
		if _, err := io.Copy(reader, r.Body); err != nil {
			slog.Error(fmt.Sprintf("Failed to copy body to pipe: %v", err))
			return err
		}
		return nil
	})

	g.Go(func() error {
		if err := cmd.Run(); err != nil {
			slog.Error(fmt.Sprintf("Failed to tar command: %v", err))
			return err
		}
		return nil
	})

	if err := g.Wait(); err != nil {
		http.Error(w, "Failed to upload data", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "Upload data successfully to %s\n", unpackDir)
}

func run() error {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM, os.Interrupt)
	defer stop()

	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	mux := http.NewServeMux()
	g, ctx := errgroup.WithContext(ctx)
	server := http.Server{Addr: ":8080", Handler: mux}

	mux.Handle("POST /multi-part-upload", &MultiPartFileUploadHandler{})
	mux.Handle("POST /upload", &FileUploadHandler{ctx: ctx})

	g.Go(func() error {
		if err := server.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
			slog.Error(fmt.Sprintf("HTTP server error: %v", err))
			return err
		}
		slog.Info("Stopped serving new connections.")
		return nil
	})

	go func() {
		log.Println(http.ListenAndServe("localhost:6060", nil))
	}()

	g.Go(func() error {
		<-ctx.Done()
		slog.Info("Shutting down server...")
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		if err := server.Shutdown(ctx); err != nil {
			slog.Error(fmt.Sprintf("HTTP server error: %v", err))
			return err
		}
		return nil
	})

	if err := g.Wait(); err != nil {
		slog.Error(fmt.Sprintf("Error: %v", err))
		return err
	}

	slog.Info("Graceful shutdown complete.")
	return nil
}

func main() {
	if err := run(); err != nil {
		os.Exit(1)
	}
}
