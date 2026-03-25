// go-http-timeout-check: verifies whether net/http Client.Timeout errors
// compare equal to context.DeadlineExceeded via errors.Is.
package main

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"time"
)

func main() {
	// Server that never finishes the response body in time (slow handler).
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		select {
		case <-time.After(5 * time.Second):
			_, _ = w.Write([]byte("ok"))
		case <-r.Context().Done():
			// Client cancelled; normal for timeout test.
		}
	}))
	defer srv.Close()

	client := &http.Client{Timeout: 50 * time.Millisecond}

	resp, err := client.Get(srv.URL)
	if resp != nil {
		_ = resp.Body.Close()
	}

	fmt.Println("=== http.Client.Timeout ===")
	printErrChain("Get", err)
	fmt.Printf("errors.Is(err, context.DeadlineExceeded): %v\n", errors.Is(err, context.DeadlineExceeded))
	fmt.Printf("errors.Is(err, context.Canceled): %v\n", errors.Is(err, context.Canceled))
	fmt.Println()
}

func printErrChain(label string, err error) {
	if err == nil {
		fmt.Printf("%s: err is nil\n", label)
		return
	}
	fmt.Printf("%s: %v\n", label, err)
	fmt.Printf("%s: type: %T\n", label, err)
	var e error = err
	for i := 0; e != nil && i < 10; i++ {
		fmt.Printf("  unwrap[%d]: %T — %v\n", i, e, e)
		e = errors.Unwrap(e)
	}
}
