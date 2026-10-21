# CacheMatrix-mini

A small, fully-containerized caching gateway for LLM apps, built as a learning
project for a Docker/containerization class assignment. It's a stripped-down
version of my capstone, CacheMatrix: a gateway that sits in front of an LLM,
caches answers to repeated prompts, and serves cached hits instantly instead
of paying the LLM's latency again.

## Architecture

```
                 host:8000
                     |
                     v
          +----------------------+
          |       gateway        |   FastAPI, Python 3.12
          |  /chat /health /stats|
          +----------+-----------+
                 |         |
      cache hit? |         | cache miss
                 v         v
          +-------------+  +----------------+
          |    redis    |  |   mock-llm     |
          | (cache +    |  | FastAPI,       |
          |  stats)     |  | ~2s fake delay |
          +-------------+  +----------------+

   All three containers share one internal Docker network
   (cachematrix-net). Only the gateway's port is published to
   the host; redis and mock-llm are reachable only on that network.
```

Flow for `POST /chat`:
1. Normalize the prompt (trim + lowercase) and hash it (SHA-256).
2. Look up the hash in Redis.
   - **Hit**: return the cached answer immediately.
   - **Miss**: call `mock-llm`'s `/generate`, store the result in Redis with
     a TTL, bump the miss counter, and return it.

## Services

| Service    | Role                                   | Exposed to host? |
|------------|----------------------------------------|-------------------|
| `gateway`  | FastAPI caching gateway                 | yes, port 8000    |
| `redis`    | cache storage + hit/miss counters       | no (internal only)|
| `mock-llm` | fake slow LLM (sleeps ~2s per request)  | no (internal only)|

## Running it

Requires Docker with Compose v2.

```bash
cp .env.example .env   # optional, defaults work out of the box
docker compose up --build
```

Wait for all three containers to report healthy (compose will wait on this
automatically before starting `gateway`), then in another terminal:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Docker?"}'

curl http://localhost:8000/stats
```

## Running the demo

With the stack up (`docker compose up --build -d`):

```bash
./demo.sh
```

This sends the same prompt twice and prints the full JSON response for
each, so you can see `cache: "miss"` with ~2000ms latency on the first
call and `cache: "hit"` with single-digit-millisecond latency on the
second, followed by `/stats`.

## Image size: naive vs. multi-stage build

```bash
./size_compare.sh
```

Builds `gateway/Dockerfile.naive` (single-stage, ships build tools and
runs as root) alongside `gateway/Dockerfile` (multi-stage, slim runtime,
non-root user) and prints both image sizes for comparison/screenshot.

Measured on this machine:

```
REPOSITORY:TAG                      SIZE
cachematrix-gateway:naive           1.68GB
cachematrix-gateway:multistage      344MB
```

The multi-stage build is roughly 80% smaller, mainly because the naive
build keeps the full `python:3.12` image (compilers, headers, apt
metadata) in its final layer, while the multi-stage build only copies
the installed Python packages into a `python:3.12-slim` base.

## Tests

```bash
cd gateway
pip install -r requirements-dev.txt
pytest
```

Tests use `fakeredis` so they don't need a real Redis instance.

## What I learned

_(placeholder — fill in after finishing the assignment write-up)_

-
-
-
