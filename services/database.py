import sqlite3
import os
import logging
from datetime import datetime
from typing import List

# Configure logging
logger = logging.getLogger(__name__)

# Global variables
_DB_PATH = os.environ.get('DB_PATH', 'icsgate.db')

def set_db_path(db_path: str):
    """Set the database path"""
    global _DB_PATH
    _DB_PATH = db_path

def get_db_connection():
    """Get a database connection"""
    print(f"Connecting to database: {_DB_PATH}")
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Database initialization
def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create calendars table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            last_sync_at TIMESTAMP,
            sync_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, url)
        )
    ''')
    
    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
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
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_calendars_user_id ON calendars (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_calendar_id ON events (calendar_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_start_datetime ON events (start_datetime)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_notified ON events (notified)')
    
    # Check if tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables created: {[table[0] for table in tables]}")
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Database models
class User:
    def __init__(self, id: int, user_id: str, created_at: str):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at

class Calendar:
    def __init__(self, id: int, user_id: int, url: str, last_sync_at: str, sync_hash: str):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.last_sync_at = last_sync_at
        self.sync_hash = sync_hash

class Event:
    def __init__(self, id: int, calendar_id: int, uid: str, title: str, description: str,
                 location: str, start_datetime: str, end_datetime: str, all_day: bool, notified: bool, user_id: str = None):
        self.id = id
        self.calendar_id = calendar_id
        self.uid = uid
        self.title = title
        self.description = description
        self.location = location
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.all_day = all_day
        self.notified = notified
        self.user_id = user_id

# Database operations
def create_user(user_id: str) -> User:
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (user_id) VALUES (?)',
            (user_id,)
        )
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables in database: {[table[0] for table in tables]}")
        
        conn.commit()
        user_row_id = cursor.lastrowid
        logger.info(f"Created user with ID {user_row_id}")
        return User(user_row_id, user_id, datetime.now().isoformat())
    except sqlite3.IntegrityError:
        logger.warning(f"User {user_id} already exists")
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return User(row['id'], row['user_id'], row['created_at'])
    finally:
        conn.close()

def create_calendar(user_id: int, url: str) -> Calendar:
    """Create a new calendar for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO calendars (user_id, url) VALUES (?, ?)',
            (user_id, url)
        )
        conn.commit()
        calendar_id = cursor.lastrowid
        logger.info(f"Created calendar {calendar_id} for user {user_id}")
        calendar = Calendar(calendar_id, user_id, url, None, None)
    except sqlite3.IntegrityError as e:
        # Handle duplicate calendar entry
        conn.rollback()
        logger.warning(f"Calendar for user {user_id} with URL {url} already exists: {e}")
        cursor.execute(
            'SELECT * FROM calendars WHERE user_id = ? AND url = ?',
            (user_id, url)
        )
        row = cursor.fetchone()
        if row:
            calendar = Calendar(row['id'], row['user_id'], row['url'],
                                  row['last_sync_at'], row['sync_hash'])
        else:
            raise Exception("Failed to retrieve existing calendar")
    finally:
        conn.close()
    
    return calendar

def get_calendars() -> List[Calendar]:
    """Get all calendars"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM calendars')
    rows = cursor.fetchall()
    conn.close()
    
    return [Calendar(row['id'], row['user_id'], row['url'], 
                     row['last_sync_at'], row['sync_hash']) for row in rows]

def update_calendar_sync(calendar_id: int, sync_hash: str):
    """Update calendar sync metadata"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE calendars SET last_sync_at = ?, sync_hash = ? WHERE id = ?',
        (datetime.now().isoformat(), sync_hash, calendar_id)
    )
    conn.commit()
    conn.close()
    
    logger.info(f"Updated sync metadata for calendar {calendar_id}")

def create_event(calendar_id: int, uid: str, title: str, description: str, 
                location: str, start_datetime: str, end_datetime: str, all_day: bool) -> Event:
    """Create a new event"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO events (calendar_id, uid, title, description, location, 
                           start_datetime, end_datetime, all_day)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (calendar_id, uid, title, description, location, 
          start_datetime, end_datetime, all_day))
    
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    
    logger.info(f"Created event {event_id} for calendar {calendar_id}")
    return Event(event_id, calendar_id, uid, title, description, location,
                 start_datetime, end_datetime, all_day, False)

def get_pending_events(user_id: str = None) -> List[Event]:
    """Get events that need to be notified"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate notification window (10 minutes before event by default)
    notify_before_minutes = int(os.environ.get('NOTIFY_BEFORE_MINUTES', 10))
    
    # Build query based on whether user_id is provided
    if user_id:
        # First check if user exists
        cursor.execute('SELECT id FROM users WHERE user_id = ?', (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            raise ValueError(f"User {user_id} not found")
        
        cursor.execute('''
            SELECT e.*, u.user_id as user_id FROM events e
            JOIN calendars c ON e.calendar_id = c.id
            JOIN users u ON c.user_id = u.id
            WHERE e.notified = FALSE
              AND julianday(e.start_datetime) <= julianday(datetime('now')) + (? / 1440.0)
              AND julianday(e.start_datetime) > julianday(datetime('now'))
              AND u.user_id = ?
            ORDER BY e.start_datetime ASC
        ''', (notify_before_minutes, user_id))
    else:
        # Debug output for datetime calculations
        cursor.execute("SELECT datetime('now') as now")
        now_row = cursor.fetchone()
        now_time = now_row['now']
        print(f"Current time: {now_time}")
        print(f"Notification window: {notify_before_minutes} minutes")
        
        cursor.execute('''
            SELECT *,
                   julianday(start_datetime) as start_jd,
                   julianday(datetime('now')) as now_jd,
                   julianday(datetime('now')) + (? / 1440.0) as window_end_jd
            FROM events
            WHERE notified = FALSE
        ''', (notify_before_minutes,))
        
        all_events = cursor.fetchall()
        print(f"Total events: {len(all_events)}")
        for event in all_events:
            start_jd = event['start_jd']
            now_jd = event['now_jd']
            window_end_jd = event['window_end_jd']
            print(f"  - Event {event['id']}: {event['title']} at {event['start_datetime']}")
            print(f"    Start JD: {start_jd}, Now JD: {now_jd}, Window End JD: {window_end_jd}")
            print(f"    Is future: {start_jd > now_jd}, Is within window: {start_jd <= window_end_jd}")
        
        cursor.execute('''
            SELECT e.*, u.user_id as user_id FROM events e
            JOIN calendars c ON e.calendar_id = c.id
            JOIN users u ON c.user_id = u.id
            WHERE e.notified = FALSE
              AND julianday(e.start_datetime) <= julianday(datetime('now')) + (? / 1440.0)
              AND julianday(e.start_datetime) > julianday(datetime('now'))
            ORDER BY e.start_datetime ASC
        ''', (notify_before_minutes,))
    
    rows = cursor.fetchall()
    
    # Debug output
    print(f"Found {len(rows)} pending events")
    for row in rows:
        print(f"  - Event: {row['title']} at {row['start_datetime']}")
    
    conn.close()
    
    events = []
    for row in rows:
        event = Event(row['id'], row['calendar_id'], row['uid'], row['title'],
                      row['description'], row['location'], row['start_datetime'],
                      row['end_datetime'], row['all_day'], row['notified'],
                      row['user_id'] if 'user_id' in row.keys() else None)
        events.append(event)
    
    return events

def mark_event_notified(event_id: int) -> bool:
    """Mark an event as notified"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE events SET notified = TRUE WHERE id = ? AND notified = FALSE',
        (event_id,)
    )
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if updated:
        logger.info(f"Marked event {event_id} as notified")
    else:
        logger.warning(f"Event {event_id} not found or already notified")
    
    return updated