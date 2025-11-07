.PHONY: build run setup-infra teardown-infra clean k6-load-test

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

setup-infra:
	@echo "Starting prometheus and grafana..."
	@docker compose -f infra/compose.yml up -d

teardown-infra:
	@echo "Stopping prometheus and grafana..."
	@docker compose -f infra/compose.yml down -v

clean:
	@echo "Cleaning..."
	@rm -rf bin/
	@rm -rf proto/gen/

k6-load-test:
	@docker run --rm --network host -v ./infra/k6:/scripts \
		grafana/k6:latest run /scripts/script.js
