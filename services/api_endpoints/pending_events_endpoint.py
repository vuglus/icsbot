import logging
from flask import request, jsonify
from flask_apispec import doc, use_kwargs
from marshmallow import Schema, fields
from dateutil import tz
from services.config_service import get_api_key
from services.notification_service import get_pending_events_for_api
from services.api_utils import validate_api_key

# Configure logging
logger = logging.getLogger(__name__)

# Timezone cache to avoid recreating timezone objects
_timezone_cache = {}

def convert_datetime_to_timezone(dt_string, timezone_name):
    """Convert datetime string to specified timezone"""
    from dateutil import parser
    
    if not dt_string:
        return None
    
    try:
        # Parse the datetime string
        dt = parser.isoparse(dt_string)
        
        # Get or create timezone object
        if timezone_name not in _timezone_cache:
            _timezone_cache[timezone_name] = tz.gettz(timezone_name)
        
        # Convert to target timezone
        target_tz = _timezone_cache[timezone_name]
        dt = dt.astimezone(target_tz)
        return dt.isoformat()
    except Exception as e:
        logger.warning(f"Error converting datetime {dt_string} to timezone {timezone_name}: {e}")
        return dt_string  # Return original if conversion fails

def register_pending_events_endpoint(app):
    """Register pending events endpoint"""
    
    # Define schema for query parameters
    class PendingEventsSchema(Schema):
        user_id = fields.Str(required=False, description="Filter events by user ID")
    
    @app.route('/events/pending')
    @use_kwargs(PendingEventsSchema, location="query")
    @doc(
        summary="Get pending events",
        description="Returns a list of events that are ready for notification",
        security=[{"ApiKeyAuth": []}],
        parameters=[
            {
                "in": "query",
                "name": "user_id",
                "required": False,
                "schema": {"type": "string"},
                "description": "Filter events by user ID"
            }
        ],
        responses={
            200: {
                "description": "List of pending events",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "events": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "uid": {"type": "string"},
                                            "user_id": {"type": "integer"},
                                            "title": {"type": "string"},
                                            "description": {"type": "string"},
                                            "location": {"type": "string"},
                                            "start_datetime": {"type": "string", "format": "date-time"},
                                            "end_datetime": {"type": "string", "format": "date-time"},
                                            "all_day": {"type": "boolean"},
                                            "calendar_timezone": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
            },
            401: {"description": "Unauthorized"}
        }
    )
    def get_events_pending(user_id=None):
        """Get pending events"""
        if not validate_api_key():
            return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
        
        try:
            pending_events = get_pending_events_for_api(user_id)
            
            events_data = []
            for event in pending_events:
                calendar_timezone = getattr(event, 'calendar_timezone', 'GMT+3')
                event_data = {
                    'id': event.id,
                    'uid': event.uid,
                    'user_id': event.user_id,
                    'title': event.title,
                    'description': event.description,
                    'location': event.location,
                    'start_datetime': convert_datetime_to_timezone(event.start_datetime, calendar_timezone),
                    'end_datetime': convert_datetime_to_timezone(event.end_datetime, calendar_timezone),
                    'all_day': event.all_day,
                    'calendar_timezone': calendar_timezone,
                }
                
                events_data.append(event_data)
            
            return jsonify({'events': events_data})
        except ValueError as e:
            # Handle user not found error
            logger.warning(f"User not found: {e}")
            return jsonify({'error': {'code': 404, 'message': 'User not found'}}), 404
        except Exception as e:
            logger.error(f"Error getting pending events: {e}")
            return jsonify({'error': {'code': 500, 'message': 'Internal Server Error'}}), 500
    
    # Return the view function so it can be registered with flask-apispec
    return [get_events_pending]