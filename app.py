import logging
from flask_smorest import Api
from services.config_service import Config
from services.api_service import App
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService
from services.database import Database
from services.database_provider import DatabaseProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)
config = Config({})
# Initialize services
provider = DatabaseProvider(config)
db = Database(provider, config)
calendar_service = CalendarService(db, tzone=config.getTZone())
notification_service = NotificationService(db)

app = App()
auth_service = AuthService(app.get_app(), config)
# Initialize API endpoints
app.initialize_api(
    Api(app.get_app()), 
    auth_service, 
    calendar_service, 
    notification_service
)

if __name__ == '__main__':
    logger.info("ICS-Gate application initialized successfully")    
    # Run Flask app
    app.get_app().run(host='0.0.0.0', port=config.get_port() , debug=False)
