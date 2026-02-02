import logging
from flask import jsonify, current_app
from services.config_service import get_api_key
from services.api_utils import validate_api_key
from services.api_docs import Blueprint

# Configure logging
logger = logging.getLogger(__name__)

# Create a blueprint for this endpoint
openapi_blp = Blueprint('openapi', __name__, url_prefix='/openapi')

@openapi_blp.route('.json', methods=['GET'])
@openapi_blp.doc(
    summary="Get OpenAPI specification",
    description="Returns the OpenAPI specification for the API"
)
def get_openapi_spec():
    """Get OpenAPI specification"""
    # Note: We don't require API key authentication for the OpenAPI spec
    # as it's typically public documentation
    
    # Try to get the auto-generated spec from Flask-Smorest
    try:
        # Get the spec from the Flask app
        if hasattr(current_app, 'extensions') and 'flask-smorest' in current_app.extensions:
            api = current_app.extensions['flask-smorest']
            openapi_spec = api.spec.to_dict()
        else:
            # Fallback to manual spec if auto-generation fails
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "ICS-Gate API",
                    "description": "API for managing ICS calendars and receiving event notifications",
                    "version": "1.0.0"
                },
                "servers": [
                    {
                        "url": "http://localhost:5800",
                        "description": "Local development server"
                    }
                ],
                "components": {
                    "securitySchemes": {
                        "ApiKeyAuth": {
                            "type": "apiKey",
                            "in": "header",
                            "name": "X-API-Key",
                            "description": "API key for authentication"
                        }
                    },
                    "schemas": {
                        "Error": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "integer"},
                                        "message": {"type": "string"}
                                    },
                                    "required": ["code", "message"]
                                }
                            }
                        },
                        "Calendar": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "user_id": {"type": "integer"},
                                "url": {"type": "string"},
                                "timezone": {"type": "string"},
                                "last_sync_at": {"type": "string", "nullable": True},
                                "sync_hash": {"type": "string", "nullable": True}
                            }
                        },
                        "Event": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "uid": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "location": {"type": "string"},
                                "start_datetime": {"type": "string"},
                                "end_datetime": {"type": "string"},
                                "all_day": {"type": "boolean"},
                                "user_id": {"type": "string"},
                                "calendar_timezone": {"type": "string"}
                            }
                        }
                    }
                },
                "security": [
                    {
                        "ApiKeyAuth": []
                    }
                ],
                "paths": {}
            }
    except Exception as e:
        logger.error(f"Error generating OpenAPI spec: {e}")
        # Fallback to manual spec
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "ICS-Gate API",
                "description": "API for managing ICS calendars and receiving event notifications",
                "version": "1.0.0"
            },
            "servers": [
                {
                    "url": "http://localhost:5800",
                    "description": "Local development server"
                }
            ],
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key for authentication"
                    }
                },
                "schemas": {
                    "Error": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "integer"},
                                    "message": {"type": "string"}
                                },
                                "required": ["code", "message"]
                            }
                        }
                    },
                    "Calendar": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "user_id": {"type": "integer"},
                            "url": {"type": "string"},
                            "timezone": {"type": "string"},
                            "last_sync_at": {"type": "string", "nullable": True},
                            "sync_hash": {"type": "string", "nullable": True}
                        }
                    },
                    "Event": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "uid": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "location": {"type": "string"},
                            "start_datetime": {"type": "string"},
                            "end_datetime": {"type": "string"},
                            "all_day": {"type": "boolean"},
                            "user_id": {"type": "string"},
                            "calendar_timezone": {"type": "string"}
                        }
                    }
                }
            },
            "security": [
                {
                    "ApiKeyAuth": []
                }
            ],
            "paths": {}
        }
    
    return jsonify(openapi_spec)

def register_openapi_endpoint(app):
    """Register OpenAPI specification endpoint"""
    # Register the blueprint with the app
    app.register_blueprint(openapi_blp)
    
    # Return the view function
    return get_openapi_spec