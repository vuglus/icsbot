import logging
import os
from .database import init_db, create_user
from .config_service import load_config
from .calendar_service import create_calendar
from .background_service import start_background_processes

# Configure logging
logger = logging.getLogger(__name__)

def initialize_app(sync_interval_minutes: int, notify_interval_seconds: int):
    """Initialize the application"""
    logger.info("Initializing ICS-Gate application")
    
    # Set global variables for background service
    import services.background_service as background_service
    background_service.SYNC_INTERVAL_MINUTES = sync_interval_minutes
    background_service.NOTIFY_INTERVAL_SECONDS = notify_interval_seconds
    
    # Set global variables for ICS parser
    import services.ics_parser as ics_parser
    ics_parser.TIMEZONE_DEFAULT = os.environ.get('TIMEZONE_DEFAULT', 'UTC')
    
    # Initialize database
    init_db()
    
    # Load configuration
    config = load_config()
    
    # Create users and calendars from config
    if 'calendars' in config:
        for user_id, calendar_url in config['calendars'].items():
            user = create_user(user_id)
            create_calendar(user.id, calendar_url)
    
    # Start background processes
    scheduler = start_background_processes()
    
    logger.info("ICS-Gate application initialized successfully")
    
    return scheduler