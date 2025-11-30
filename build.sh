#!/bin/bash
# Build script for RAG ISO17025 Consulting System
# Usage: ./build.sh [api|frontend|all] [tag]
# Example: ./build.sh all v1.0.0

set -e

REGISTRY="${REGISTRY:-}"
API_IMAGE="${REGISTRY}rag-api"
FRONTEND_IMAGE="${REGISTRY}rag-frontend"
TAG="${2:-latest}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

build_api() {
    echo_info "Building API image: ${API_IMAGE}:${TAG}"
    docker build \
        --progress=plain \
        -t "${API_IMAGE}:${TAG}" \
        -t "${API_IMAGE}:latest" \
        -f api/Dockerfile \
        api/
    echo_info "API image built successfully"
}

build_frontend() {
    echo_info "Building Frontend image: ${FRONTEND_IMAGE}:${TAG}"
    docker build \
        --progress=plain \
        -t "${FRONTEND_IMAGE}:${TAG}" \
        -t "${FRONTEND_IMAGE}:latest" \
        -f frontend/Dockerfile \
        frontend/
    echo_info "Frontend image built successfully"
}

push_api() {
    if [ -z "$REGISTRY" ]; then
        echo_warn "No REGISTRY set, skipping push"
        return
    fi
    echo_info "Pushing API image: ${API_IMAGE}:${TAG}"
    docker push "${API_IMAGE}:${TAG}"
    docker push "${API_IMAGE}:latest"
    echo_info "API image pushed successfully"
}

push_frontend() {
    if [ -z "$REGISTRY" ]; then
        echo_warn "No REGISTRY set, skipping push"
        return
    fi
    echo_info "Pushing Frontend image: ${FRONTEND_IMAGE}:${TAG}"
    docker push "${FRONTEND_IMAGE}:${TAG}"
    docker push "${FRONTEND_IMAGE}:latest"
    echo_info "Frontend image pushed successfully"
}

case "${1:-all}" in
    api)
        build_api
        push_api
        ;;
    frontend)
        build_frontend
        push_frontend
        ;;
    all)
        build_api
        build_frontend
        push_api
        push_frontend
        ;;
    *)
        echo_error "Unknown target: $1"
        echo "Usage: $0 [api|frontend|all] [tag]"
        exit 1
        ;;
esac

echo_info "Build complete!"
