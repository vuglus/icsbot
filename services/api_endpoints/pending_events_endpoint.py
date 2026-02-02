import logging
from flask import request, jsonify
from marshmallow import Schema, fields
from dateutil import tz
from services.config_service import get_api_key
from services.notification_service import get_pending_events_for_api
from services.api_utils import validate_api_key
from services.api_docs import Blueprint

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

# Create a blueprint for this endpoint
pending_events_blp = Blueprint('events', __name__, url_prefix='/events')

# Define schema for query parameters
class PendingEventsSchema(Schema):
    user_id = fields.Str(required=False, metadata={"description": "Filter events by user ID"})

@pending_events_blp.route('/pending', methods=['GET'])
@pending_events_blp.arguments(PendingEventsSchema, location="query")
@pending_events_blp.doc(
    summary="Get pending events",
    description="Returns a list of events that are ready for notification",
    security=[{"ApiKeyAuth": []}]
)
def get_events_pending(args):
    """Get pending events"""
    if not validate_api_key():
        return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
    
    try:
        user_id = args.get('user_id') if args else None
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

def register_pending_events_endpoint(app):
    """Register pending events endpoint"""
    # Register the blueprint with the app
    app.register_blueprint(pending_events_blp)
    
    # Return the view function
    return get_events_pending