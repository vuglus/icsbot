# Multi-stage build
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy application code
COPY --chown=app:app . ./ics-gate
WORKDIR /home/app/ics-gate

# Environment variables
ENV DB_PROVIDER=ydb
ENV DB_ENDPOINT=ydb-local:2136
ENV DB_PATH=/local
ENV EXT_PORT=8080
ENV TG_BOT_URL=
ENV TG_BOT_TOKEN=
# Expose port
EXPOSE ${EXT_PORT}


# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; import sys; sys.exit(0 if urllib.request.urlopen('http://localhost:${EXT_PORT:-8080}/health').status == 200 else 1)"

# Run application
ENTRYPOINT ["python", "app.py"]