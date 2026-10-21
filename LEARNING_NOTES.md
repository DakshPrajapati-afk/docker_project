# Docker Concepts — Learning Notes

Plain-English notes on the Docker concepts used in this project, for the
assignment write-up.

## Image vs. container

An **image** is a read-only template: a filesystem snapshot plus metadata
(what command to run, what port to expose, etc.), built once from a
Dockerfile. A **container** is a running instance of an image — the same
image can be started as many independent containers, each with its own
writable layer, process, and network identity, but they all start from the
exact same image contents. It's the same relationship as a class and an
object: the image is the blueprint, the container is the live thing.

## Layers

Each instruction in a Dockerfile (`RUN`, `COPY`, etc.) produces a new
filesystem layer stacked on top of the previous one. Docker caches layers,
so if a layer's inputs haven't changed, Docker reuses the cached result
instead of re-running that step. That's why `gateway/Dockerfile` copies
`requirements.txt` and runs `pip install` *before* copying the rest of the
application code: changing a `.py` file only invalidates the last couple of
layers, not the (slow) dependency install.

## Multi-stage builds

A multi-stage Dockerfile has more than one `FROM` line, each starting a
named stage. Earlier stages can contain compilers, build tools, or anything
else needed to produce an artifact, and later stages can selectively
`COPY --from=<stage>` just that artifact — leaving everything else from the
earlier stage behind. `gateway/Dockerfile` uses this to install Python
packages in a `builder` stage, then copy only the installed packages into a
clean final image, so build tooling never ends up in the image that
actually ships. `size_compare.sh` demonstrates the size difference this
makes versus the naive single-stage `Dockerfile.naive`.

## Volumes

A volume is storage that lives outside a container's writable layer and
persists independently of any single container's lifecycle. The `redis`
service mounts a named volume (`redis-data`) at `/data`, so cached answers
and stats survive `docker compose down` and container restarts — without
it, all cached data would vanish the moment the Redis container stopped.

## Networks

Compose automatically creates a private network for a project and attaches
every service to it, giving each service a DNS name equal to its service
name (`gateway` can reach Redis at `redis:6379` without knowing its IP).
This project defines an explicit named network, `cachematrix-net`, so that
relationship is visible and intentional in `docker-compose.yml` rather than
left to compose's default. Only `gateway`'s port is published to the host
with `ports:`; `redis` and `mock-llm` have no `ports:` entry at all, so
they're reachable *only* from other containers on that network, not from
the host machine or the outside world.

## Healthchecks

A `HEALTHCHECK` instruction tells Docker how to actively verify that a
container is not just running, but actually working — by running a command
inside it on an interval (here, hitting each service's own `/health`
endpoint, or `redis-cli ping` for Redis) and marking the container
`healthy`/`unhealthy` based on the result. Without this, Docker only knows
whether the container's main process is alive, which is a much weaker
signal — a FastAPI app can be "running" while still failing to accept
connections during startup.

## `depends_on` with `condition: service_healthy`

Plain `depends_on` only waits for a dependency's container to *start*, not
for it to be ready to serve traffic — which matters here because the
`gateway` container could start and immediately get a connection refused
from Redis if Redis is still initializing. `condition: service_healthy`
makes Compose wait for the dependency's `HEALTHCHECK` to report healthy
before starting the dependent service, which is why `gateway` doesn't start
until both `redis` and `mock-llm` are confirmed healthy.
