# ── Stage 1: Build dependencies ───────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies needed to compile asyncpg / psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first (better layer caching)
COPY requirements.txt .

# Install dependencies into an isolated prefix
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Development image ────────────────────────────────────────────────
FROM python:3.12-slim AS development

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Expose the application port
EXPOSE 8000

# Hot-reload on every file change – code is mounted as a volume
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]


# ── Stage 3: Production image ─────────────────────────────────────────────────
FROM python:3.12-slim AS production

# Non-root user for security
RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy source code
COPY --chown=appuser:appgroup . .

USER appuser

# Expose the application port
EXPOSE 8000

# Health check for Docker / ECS
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

# Start with Uvicorn (production settings: no reload, 4 workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
