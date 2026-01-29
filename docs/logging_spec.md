# Logging and Error Handling Specification

## Overview

This document outlines the logging and error handling strategy for ICS-Gate.

## Logging Framework

### Python Logging Module
Use Python's built-in `logging` module for all logging needs.

### Log Levels
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General information about program execution
- **WARNING**: Potentially harmful situations
- **ERROR**: Error events that might still allow the application to continue
- **CRITICAL**: Serious errors that may prevent the application from continuing

### Log Format
```
[%(asctime)s] %(levelname)s in %(module)s: %(message)s
```

With additional context:
- Timestamp in ISO 8601 format
- Log level
- Module name
- Message
- Optional context data

## Logger Configuration

### Application Logger
- Name: `icsgate`
- Level: INFO by default, configurable via environment variable
- Handlers: Console and file handlers

### Component Loggers
- `icsgate.sync`: ICS synchronization
- `icsgate.api`: REST API
- `icsgate.scheduler`: Background processes
- `icsgate.db`: Database operations

## Log Storage

### File Location
- Default: `/var/log/icsgate/` in Docker, `./logs/` in development
- Configurable via `LOG_PATH` environment variable

### File Rotation
- Daily rotation
- Keep 30 days of logs
- Maximum file size: 10MB

### Log Content

#### ICS Synchronization Logs
```python
logger.info("Starting sync for calendar %s", calendar_url)
logger.debug("Parsing %d events from calendar", event_count)
logger.warning("Failed to download calendar %s: %s", calendar_url, error)
logger.error("Database error during sync: %s", error)
```

#### API Request Logs
```python
logger.info("API request: %s %s from %s", method, path, client_ip)
logger.info("Authentication success for API key ending in %s", api_key[-4:])
logger.warning("Authentication failed from %s", client_ip)
```

#### Background Process Logs
```python
logger.info("Notification scheduler checking for events")
logger.debug("Found %d pending notifications", count)
logger.info("Marked %d events as notified", updated_count)
```

## Error Handling

### Exception Hierarchy
```
ICSException
├── ConfigurationError
├── DatabaseError
├── NetworkError
├── ParseError
└── AuthenticationError
```

### Error Response Format
```json
{
  "error": {
    "code": 500,
    "message": "Internal Server Error",
    "details": "Database connection failed"
  }
}
```

### HTTP Error Codes
- 400: Bad Request (invalid input)
- 401: Unauthorized (invalid API key)
- 404: Not Found (resource not found)
- 500: Internal Server Error (unexpected errors)
- 503: Service Unavailable (temporary issues)

## Error Handling Patterns

### API Error Handling
```python
try:
    # Process request
    result = process_request(data)
    return jsonify(result), 200
except AuthenticationError as e:
    logger.warning("Authentication failed: %s", e)
    return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
except ValidationError as e:
    logger.info("Invalid request: %s", e)
    return jsonify({"error": {"code": 400, "message": "Bad Request"}}), 400
except Exception as e:
    logger.error("Unexpected error: %s", e, exc_info=True)
    return jsonify({"error": {"code": 500, "message": "Internal Server Error"}}), 500
```

### Background Process Error Handling
```python
try:
    sync_calendar(calendar)
    logger.info("Successfully synced calendar %s", calendar.url)
except NetworkError as e:
    logger.warning("Network error for calendar %s: %s", calendar.url, e)
    # Continue with other calendars
except DatabaseError as e:
    logger.error("Database error for calendar %s: %s", calendar.url, e)
    # Alert for critical errors
except Exception as e:
    logger.critical("Unexpected error for calendar %s: %s", calendar.url, e)
    # Alert and continue
```

## Monitoring and Alerting

### Health Checks
- Database connectivity
- Calendar URL accessibility
- Recent sync status
- API responsiveness

### Metrics Collection
- Request count and response times
- Error rates by type
- Sync duration and success rate
- Notification processing count

### Alerting Thresholds
- Critical: Database connection failures
- Warning: High error rates (>5%)
- Info: Sync failures for individual calendars

## Log Analysis

### Key Metrics to Track
- Sync success rate
- API response times
- Error frequency by type
- Resource usage (CPU, memory)

### Log Aggregation
- Use structured logging (JSON format) for easier parsing
- Include correlation IDs for request tracing
- Tag logs with service and environment

## Security Logging

### Authentication Events
- Log failed authentication attempts
- Log successful authentication
- Alert on high frequency of failures

### Data Access
- Log access to sensitive data
- Log configuration changes
- Log administrative actions

## Performance Considerations

### Log Volume
- Avoid excessive DEBUG logging in production
- Use sampling for high-volume logs
- Implement log filtering

### Asynchronous Logging
- Use async handlers to prevent blocking
- Buffer logs to reduce I/O operations
- Separate logging from request processing

## Configuration

### Environment Variables
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_PATH`: Path to log files (default: ./logs/)
- `LOG_FORMAT`: Log format string
- `ENABLE_LOG_FILE`: Enable file logging (default: True)

### Configuration Example
```python
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s [%(pathname)s:%(lineno)d]",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "icsgate.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 30,
            "formatter": "detailed",
        }
    },
    "loggers": {
        "icsgate": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        }
    }
}
```

## Testing

### Log Testing
- Verify log messages for different scenarios
- Test log levels and filtering
- Validate log format and content

### Error Handling Testing
- Test all error conditions
- Verify error responses
- Check error logging
- Test recovery mechanisms

## Best Practices

### Logging Best Practices
- Log at appropriate levels
- Include contextual information
- Avoid logging sensitive data
- Use structured logging where possible
- Log external interactions

### Error Handling Best Practices
- Fail fast for unrecoverable errors
- Gracefully handle recoverable errors
- Provide meaningful error messages
- Don't expose internal details in error responses
- Log errors with sufficient context for debugging