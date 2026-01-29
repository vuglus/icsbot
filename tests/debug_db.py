import sys
import os

# Add the parent directory to the path so we can import from services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import init_db, set_db_path

# Use an in-memory database for testing
set_db_path(':memory:')

# Initialize the database
print("Initializing database...")
init_db()
print("Database initialized successfully!")