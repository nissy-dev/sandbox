#!/bin/bash
set -e

CLUSTER_NAME="crd-demo"

echo "Creating kind cluster: ${CLUSTER_NAME}..."
kind create cluster --name ${CLUSTER_NAME}

echo "Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=60s

echo "Cluster created successfully!"
kubectl cluster-info --context kind-${CLUSTER_NAME}
kubectl get nodes
