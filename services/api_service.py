import logging
from flask import Flask
from .notification_service import get_pending_events_for_api

# Configure logging
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)

def register_endpoints_with_apispec(app):
    """Register endpoints with FlaskApiSpec"""
    # Import and register API endpoints
    from .api_endpoints.health_endpoint import register_health_endpoint
    from .api_endpoints.pending_events_endpoint import register_pending_events_endpoint
    from .api_endpoints.notification_endpoint import register_notification_endpoint
    from .api_endpoints.calendar_endpoint import register_calendar_endpoint
    from .api_endpoints.openapi_endpoint import register_openapi_endpoint

    # Register all endpoints
    register_health_endpoint(app)
    register_pending_events_endpoint(app)
    register_notification_endpoint(app)
    register_calendar_endpoint(app)
    register_openapi_endpoint(app)

def get_app():
    """Get the Flask app instance"""
    return app