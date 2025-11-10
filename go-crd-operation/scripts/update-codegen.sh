#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
SCRIPT_ROOT="${SCRIPT_DIR}/.."
CODEGEN_PKG=$(go list -m -f '{{.Dir}}' k8s.io/code-generator)

source "${CODEGEN_PKG}/kube_codegen.sh"

THIS_PKG="github.com/nissy-dev/sandbox/go-crd-operation"

kube::codegen::gen_helpers \
    --boilerplate "${SCRIPT_ROOT}/scripts/boilerplate.go.txt" \
    "${SCRIPT_ROOT}"

kube::codegen::gen_register \
    --boilerplate "${SCRIPT_ROOT}/scripts/boilerplate.go.txt" \
    "${SCRIPT_ROOT}"

kube::codegen::gen_client \
    --with-watch \
    --output-dir "${SCRIPT_ROOT}/pkg/generated" \
    --output-pkg "${THIS_PKG}/pkg/generated" \
    --boilerplate "${SCRIPT_ROOT}/scripts/boilerplate.go.txt" \
    "${SCRIPT_ROOT}/pkg/apis"
