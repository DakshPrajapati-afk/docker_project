# Single-stage build: this service is tiny (two deps) so a multi-stage
# split wouldn't teach anything new here — that lesson lives in gateway/Dockerfile.
FROM python:3.12-slim

# Install curl only for the HEALTHCHECK below; removing apt lists keeps the layer small.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy just the requirements file first so Docker can cache this layer
# and skip the pip install when only application code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Create a dedicated non-root user/group. Running containers as root is a
# needless privilege escalation risk if the app is ever compromised.
RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid appuser --no-create-home appuser
USER appuser

EXPOSE 8001

# Docker/Compose uses this to know when the container is actually ready to
# serve traffic, not just "the process started".
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
