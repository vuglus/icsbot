import logging
from flask import request, jsonify
from services.config_service import get_api_key
from services.database import create_user, create_calendar

# Configure logging
logger = logging.getLogger(__name__)

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

def register_calendar_endpoint(app):
    """Register calendar creation endpoint"""
    
    @app.route('/calendars', methods=['POST'])
    def create_calendar_api():
        """Create a new calendar for a user"""
        if not validate_api_key():
            return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
        
        try:
            # Get JSON data from request
            data = request.get_json()
            
            # Validate required fields
            if not data or 'user_id' not in data or 'url' not in data:
                return jsonify({'error': {'code': 400, 'message': 'Missing required fields: user_id and url'}}), 400
            
            user_id = data['user_id']
            url = data['url']
            
            # Validate URL format (basic validation)
            if not url.startswith(('http://', 'https://')):
                return jsonify({'error': {'code': 400, 'message': 'Invalid URL format'}}), 400
            
            # Create user if not exists
            user = create_user(user_id)
            
            # Create calendar
            calendar = create_calendar(user.id, url)
            
            # Return success response
            return jsonify({
                'status': 'success',
                'message': 'Calendar created successfully',
                'calendar': {
                    'id': calendar.id,
                    'user_id': calendar.user_id,
                    'url': calendar.url,
                    'timezone': calendar.timezone
                }
            }), 201
            
        except Exception as e:
            logger.error(f"Error creating calendar: {e}")
            return jsonify({'error': {'code': 500, 'message': 'Internal Server Error'}}), 500