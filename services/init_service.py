import logging
import os
from services.database import Database
from services.config_service import Config

# Configure logging
logger = logging.getLogger(__name__)

# Global database instance
_database = None

def get_database(config: Config):
    """Get the database instance"""
    global _database

    if (_database is None):
        _database = Database(config)

    return _database

