import os
import logging
from flask import Flask
from flask_smorest import Api
from services.config_service import load_config, Config
from services.api_service import get_app, initialize_api
from services.init_service import get_database
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService
import services.background_service as background_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)
config = Config(load_config(
    os.environ.get('CONFIG_PATH', './config/config.yml')
))

# Get Flask app instance
app = get_app()
auth_service = AuthService(app, config)

# Initialize services
db = get_database(config.get('DB_PROVIDER'), config.get('DB_PATH'))

calendar_service = CalendarService(db)
notification_service = NotificationService(db)

# Configure Flask-Smorest API
app.config["API_TITLE"] = "ICS Bot API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/api"
app.config["OPENAPI_REDOC_PATH"] = "/redoc"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Initialize Flask-Smorest API
api = Api(app)

# Initialize API endpoints
initialize_api(api, auth_service, calendar_service, notification_service)

# Print debug info
print(f"App has {len(app.view_functions)} view functions")
for endpoint, view_func in app.view_functions.items():
    print(f"  {endpoint} -> {view_func}")


if __name__ == '__main__':
    # Set global variables for background service
    import services.background_service as background_service
    background_service.SYNC_INTERVAL_MINUTES = int(config.get('SYNC_INTERVAL_MINUTES', 15))
    background_service.NOTIFY_INTERVAL_SECONDS = int(config.get('NOTIFY_INTERVAL_SECONDS', 60))
    
    # Set global variables for ICS parser
    import services.ics_parser as ics_parser
    ics_parser.TIMEZONE_DEFAULT = os.environ.get('TIMEZONE_DEFAULT', 'UTC')

    # # Create users and calendars from config
    if config.get('calendars'):
        for user_id, calendar_url in config.get('calendars').items():
            user = db.getUser().create_user(user_id)
            db.getCalendar().create_calendar(user.id, calendar_url)
    # Import background service after setting up entities to avoid circular imports
    from services.background_service import start_background_processes
    
    # Start background processes
    scheduler = start_background_processes(
        calendar_service,
        notification_service
    )
    
    logger.info("ICS-Gate application initialized successfully")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5800, debug=False)