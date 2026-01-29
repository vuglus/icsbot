# ICS-Gate

A service for processing ICS calendars and notifying external clients about upcoming events.

[![License](https://img.shields.io/github/license/.../ics-gate)](LICENSE)

## Features

- ICS calendar parsing and storage
- REST API with API key authentication
- Background synchronization and notification scheduling
- SQLite persistence
- Docker deployment

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ics-gate
   ```

2. Create a configuration file:
   ```bash
   cp config.example.yml config.yml
   # Edit config.yml with your settings
   ```

3. Run with Docker:
   ```bash
   docker-compose up -d
   ```

## Configuration

Create a `config.yml` file with your calendar URLs:

```yaml
api_key: "your-secret-api-key"
SYNC_INTERVAL_MINUTES: 15
NOTIFY_INTERVAL_SECONDS: 60

calendars:
  "user1": "https://calendar.google.com/calendar/ical/..."
  "user2": "https://outlook.office365.com/owa/calendar/..."
```

## API Usage

### Get pending events

```bash
curl -H "X-API-Key: your-api-key" http://localhost:5800/events/pending
```

### Mark notification as delivered

```bash
curl -X POST -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"delivered_at": "2023-06-15T09:30:00Z"}' \
  http://localhost:5800/notifications/123/delivered
```

## API Endpoints

### `GET /events/pending`

Retrieves events that are approaching and need to be notified to clients.

**Response:**
```json
{
  "events": [
    {
      "id": 123,
      "uid": "event-uid-123",
      "title": "Team Meeting",
      "description": "Weekly team meeting to discuss project progress",
      "location": "Conference Room 3",
      "start_datetime": "2023-06-15T10:00:00Z",
      "end_datetime": "2023-06-15T11:00:00Z",
      "all_day": false
    }
  ]
}
```

### `POST /notifications/{id}/delivered`

Confirms that a notification has been successfully delivered to the client.

**Request:**
```json
{
  "delivered_at": "2023-06-15T09:30:00Z"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Notification marked as delivered",
  "event_id": 123
}
```

### `GET /health`

Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-06-15T09:30:00Z",
  "version": "1.0.0"
}
```

## Environment Variables

- `ICS_GATE_API_KEY`: API key for authentication
- `SYNC_INTERVAL_MINUTES`: ICS synchronization frequency (default: 15)
- `NOTIFY_INTERVAL_SECONDS`: Notification check frequency (default: 60)
- `DB_PATH`: Path to SQLite database (default: ./icsgate.db)
- `CONFIG_PATH`: Path to YAML configuration file (default: ./config.yml)
- `TIMEZONE_DEFAULT`: Default timezone (default: UTC)

## Development

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for containerized deployment)

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Testing

Run tests with pytest:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.