import sqlite3
from datetime import datetime, timedelta

# Create a test database
conn = sqlite3.connect(':memory:')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Create events table
cursor.execute('''
    CREATE TABLE events (
        id INTEGER PRIMARY KEY,
        start_datetime TIMESTAMP NOT NULL,
        notified BOOLEAN DEFAULT FALSE
    )
''')

# Insert a test event that should be within the notification window
# Get current time from SQLite
cursor.execute("SELECT datetime('now') as now")
now_row = cursor.fetchone()
now_time = now_row['now']
print(f"Current time in DB: {now_time}")

# Create event for 5 minutes in the future using SQLite's time
cursor.execute("SELECT datetime(datetime('now'), '+5 minutes') as future_time")
future_row = cursor.fetchone()
future_time = future_row['future_time']
print(f"Creating event for: {future_time}")

cursor.execute('''
    INSERT INTO events (id, start_datetime) VALUES (1, ?)
''', (future_time,))

# Check if the event is within the notification window
# Notification window: current time to current time + 60 minutes
notify_before_minutes = 60

cursor.execute("SELECT datetime(datetime('now')) as now")
now_row = cursor.fetchone()
now_time = now_row['now']
print(f"Current time in DB: {now_time}")

cursor.execute("SELECT datetime(datetime('now'), '+' || ? || ' minutes') as window_end", (str(notify_before_minutes),))
window_end_row = cursor.fetchone()
window_end_time = window_end_row['window_end']
print(f"Window end time in DB: {window_end_time}")

cursor.execute('''
    SELECT *, 
           julianday(start_datetime) as start_jd,
           julianday(datetime('now')) as now_jd,
           julianday(datetime('now', '+' || ? || ' minutes')) as window_end_jd
    FROM events
    WHERE notified = FALSE
      AND julianday(start_datetime) <= julianday(datetime('now', '+' || ? || ' minutes'))
      AND julianday(start_datetime) > julianday(datetime('now'))
''', (str(notify_before_minutes), str(notify_before_minutes)))

events = cursor.fetchall()
print(f"Found {len(events)} pending events")
for event in events:
    print(f"  - Event {event['id']}: {event['start_datetime']}")
    print(f"    Start JD: {event['start_jd']}, Now JD: {event['now_jd']}, Window End JD: {event['window_end_jd']}")
    print(f"    Is future: {event['start_jd'] > event['now_jd']}, Is within window: {event['start_jd'] <= event['window_end_jd']}")

conn.close()