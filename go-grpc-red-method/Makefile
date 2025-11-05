.PHONY: proto build run test clean

proto:
	@echo "Generating proto files..."
	@mkdir -p proto/gen/go
	@protoc \
    --go_out=proto/gen/go \
    --go_opt=paths=source_relative \
    --go-grpc_out=proto/gen/go \
    --go-grpc_opt=paths=source_relative \
    proto/*.proto

build: proto
	@echo "Building server..."
	@CGO_ENABLED=0 go build -trimpath -o bin/server ./cmd/server

run: build
	@echo "Starting server..."
	@./bin/server

# Run tests
test:
	@echo "Running tests..."
	@go test -race -v ./...

clean:
	@echo "Cleaning..."
	@rm -rf bin/
	@rm -rf proto/gen/
