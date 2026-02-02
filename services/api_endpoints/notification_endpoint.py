import logging
from flask import request, jsonify
from flask_apispec import doc
from services.config_service import get_api_key
from services.notification_service import mark_notification_delivered
from services.api_utils import validate_api_key

# Configure logging
logger = logging.getLogger(__name__)

def register_notification_endpoint(app):
    """Register notification delivered endpoint"""
    
    @app.route('/notifications/<int:event_id>/delivered', methods=['POST'])
    @doc(
        summary="Mark notification as delivered",
        description="Marks a notification as delivered",
        security=[{"ApiKeyAuth": []}],
        parameters=[
            {
                "in": "path",
                "name": "event_id",
                "required": True,
                "schema": {"type": "integer"},
                "description": "Event ID"
            }
        ],
        responses={
            200: {"description": "Notification marked as delivered"},
            401: {"description": "Unauthorized"},
            404: {"description": "Event not found"},
            500: {"description": "Internal Server Error"}
        }
    )
    def mark_notification_delivered_api(event_id):
        """Mark notification as delivered"""
        if not validate_api_key():
            return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
        
        try:
            success = mark_notification_delivered(event_id)
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Notification marked as delivered',
                    'event_id': event_id
                })
            else:
                return jsonify({'error': {'code': 404, 'message': 'Event not found'}}), 404
        except Exception as e:
            logger.error(f"Error marking notification as delivered: {e}")
            return jsonify({'error': {'code': 500, 'message': 'Internal Server Error'}}), 500
    
    # Return the view function so it can be registered with flask-apispec
    return [mark_notification_delivered_api]