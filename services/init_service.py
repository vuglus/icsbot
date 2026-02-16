import logging
import os
from services.database import Database

# Configure logging
logger = logging.getLogger(__name__)

# Global database instance
_database = None

def get_database(provider: str, path: str):
    """Get the database instance"""
    global _database

    if (_database is None):
        _database = Database(provider, path)

    return _database

