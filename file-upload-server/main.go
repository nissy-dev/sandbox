package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"syscall"
	"time"
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
	if err := os.RemoveAll(destPath); err != nil {
		return err
	}
	if err := os.MkdirAll(destPath, 0755); err != nil {
		return err
	}
	return exec.Command("tar", "-zxvf", tmpFilePath, "-C", destPath).Run()
}

type FileUploadHandler struct{}

func (h *FileUploadHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	destPath := r.FormValue("path")
	file, handler, err := r.FormFile("file")
	if destPath == "" || err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer file.Close()

	time.Sleep(6 * time.Second)

	tmpFile, err := saveFileToTempDir(file, handler.Filename)
	if err != nil {
		http.Error(w, "Failed to save file to temp directory", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tmpFile.Name())

	fmt.Fprintf(w, "Create tmp file successfully: %s\n", tmpFile.Name())

	if err := unTarFile(tmpFile.Name(), destPath); err != nil {
		http.Error(w, "Failed to untar file", http.StatusInternalServerError)
		return
	}
	fmt.Fprintf(w, "Untar tmp file successfully: %s\n", destPath)
}

func main() {
	server := http.Server{Addr: ":8080"}

	fileUploadHandler := FileUploadHandler{}
	http.Handle("PUT /upload", &fileUploadHandler)

	go func() {
		if err := server.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("HTTP server error: %v", err)
		}
		log.Println("Stopped serving new connections.")
	}()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	shutdownCtx, shutdownRelease := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownRelease()

	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("HTTP shutdown error: %v", err)
	}
	log.Println("Graceful shutdown complete.")
}
