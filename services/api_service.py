import logging
from flask import Flask, request, jsonify
from datetime import datetime
from .config_service import get_api_key
from .notification_service import get_pending_events_for_api, mark_notification_delivered

# Configure logging
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)

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

# API routes
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

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
            event_data = {
                'id': event.id,
                'uid': event.uid,
                'title': event.title,
                'description': event.description,
                'location': event.location,
                'start_datetime': event.start_datetime,
                'end_datetime': event.end_datetime,
                'all_day': event.all_day
            }
            
            # Include user_id if available
            if hasattr(event, 'user_id'):
                event_data['user_id'] = event.user_id
                
            events_data.append(event_data)
        
        return jsonify({'events': events_data})
    except ValueError as e:
        # Handle user not found error
        logger.warning(f"User not found: {e}")
        return jsonify({'error': {'code': 404, 'message': 'User not found'}}), 404
    except Exception as e:
        logger.error(f"Error getting pending events: {e}")
        return jsonify({'error': {'code': 500, 'message': 'Internal Server Error'}}), 500

@app.route('/notifications/<int:event_id>/delivered', methods=['POST'])
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

def get_app():
    """Get the Flask app instance"""
    return app