# Production-ready Backend Dockerfile (multi-stage, non-root, pinned Python 3.10)

FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
  && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest and build wheels to leverage layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
  && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# Final runtime image
FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user for security (fixed UID/GID to keep filesystem permissions predictable)
RUN groupadd -g 1000 appgroup || true \
  && useradd -m -u 1000 -g appgroup -s /bin/bash app || true

WORKDIR /app

# Install minimal runtime dependencies and tini init
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    tini \
  && rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
  && rm -rf /wheels

# Copy application code
COPY . /app

# Ensure the entrypoint script is executable
RUN chmod +x /app/docker-entrypoint.sh || true

# Fix ownership
RUN chown -R app:app /app || true
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

# Use tini as PID 1 for proper signal handling and an entrypoint that can run migrations then exec the CMD
ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
