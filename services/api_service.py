import logging
from flask import Flask
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService
from .api_endpoints import create_endpoints
from api_endpoints.health_endpoint import health_blp as health_blueprint
from api_endpoints.calendar_endpoint import create_calendar_blueprint
from api_endpoints.cron_endpoint import handle_cron_blueprint
from api_endpoints.notification_endpoint import create_notification_blueprint
from api_endpoints.pending_events_endpoint import create_pending_events_blueprint
from api_endpoints.openapi_endpoint import openapi_blp as openapi_blueprint

# Configure logging
logger = logging.getLogger(__name__)

# Flask app initialization

class App:
    def __init__(self):
        self.app = Flask(__name__)
        """Get the Flask app instance"""
        # Configure Flask-Smorest API
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"
        self.app.config["OPENAPI_URL_PREFIX"] = "/api"
        self.app.config["OPENAPI_REDOC_PATH"] = "/redoc"
        self.app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
        self.app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"    

    def get_app(self):
        
        return self.app

    def initialize_api(
            self,
            api,             
            auth_service: AuthService, 
            calendar_service: CalendarService, 
            notification_service: NotificationService
        ):
        # Create all endpoints with injected dependencies
        blueprints = create_endpoints(
            auth_service, 
            calendar_service, 
            notification_service
        )
        
        # Register blueprints with the API
        for name, blueprint in blueprints.items():
            if hasattr(blueprint, 'name') and blueprint.name:
                api.register_blueprint(blueprint)

    def create_endpoints(auth_service, calendar_service, notification_service):
        """
        Create all API endpoint blueprints with injected dependencies.
        
        Args:
            auth_service: Authentication service instance
            calendar_service: Calendar service instance
            notification_service: Notification service instance
            
        Returns:
            dict: A dictionary of blueprints
        """
        # Dictionary to store blueprints
        blueprints = {}
        
        # Register each endpoint blueprint
        blueprints['health'] = health_blueprint
        blueprints['calendar'] = create_calendar_blueprint(auth_service, calendar_service)
        blueprints['notification'] = create_notification_blueprint(auth_service, notification_service)
        blueprints['pending_events'] = create_pending_events_blueprint(auth_service, notification_service)
        blueprints['openapi'] = openapi_blueprint
        blueprints['cron'] = handle_cron_blueprint(auth_service, calendar_service)
        
        return blueprints