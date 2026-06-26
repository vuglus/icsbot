import logging
from flask import request, jsonify
from services.api_docs import Blueprint

# Configure logging
logger = logging.getLogger(__name__)

def create_notification_blueprint(auth_service, notification_service):
    notification_blp = Blueprint(
        'notifications',
        __name__,
        url_prefix='/notifications'
    )

    @notification_blp.route('/<string:event_id>/delivered', methods=['POST'])
    @notification_blp.doc(
        summary="Mark notification as delivered",
        description="Marks a notification as delivered",
        security=[{"ApiKeyAuth": []}]
    )
    def mark_notification_delivered_api(event_id):
        """Mark notification as delivered"""
        if not auth_service.validate_api_key():
            return jsonify({'error': {'code': 401, 'message': 'Unauthorized'}}), 401
        
        try:
            success = notification_service.mark_notification_delivered(event_id)
            
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

    return notification_blp