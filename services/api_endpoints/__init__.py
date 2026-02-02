"""
API Endpoints Package
Each API endpoint is implemented in a separate file.
"""

from flask import Flask
from .health_endpoint import health_blp as health_blueprint
from .calendar_endpoint import calendar_blp as calendar_blueprint
from .notification_endpoint import notification_blp as notification_blueprint
from .pending_events_endpoint import pending_events_blp as pending_events_blueprint
from .openapi_endpoint import openapi_blp as openapi_blueprint

def get_endpoints():
    """
    Get all API endpoint blueprints.
    
    Returns:
        dict: A dictionary of blueprints
    """
    # Dictionary to store blueprints
    blueprints = {}
    
    # Register each endpoint blueprint
    blueprints['health'] = health_blueprint
    blueprints['calendar'] = calendar_blueprint
    blueprints['notification'] = notification_blueprint
    blueprints['pending_events'] = pending_events_blueprint
    blueprints['openapi'] = openapi_blueprint
    
    return blueprints