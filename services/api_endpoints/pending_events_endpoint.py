import logging
from flask import request, jsonify
from dateutil import tz
from services.config_service import get_api_key
from services.notification_service import get_pending_events_for_api

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

def validate_api_key() -> bool:
    """Validate API key from request"""
    # Check header first
    api_key = request.headers.get('X-API-Key')
    
    # Check query parameter if header not found
    if not api_key:
        api_key = request.args.get('api_key')
    
    # Validate against environment variable or config
    expected_key = get_api_key()
    
    return api_key == expected_key

def register_pending_events_endpoint(app):
    """Register pending events endpoint"""
    
    @app.route('/events/pending')
    def get_events_pending():
        """Get pending events"""
        if not validate_api_key():
            return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
        
        try:
            # Get user_id from query parameters (optional)
            user_id = request.args.get('user_id')
            
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