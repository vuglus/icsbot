import logging
from flask import Flask
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService

# Configure logging
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)

def get_app():
    """Get the Flask app instance"""
    return app

def initialize_api(
        api, 
        auth_service: AuthService, 
        calendar_service: CalendarService, 
        notification_service: NotificationService
    ):
    """Initialize API endpoints with flask-smorest"""
    from .api_endpoints import create_endpoints
    
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