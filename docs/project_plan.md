# ICS-Gate Project Plan

## Project Overview

ICS-Gate is a service that processes ICS calendars and notifies external clients about upcoming events. The service will:

1. Store and parse ICS calendars with API_KEY authorization
2. Run background processes for ICS synchronization and notification scheduling
3. Provide API endpoints for clients to retrieve pending notifications

## Configuration Structure

The service will use the following configuration files:

### config.yml
```yaml
calendars:
  <user_id>: <calendar_url>
```

### Environment Variables
- `ICS_GATE_API_KEY` - Key for API access
- `SYNC_INTERVAL_MINUTES` - ICS synchronization frequency
- `NOTIFY_INTERVAL_SECONDS` - Notification check frequency
- `DB_PATH` - Path to SQLite database
- `TIMEZONE_DEFAULT` - Default timezone
- `CONFIG_PATH` - Path to YAML configuration file

## Database Schema

### Users Table
- user_id (Primary Key)

### Calendars Table
- id (Primary Key)
- user_id (Foreign Key to Users)
- url
- last_sync_at
- sync_hash

### Events Table
- id (Primary Key)
- calendar_id (Foreign Key to Calendars)
- uid
- title
- start_datetime
- end_datetime
- all_day
- notified (Boolean)

## API Endpoints

### Authentication
API key can be passed in headers or GET parameters

### Endpoints
- `GET /events/pending` - Returns events that need notification
- `POST /notifications/{id}/delivered` - Confirm notification delivery

## Background Processes

1. **ICS Synchronization** - Periodically loads calendars from YAML config and updates events
2. **Notification Scheduler** - Checks for upcoming events and marks them for notification

## Docker Configuration

- Separate container for ICS-Gate
- Volume mount for SQLite database persistence

## Implementation Steps

1. Create project structure and configuration files
2. Design database schema
3. Implement ICS parsing and synchronization
4. Develop REST API with authentication
5. Create background processes
6. Implement notification management endpoints
7. Add logging and error handling
8. Create Docker configuration
9. Test functionality
10. Document API and usage