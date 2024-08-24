package main

import (
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
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
	server.ListenAndServe()
}
