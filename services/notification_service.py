import logging
from datetime import datetime
from .database import EventEntity

# Configure logging
logger = logging.getLogger(__name__)

def check_pending_notifications():
    """Check for pending notifications"""
    logger.info("Checking for pending notifications")
    
    pending_events = EventEntity.get_pending_events()
    logger.info(f"Found {len(pending_events)} pending events")
    
    # In a real implementation, this would trigger external notifications
    # For now, we just log them
    for event in pending_events:
        logger.info(f"Pending notification: {event.title} at {event.start_datetime}")

def get_pending_events_for_api(user_id=None):
    """Get pending events for API response"""
    return EventEntity.get_pending_events(user_id)

def mark_notification_delivered(event_id: int) -> bool:
    """Mark notification as delivered"""
    return EventEntity.mark_event_notified(event_id)