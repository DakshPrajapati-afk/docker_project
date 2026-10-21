#!/usr/bin/env bash
# Builds the naive single-stage gateway image and the real multi-stage one,
# then prints their sizes side by side for the write-up screenshot.
set -euo pipefail

cd "$(dirname "$0")/gateway"

echo "==> Building naive single-stage image..."
docker build -f Dockerfile.naive -t cachematrix-gateway:naive . >/dev/null

echo "==> Building multi-stage image..."
docker build -f Dockerfile -t cachematrix-gateway:multistage . >/dev/null

echo
echo "==> Image size comparison:"
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" \
  | grep -E "cachematrix-gateway:(naive|multistage)|REPOSITORY"
