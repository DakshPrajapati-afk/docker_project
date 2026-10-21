# ---- Stage 1: builder -------------------------------------------------
# Full-size image with build tools. We install Python deps into a local
# directory here so the final stage can copy just that directory instead
# of carrying pip, gcc headers, apt caches, etc.
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
# --user installs into /root/.local, a self-contained folder we can copy
# wholesale into the final stage without dragging pip itself along.
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: final / runtime -----------------------------------------
# Start fresh from the same slim base. None of the builder's layers
# (pip cache, apt metadata, wheel build artifacts) exist in this image.
FROM python:3.12-slim

# curl is only needed so the HEALTHCHECK below can hit the app's /health
# endpoint; without it the container would need wget or a Python-based
# check instead.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a non-root user to run the app as. Containers run as root by
# default, which is more privilege than this process needs.
RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid appuser --no-create-home appuser

# Pull the already-installed packages from the builder stage instead of
# re-running pip install. This is the core multi-stage trick.
COPY --from=builder /root/.local /home/appuser/.local
COPY app/ ./app/

# Give appuser ownership of what it needs to read/execute before dropping
# out of root.
RUN chown -R appuser:appuser /app /home/appuser/.local
USER appuser

# So Python can find the packages installed under the appuser home dir,
# and so pip-installed console scripts (like uvicorn) are on PATH.
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
