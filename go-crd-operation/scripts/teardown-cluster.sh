#!/bin/bash
set -e

CLUSTER_NAME="crd-demo"

echo "Deleting kind cluster: ${CLUSTER_NAME}..."
kind delete cluster --name ${CLUSTER_NAME}

echo "Cluster deleted successfully!"
