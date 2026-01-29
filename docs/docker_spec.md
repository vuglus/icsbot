# Docker Configuration Specification

## Overview

ICS-Gate will run in a Docker container with persistent storage for the SQLite database.

## Dockerfile

### Base Image
Use a lightweight Python base image:
```dockerfile
FROM python:3.9-slim
```

### Dependencies
- Install Python dependencies from requirements.txt
- Use multi-stage build to minimize image size

### Application Setup
- Create non-root user for security
- Copy application code
- Set working directory
- Expose appropriate port

### Runtime Configuration
- Use environment variables for configuration
- Set proper entrypoint

## Docker Compose

### Services
- Single service for ICS-Gate

### Volumes
- Persistent volume for SQLite database
- Configuration file mounting (optional)

### Environment Variables
- All configuration variables passed from configuration file config.yml

config.yml
  calendars:
    5164400: https://calendar.google.com/calendar/ical/
  api_key: your-api-key-here
  SYNC_INTERVAL_MINUTES: 15
  NOTIFY_INTERVAL_SECONDS: 60
  DB_PATH: /data/icsgate.db

## Dockerfile Content

```dockerfile
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
COPY . ./ics-gate
WORKDIR /home/app/ics-gate

# Expose port
EXPOSE 5800

# Environment variables
ENV DB_PATH=/data/icsgate.db
ENV CONFIG_PATH=/config/config.yml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5800/health || exit 1

# Run application
ENTRYPOINT ["python", "app.py"]
```

## Docker Compose File

```yaml
version: '3.8'

services:
  ics-gate:
    build: .
    container_name: ics-gate
    ports:
      - "8000:8000"
    environment:
      - CONFIG_PATH=/config/config.yml
      - TIMEZONE_DEFAULT=UTC
    volumes:
      - icsgate_data:/data
      - ./config.yml:/config/config.yml:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  icsgate_data:
```

## Volume Management

### Data Volume
- Mount persistent volume to `/data` directory
- SQLite database stored at `/data/icsgate.db`
- Set proper permissions for database file

### Configuration Volume
- Mount configuration file to `/config/config.yml`
- Use read-only mount for security
- Validate configuration file format

## Environment Variables

### Required
- `ICS_GATE_API_KEY`: API key for authentication

### Optional with Defaults
- `SYNC_INTERVAL_MINUTES`: 15
- `NOTIFY_INTERVAL_SECONDS`: 60
- `DB_PATH`: `/data/icsgate.db`
- `CONFIG_PATH`: `/config/config.yml`
- `TIMEZONE_DEFAULT`: UTC

## Security Considerations

### Image Security
- Use official Python base image
- Run as non-root user
- Minimize installed packages
- Regularly update base images

### Runtime Security
- Don't run in privileged mode
- Use read-only root filesystem where possible
- Limit capabilities
- Use secrets for sensitive data

## Resource Constraints

### CPU and Memory
- Set reasonable limits to prevent resource exhaustion
- Monitor resource usage in production

### Network
- Limit network access to only required ports
- Use internal networks for multi-container setups

## Health Checks

### Container Health
- HTTP endpoint check on `/health`
- Database connectivity check
- Configuration file accessibility check

### Monitoring
- Log health check results
- Alert on repeated failures
- Include health information in logs

## Build Process

### CI/CD Integration
- Automated builds on code changes
- Security scanning of images
- Version tagging

### Multi-architecture Support
- Build for multiple architectures if needed
- Use buildx for cross-platform builds

## Deployment Considerations

### Scaling
- Stateful service - single instance recommended
- Use external database for multi-instance deployments

### Updates
- Rolling updates with proper shutdown handling
- Backup database before major updates
- Test updates in staging environment

### Backup
- Regular database backups
- Configuration file backups
- Document backup and restore procedures