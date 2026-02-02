import logging
from flask import request, jsonify
from flask_apispec import doc, use_kwargs
from marshmallow import Schema, fields
from services.config_service import get_api_key
from services.database import create_user, create_calendar, get_calendars, delete_calendar, get_calendar_by_id
from services.api_utils import validate_api_key

# Configure logging
logger = logging.getLogger(__name__)

def register_calendar_endpoint(app):
    """Register calendar endpoints"""
    
    # Define schema for query parameters
    class ListCalendarsSchema(Schema):
        user_id = fields.Str(required=False, description="Filter calendars by user ID")
    
    @app.route('/calendars', methods=['POST'])
    @doc(
        summary="Create calendar",
        description="Creates a new calendar for a user",
        security=[{"ApiKeyAuth": []}],
        requestBody={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["user_id", "url"],
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User ID"
                            },
                            "url": {
                                "type": "string",
                                "description": "Calendar URL"
                            }
                        }
                    }
                }
            }
        },
        responses={
            201: {
                "description": "Calendar created successfully"
            },
            400: {"description": "Bad request"},
            401: {"description": "Unauthorized"}
        }
    )
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
        
    @app.route('/calendars', methods=['GET'])
    @use_kwargs(ListCalendarsSchema, location="query")
    @doc(
        summary="List calendars",
        description="Returns a list of calendars, optionally filtered by user ID",
        security=[{"ApiKeyAuth": []}],
        responses={
            200: {
                "description": "List of calendars",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "User ID"
                                },
                                "url": {
                                    "type": "string",
                                    "description": "Calendar URL"
                                }
                            }
                        }
                    }
                },
            },
            401: {"description": "Unauthorized"}
        }
    )

    def list_calendars_api(user_id=None):
        """List calendars, optionally filtered by user_id"""
        if not validate_api_key():
            return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
        
        try:
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

    @app.route('/calendars/<int:calendar_id>', methods=['DELETE'])
    @doc(
        summary="Delete calendar",
        description="Deletes a calendar by ID, optionally checking user ownership",
        security=[{"ApiKeyAuth": []}],
        parameters=[
            {
                "in": "path",
                "name": "calendar_id",
                "required": True,
                "schema": {"type": "integer"},
                "description": "Calendar ID"
            },
            {
                "in": "query",
                "name": "user_id",
                "required": False,
                "schema": {"type": "string"},
                "description": "User ID for ownership check"
            }
        ],
        responses={
            200: {"description": "Calendar deleted successfully"},
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
            404: {"description": "Calendar not found"}
        }
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
    
    # Return the view functions so they can be registered with flask-apispec
    return [create_calendar_api, list_calendars_api, delete_calendar_api]