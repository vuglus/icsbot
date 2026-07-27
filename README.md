# ICS-Gate

A service for processing ICS/CalDAV calendars and sending event notifications to Telegram/Max chats.

## Features

- ICS calendar parsing (load, notify, forget - no event storage)
- CalDAV support (on-demand event fetching)
- Chat-based calendar registration (Telegram or Max)
- Automatic event notification via chat bot API
- Sent notification tracking (deduplication)
- REST API with API key authentication
- SQLite and YDB persistence
- Docker deployment

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ics-gate
   ```

2. Configure environment variables (see below)

3. Run with Docker:
   ```bash
   docker-compose up -d
   ```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` / `EXT_PORT` | `8080` | Flask listen port |
| `API_KEY` | - | API key for authentication |
| `DB_PROVIDER` | - | `sqlite` or `ydb` |
| `DB_PATH` | - | SQLite file path or YDB database path |
| `DB_ENDPOINT` | - | YDB endpoint (e.g., `localhost:2136`) |
| `TG_BOT_URL` | - | Telegram bot API URL for sending notifications |
| `TG_BOT_TOKEN` | - | Token for Telegram bot authorization |
| `NOTIFY_BEFORE_MINUTES` | `15` | How far ahead to look for pending events |
| `NOTIFY_INTERVAL_SECONDS` | `60` | Background notification check interval |
| `TIMEZONE_DEFAULT` | `UTC` | Default timezone for parsing naive datetimes |

## API Usage

### Create a calendar

```bash
curl -X POST -H "X-Auth-Token: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123456789", "chat_type": "tg", "url": "https://calendar.google.com/calendar/ical/.../basic.ics"}' \
  http://localhost:8080/calendars
```

### Get pending events

```bash
curl -H "X-Auth-Token: your-api-key" \
  http://localhost:8080/events/pending?user_id=123456789
```

### List calendars

```bash
curl -H "X-Auth-Token: your-api-key" \
  http://localhost:8080/calendars
```

### Delete a calendar

```bash
curl -X DELETE -H "X-Auth-Token: your-api-key" \
  http://localhost:8080/calendars/<calendar_id>
```

### Health check

```bash
curl http://localhost:8080/health
```

## Architecture

### Database Tables

1. **calendars** - Registered calendars with chat bindings
   - `id` - Primary key
   - `user_id` - User identifier (kept for backward compatibility)
   - `chat_id` - Chat ID (Telegram or Max)
   - `chat_type` - Chat type (`tg` or `max`)
   - `url` - Calendar URL (ICS or CalDAV)
   - `client_type` - Client type (`ics` or `caldav`)
   - `timezone` - Calendar timezone
   - `last_sync_at` - Last sync timestamp
   - `sync_hash` - Sync hash (ICS only)

2. **sent_notifications** - Sent notification tracking
   - `id` - Primary key
   - `calendar_id` - Calendar reference
   - `event_uid` - Event UID
   - `chat_id` - Target chat
   - `event_data` - Full event JSON
   - `sent_at` - Sent timestamp

### Data Flow

1. **Calendar Registration**: API accepts `chat_id`, `chat_type`, and `url`
2. **Background Notification Check**: Iterates calendars with `chat_id`, fetches events for the notification window, checks `sent_notifications` for duplicates, sends to chat bot
3. **Pending Events API**: Fetches events on-demand, filters by user_id, returns not-yet-sent events
4. **ICS Mode**: Downloads and parses ICS, sends notifications, does not store events
5. **CalDAV Mode**: Fetches events via CalDAV protocol on-demand

## Development

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
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

```bash
pytest
```