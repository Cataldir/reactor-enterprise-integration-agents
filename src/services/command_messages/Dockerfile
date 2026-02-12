# Pattern 4: Command Messages
FROM python:3.11-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Copy dependency files and install
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy shared utilities
COPY src/shared/ ./src/shared/

# Copy service code
COPY src/services/command_messages/ ./src/services/command_messages/

WORKDIR /app/src/services/command_messages

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

# Production image
FROM base AS production
CMD ["python", "main.py"]

# Development image
FROM base AS development
RUN uv sync --frozen --no-install-project

EXPOSE 8003
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
