# Pattern 3: Pub/Sub
FROM python:3.11-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files and install
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy shared utilities
COPY src/shared/ ./src/shared/

# Copy service code
COPY src/services/pubsub/ ./src/services/pubsub/

WORKDIR /app/src/services/pubsub

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

# Production image
FROM base AS production
CMD ["python", "main.py"]

# Development image
FROM base AS development
RUN uv sync --frozen --no-install-project

EXPOSE 8002
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
