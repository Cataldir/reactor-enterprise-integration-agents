# Pattern 2: Pipes and Filters
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ ./shared/

# Copy pattern-specific code
COPY pattern-2-pipes-filters/ ./pattern-2-pipes-filters/

WORKDIR /app/pattern-2-pipes-filters

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Production image
FROM base as production
CMD ["python", "main.py"]

# Development image
FROM base as development
COPY requirements-dev.txt /app/
RUN pip install --no-cache-dir -r /app/requirements-dev.txt

EXPOSE 8001
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
