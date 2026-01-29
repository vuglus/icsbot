#!/usr/bin/env python3
"""
Manual calendar synchronization script for ICS-Gate.
This script allows manual triggering of calendar synchronization for debugging purposes.
"""

import sys
import os
import logging
import argparse

# Add the services directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.database import init_db, get_calendars, get_calendar_by_id
from services.calendar_service import sync_calendar

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def sync_specific_calendar(calendar_id):
    """Sync a specific calendar by ID"""
    logger = logging.getLogger(__name__)
    
    # Initialize database
    init_db()
    
    # Get specific calendar
    calendar = get_calendar_by_id(calendar_id)
    if not calendar:
        logger.error(f"Calendar with ID {calendar_id} not found")
        return False
    
    # Sync the calendar
    logger.info(f"Manually syncing calendar {calendar_id}")
    success = sync_calendar(calendar)
    
    if success:
        logger.info(f"Calendar {calendar_id} synced successfully")
    else:
        logger.error(f"Failed to sync calendar {calendar_id}")
    
    return success

def sync_all_calendars_manual():
    """Sync all calendars manually"""
    logger = logging.getLogger(__name__)
    
    # Initialize database
    init_db()
    
    # Get all calendars
    calendars = get_calendars()
    if not calendars:
        logger.info("No calendars found to sync")
        return True
    
    logger.info(f"Found {len(calendars)} calendars to sync")
    
    success_count = 0
    for calendar in calendars:
        logger.info(f"Syncing calendar {calendar.id} from {calendar.url}")
        if sync_calendar(calendar):
            success_count += 1
            logger.info(f"Calendar {calendar.id} synced successfully")
        else:
            logger.error(f"Failed to sync calendar {calendar.id}")
    
    logger.info(f"Manual sync complete: {success_count}/{len(calendars)} successful")
    return success_count == len(calendars)

def main():
    """Main function"""
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(description='Manual calendar synchronization for ICS-Gate')
    parser.add_argument('--calendar-id', type=int, help='Sync specific calendar by ID')
    parser.add_argument('--all', action='store_true', help='Sync all calendars')
    
    args = parser.parse_args()
    
    # Check if at least one option is provided
    if not args.all and not args.calendar_id:
        parser.print_help()
        return 1
    
    # Execute sync based on arguments
    if args.calendar_id:
        success = sync_specific_calendar(args.calendar_id)
    elif args.all:
        success = sync_all_calendars_manual()
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())