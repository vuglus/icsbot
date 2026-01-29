# ICS-Gate Database Design

## Overview

The ICS-Gate service uses SQLite for data persistence. The database contains three main tables:
1. Users - Stores user identifiers
2. Calendars - Stores calendar information and synchronization metadata
3. Events - Stores parsed calendar events with notification status

## Database Schema

### Users Table
```
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Columns:
- id: Primary key (auto-incrementing integer)
- user_id: Unique identifier for the user (from config.yml)
- created_at: Timestamp when the user was created

### Calendars Table
```
CREATE TABLE calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    last_sync_at TIMESTAMP,
    sync_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(user_id, url)
);
```

Columns:
- id: Primary key (auto-incrementing integer)
- user_id: Foreign key referencing users.id
- url: ICS calendar URL
- last_sync_at: Timestamp of last successful synchronization
- sync_hash: Hash of last synced calendar content (for change detection)
- created_at: Timestamp when the calendar was added

### Events Table
```
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calendar_id INTEGER NOT NULL,
    uid TEXT NOT NULL,
    title TEXT,
    description TEXT,
    location TEXT,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    all_day BOOLEAN DEFAULT FALSE,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (calendar_id) REFERENCES calendars (id) ON DELETE CASCADE
);
```

Columns:
- id: Primary key (auto-incrementing integer)
- calendar_id: Foreign key referencing calendars.id
- uid: Unique identifier from the ICS file
- title: Event title
- description: Event description from ICS DESCRIPTION field
- location: Event location from ICS LOCATION field
- start_datetime: Event start time
- end_datetime: Event end time
- all_day: Boolean indicating if this is an all-day event
- notified: Boolean indicating if notification has been sent
- created_at: Timestamp when the event was added

## Indexes

To optimize query performance, the following indexes should be created:

```
CREATE INDEX idx_calendars_user_id ON calendars (user_id);
CREATE INDEX idx_events_calendar_id ON events (calendar_id);
CREATE INDEX idx_events_start_datetime ON events (start_datetime);
CREATE INDEX idx_events_notified ON events (notified);
```

## Relationships

```
users 1 ---< calendars 1 ---< events
```

Each user can have multiple calendars, and each calendar can have multiple events.

## Data Flow

1. Users are created based on config.yml entries
2. Calendars are associated with users based on config.yml
3. Events are parsed from ICS files and associated with calendars
4. Events are marked as notified when clients retrieve them via API
5. Notified events are marked as delivered when clients confirm via API