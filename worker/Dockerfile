# Multi-stage Dockerfile for Retail Kiosk Worker Service
# Based on Python 3.11 with optimized layers for production deployment

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Create minimal production image
# ============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app \
    C_FORCE_ROOT=true

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR $APP_HOME

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Create logs directory with proper permissions
RUN mkdir -p logs && chown -R appuser:appuser logs

# Switch to non-root user
USER appuser

# Health check - verify Celery worker is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD celery -A celery_app inspect ping -d celery@$HOSTNAME || exit 1

# Run Celery worker
# Using -A celery_app to point to the Celery app instance
# --loglevel can be overridden via docker-compose or kubernetes
# --concurrency controls the number of worker processes
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--concurrency=2"]
