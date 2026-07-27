import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from entity.base import BaseSentNotificationEntity, SentNotification

logger = logging.getLogger(__name__)


class SentNotificationEntity(BaseSentNotificationEntity):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def is_event_sent(self, calendar_id: str, event_uid: str) -> bool:
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT 1 FROM sent_notifications WHERE calendar_id = ? AND event_uid = ?",
            (calendar_id, event_uid),
        )
        return cursor.fetchone() is not None

    def record_sent(
        self, calendar_id: str, event_uid: str, chat_id: str, event_data: str
    ):
        cursor = self.db_connection.cursor()
        cursor.execute(
            "INSERT INTO sent_notifications (calendar_id, event_uid, chat_id, event_data) VALUES (?, ?, ?, ?)",
            (calendar_id, event_uid, chat_id, event_data),
        )
        self.db_connection.commit()
        logger.info(
            f"Recorded sent notification for event {event_uid} in calendar {calendar_id}"
        )

    def get_sent_notifications(
        self, calendar_id: str = None, chat_id: str = None
    ) -> List[SentNotification]:
        cursor = self.db_connection.cursor()
        if calendar_id and chat_id:
            cursor.execute(
                "SELECT * FROM sent_notifications WHERE calendar_id = ? AND chat_id = ? ORDER BY sent_at DESC",
                (calendar_id, chat_id),
            )
        elif calendar_id:
            cursor.execute(
                "SELECT * FROM sent_notifications WHERE calendar_id = ? ORDER BY sent_at DESC",
                (calendar_id,),
            )
        elif chat_id:
            cursor.execute(
                "SELECT * FROM sent_notifications WHERE chat_id = ? ORDER BY sent_at DESC",
                (chat_id,),
            )
        else:
            cursor.execute("SELECT * FROM sent_notifications ORDER BY sent_at DESC")
        rows = cursor.fetchall()
        return [
            SentNotification(
                row["id"],
                row["calendar_id"],
                row["event_uid"],
                row["chat_id"],
                row["sent_at"],
                row["event_data"],
            )
            for row in rows
        ]
