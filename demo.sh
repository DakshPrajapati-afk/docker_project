#!/usr/bin/env bash
# Sends the same prompt twice to show the cache miss -> hit latency drop,
# then prints /stats. Run `docker compose up --build -d` first.
set -euo pipefail

GATEWAY_URL="${GATEWAY_URL:-http://localhost:8000}"
PROMPT="What is containerization?"

echo "==> First request (expect a cache MISS, ~2s):"
curl -s -X POST "$GATEWAY_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$PROMPT\"}" | tee /tmp/cachematrix_demo_1.json
echo
echo

echo "==> Second request, same prompt (expect a cache HIT, near-instant):"
curl -s -X POST "$GATEWAY_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$PROMPT\"}" | tee /tmp/cachematrix_demo_2.json
echo
echo

echo "==> /stats:"
curl -s "$GATEWAY_URL/stats"
echo
