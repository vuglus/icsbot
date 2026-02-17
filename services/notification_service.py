import logging
from datetime import datetime
from services.database import Database

# Configure logging
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, database: Database):
        self.db = database
        self.events = self.db.getEvent()
        self.users = self.db.getUser()
        
    
    def check_pending_notifications(self):
        """Check for pending notifications"""
        logger.info("Checking for pending notifications")
        users = self.users.get_users_with_calendars()

        for user in users:
            pending_events = self.events.get_pending_events(user.user_id)
            logger.info(f"Found {len(pending_events)} pending events")
            # In a real implementation, this would trigger external notifications
            # For now, we just log them
            for event in pending_events:
                logger.info(f"Pending notification: {event.title} at {event.start_datetime}")
    
    def get_pending_events_for_api(self, user_id=None):
        """Get pending events for API response"""
        # Get database entities
        return self.events.get_pending_events(user_id)
    
    def mark_notification_delivered(self, event_id: int) -> bool:
        """Mark notification as delivered"""
        # Get database entities
        return self.events.mark_event_notified(event_id)