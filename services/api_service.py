import logging
from flask import Flask
from .notification_service import get_pending_events_for_api

# Configure logging
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)

def get_app():
    """Get the Flask app instance"""
    return app

def initialize_api(api):
    """Initialize API endpoints with flask-smorest"""
    from .api_endpoints import get_endpoints
    
    # Get all endpoints
    blueprints = get_endpoints()
    
    # Register blueprints with the API
    for name, blueprint in blueprints.items():
        if hasattr(blueprint, 'name') and blueprint.name:
            api.register_blueprint(blueprint)