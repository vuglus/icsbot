import logging
from flask import request, jsonify
from marshmallow import Schema, fields
from services.config_service import get_api_key
from services.database import create_user, create_calendar, get_calendars, delete_calendar, get_calendar_by_id
from services.api_utils import validate_api_key
from services.api_docs import Blueprint

# Configure logging
logger = logging.getLogger(__name__)

# Create a blueprint for this endpoint
calendar_blp = Blueprint('calendars', __name__, url_prefix='/calendars')

# Define schema for query parameters
class ListCalendarsSchema(Schema):
    user_id = fields.Str(required=False, metadata={"description": "Filter calendars by user ID"})

class CreateCalendarSchema(Schema):
    user_id = fields.Str(required=True, metadata={"description": "User ID"})
    url = fields.Str(required=True, metadata={"description": "Calendar URL"})

@calendar_blp.route('', methods=['POST'])
@calendar_blp.arguments(CreateCalendarSchema)
@calendar_blp.doc(
    summary="Create calendar",
    description="Creates a new calendar for a user",
    security=[{"ApiKeyAuth": []}]
)
@calendar_blp.response(201, description="Calendar created successfully")
def create_calendar_api(args):
    """Create a new calendar for a user"""
    if not validate_api_key():
        return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
    
    try:
        # Get data from arguments
        user_id = args['user_id']
        url = args['url']
        
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

@calendar_blp.route('', methods=['GET'])
@calendar_blp.arguments(ListCalendarsSchema, location="query")
@calendar_blp.doc(
    summary="List calendars",
    description="Returns a list of calendars, optionally filtered by user ID",
    security=[{"ApiKeyAuth": []}]
)
def list_calendars_api(args):
    """List calendars, optionally filtered by user_id"""
    if not validate_api_key():
        return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
    
    try:
        user_id = args.get('user_id') if args else None
        calendars = get_calendars(user_id)
        
        calendars_data = []
        for calendar in calendars:
            calendar_data = {
                'id': calendar.id,
                'user_id': calendar.user_id,
                'url': calendar.url,
                'timezone': calendar.timezone,
                'last_sync_at': calendar.last_sync_at,
                'sync_hash': calendar.sync_hash
            }
            calendars_data.append(calendar_data)
        
        return jsonify({'calendars': calendars_data})
    except ValueError as e:
        # Handle user not found error
        logger.warning(f"User not found: {e}")
        return jsonify({'error': {'code': 404, 'message': 'User not found'}}), 404
    except Exception as e:
        logger.error(f"Error getting calendars: {e}")
        return jsonify({'error': {'code': 500, 'message': 'Internal Server Error'}}), 500

@calendar_blp.route('/<int:calendar_id>', methods=['DELETE'])
@calendar_blp.doc(
    summary="Delete calendar",
    description="Deletes a calendar by ID, optionally checking user ownership",
    security=[{"ApiKeyAuth": []}]
)
def delete_calendar_api(calendar_id):
    """Delete a calendar by ID"""
    if not validate_api_key():
        return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
    
    try:
        # Get user_id from query parameters (optional, for ownership check)
        user_id = request.args.get('user_id')
        
        # Delete calendar
        deleted = delete_calendar(calendar_id, user_id)
        
        if deleted:
            return jsonify({
                'status': 'success',
                'message': 'Calendar deleted successfully'
            })
        else:
            # Check if calendar exists
            calendar = get_calendar_by_id(calendar_id)
            if calendar:
                return jsonify({'error': {'code': 403, 'message': 'Forbidden: You do not have permission to delete this calendar'}}), 403
            else:
                return jsonify({'error': {'code': 404, 'message': 'Calendar not found'}}), 404
                
    except ValueError as e:
        # Handle user not found error
        logger.warning(f"User not found: {e}")
        return jsonify({'error': {'code': 404, 'message': 'User not found'}}), 404
    except Exception as e:
        logger.error(f"Error deleting calendar: {e}")
        return jsonify({'error': {'code': 500, 'message': 'Internal Server Error'}}), 500

def register_calendar_endpoint(app):
    """Register calendar endpoints"""
    # Register the blueprint with the app
    app.register_blueprint(calendar_blp)
    
    # Return the view functions
    return [create_calendar_api, list_calendars_api, delete_calendar_api]