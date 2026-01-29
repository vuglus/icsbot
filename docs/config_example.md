# Configuration File Example

## Overview

This document shows the expected format for the ICS-Gate configuration file.

## config.yml

```yaml
# API key for accessing the service
api_key: "your-secret-api-key-here"

# ICS synchronization interval in minutes
SYNC_INTERVAL_MINUTES: 15

# Notification check interval in seconds
NOTIFY_INTERVAL_SECONDS: 60

# Path to SQLite database
DB_PATH: "/data/icsgate.db"

# Default timezone
TIMEZONE_DEFAULT: "UTC"

# Calendar configurations
calendars:
  # User ID mapped to calendar URL
  "user1": "https://calendar.google.com/calendar/ical/..."
  "user2": "https://outlook.office365.com/owa/calendar/..."
  "5164400": "https://example.com/calendar.ics"
```

## Environment Variables

The following environment variables can be used to override configuration values:

- `ICS_GATE_API_KEY`: API key for authentication
- `SYNC_INTERVAL_MINUTES`: ICS synchronization frequency
- `NOTIFY_INTERVAL_SECONDS`: Notification check frequency
- `DB_PATH`: Path to SQLite database
- `TIMEZONE_DEFAULT`: Default timezone
- `CONFIG_PATH`: Path to YAML configuration file

## Configuration Loading Priority

1. Environment variables (highest priority)
2. Configuration file values
3. Default values (lowest priority)

## Validation

### Required Fields
- `api_key`: Must be a non-empty string
- `calendars`: Must be a dictionary with at least one entry

### Optional Fields with Defaults
- `SYNC_INTERVAL_MINUTES`: Default 15
- `NOTIFY_INTERVAL_SECONDS`: Default 60
- `DB_PATH`: Default "./icsgate.db"
- `TIMEZONE_DEFAULT`: Default "UTC"

## Example with Minimal Configuration

```yaml
api_key: "secret-key"
calendars:
  "user1": "https://example.com/calendar.ics"
```

## Multi-user Example

```yaml
api_key: "super-secret-key"
SYNC_INTERVAL_MINUTES: 10
NOTIFY_INTERVAL_SECONDS: 30
DB_PATH: "/var/lib/icsgate/database.db"
TIMEZONE_DEFAULT: "Europe/Moscow"

calendars:
  "john_doe": "https://calendar.google.com/calendar/ical/john/private-123/basic.ics"
  "jane_smith": "https://calendar.google.com/calendar/ical/jane/private-456/basic.ics"
  "company_events": "https://company.com/events.ics"
```

## Security Considerations

### API Key
- Should be at least 32 characters long
- Should contain a mix of letters, numbers, and symbols
- Should be stored securely (environment variable preferred)

### Calendar URLs
- HTTPS URLs are recommended
- Avoid including credentials in URLs
- Validate URL format

## File Permissions

### Configuration File
- Should be readable only by the application user
- Recommended permissions: 600 (rw-------)
- Store outside of web root

### Database File
- Should be readable and writable by the application user
- Recommended permissions: 600 (rw-------)
- Store in a secure location