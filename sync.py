import logging
from services.config_service import Config
from services.api_service import get_app
from services.init_service import get_database
from services.calendar_service import CalendarService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)
config = Config({})

# Get Flask app instance
app = get_app()
# Initialize services
db = get_database(config)

calendar_service = CalendarService(db, tzone=config.getTZone())

if __name__ == '__main__':
    logger.info("Application initialized successfully")
    calendar_service.sync_all_calendars()    
    logger.info("ICS-Sync done")
