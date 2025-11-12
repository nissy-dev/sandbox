CLUSTER_NAME := crd-demo
BIN_DIR := bin
SCRIPTS_DIR := scripts

.PHONY: setup-cluster
setup-cluster:
	@echo "Setting up kind cluster..."
	@$(SCRIPTS_DIR)/setup-cluster.sh

.PHONY: teardown-cluster
teardown-cluster:
	@echo "Tearing down kind cluster..."
	@$(SCRIPTS_DIR)/teardown-cluster.sh

.PHONY: check-cluster
check-cluster:
	@echo "Checking cluster status..."
	@kubectl cluster-info --context kind-$(CLUSTER_NAME) || (echo "Cluster not found. Run 'make setup-cluster' first." && exit 1)

.PHONY: apply-crd
apply-crd: check-cluster
	@echo "Applying CRD..."
	@kubectl apply -f manifests/crd.yaml
	@echo "Waiting for CRD to be established..."
	@kubectl wait --for condition=established --timeout=60s crd/myresources.example.com
	@echo "CRD applied successfully!"

.PHONY: delete-crd
delete-crd:
	@echo "Deleting CRD..."
	@kubectl delete -f manifests/crd.yaml || true

.PHONY: codegen
codegen:
	@go get k8s.io/code-generator
	@echo "Generating code for CRD..."
	@scripts/update-codegen.sh
	@go mod tidy

.PHONY: run-clientset
run-clientset:
	@go run cmd/clientset/main.go

.PHONY: run-dynamic-client
run-dynamic-client:
	@go run cmd/dynamic-client/main.go

.PHONY: run-controller-runtime
run-controller-runtime:
	@go run cmd/controller-runtime/main.go
