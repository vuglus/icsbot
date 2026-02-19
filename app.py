import logging
from flask import Flask
from flask_smorest import Api
from services.config_service import Config
from services.api_service import get_app, initialize_api
from services.init_service import get_database
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)
config = Config({})

# Get Flask app instance
app = get_app()
auth_service = AuthService(app, config)

# Initialize services
db = get_database(config)

calendar_service = CalendarService(db, tzone=config.getTZone())
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


def handler(event, context):
    print("Получен event:", event)
    calendar_service.sync_all_calendars()
    return {
        'statusCode': 200,
        'body': '{"message": "Запрос обработан триггером"}'
    }

if __name__ == '__main__':
    logger.info("ICS-Gate application initialized successfully")    
    # Run Flask app
    app.run(host='0.0.0.0', port=config.get_port() , debug=False)