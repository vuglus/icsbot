import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from entity.base import BaseCalendarEntity, Calendar

logger = logging.getLogger(__name__)


class CalendarEntity(BaseCalendarEntity):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_calendar(
        self,
        chat_id: str,
        chat_type: str,
        url: str,
        client_type: str = "ics",
        name: str = None,
    ) -> Calendar:
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO calendars (user_id, chat_id, chat_type, url, client_type, name) VALUES (?, ?, ?, ?, ?, ?)",
                (chat_id, chat_id, chat_type, url, client_type, name),
            )
            self.db_connection.commit()
            calendar_id = cursor.lastrowid
            logger.info(
                f"Created calendar {calendar_id} for chat {chat_id} ({chat_type})"
            )
            return Calendar(
                calendar_id,
                chat_id,
                url,
                None,
                None,
                "GMT+3",
                chat_id,
                chat_type,
                client_type,
                name,
            )
        except sqlite3.IntegrityError as e:
            self.db_connection.rollback()
            logger.warning(
                f"Calendar for chat {chat_id} with URL {url} already exists: {e}"
            )
            cursor.execute(
                "SELECT * FROM calendars WHERE user_id = ? AND url = ?", (chat_id, url)
            )
            row = cursor.fetchone()
            if row:
                return Calendar(
                    row["id"],
                    row["user_id"],
                    row["url"],
                    row["last_sync_at"],
                    row["sync_hash"],
                    row["timezone"] if "timezone" in row.keys() else "GMT+3",
                    row["chat_id"] if "chat_id" in row.keys() else None,
                    row["chat_type"] if "chat_type" in row.keys() else None,
                    row["client_type"] if "client_type" in row.keys() else "ics",
                    row["name"] if "name" in row.keys() else None,
                )
            raise Exception("Failed to retrieve existing calendar")

    def get_calendars(self, chat_id: str = None) -> List[Calendar]:
        cursor = self.db_connection.cursor()
        if chat_id:
            cursor.execute("SELECT * FROM calendars WHERE user_id = ?", (chat_id,))
        else:
            cursor.execute("SELECT * FROM calendars")
        rows = cursor.fetchall()
        return [
            Calendar(
                row["id"],
                row["user_id"],
                row["url"],
                row["last_sync_at"],
                row["sync_hash"],
                row["timezone"] if "timezone" in row.keys() else "GMT+3",
                row["chat_id"] if "chat_id" in row.keys() else None,
                row["chat_type"] if "chat_type" in row.keys() else None,
                row["client_type"] if "client_type" in row.keys() else "ics",
                row["name"] if "name" in row.keys() else None,
            )
            for row in rows
        ]

    def get_calendars_with_chat(self) -> List[Calendar]:
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM calendars WHERE chat_id IS NOT NULL")
        rows = cursor.fetchall()
        return [
            Calendar(
                row["id"],
                row["user_id"],
                row["url"],
                row["last_sync_at"],
                row["sync_hash"],
                row["timezone"] if "timezone" in row.keys() else "GMT+3",
                row["chat_id"] if "chat_id" in row.keys() else None,
                row["chat_type"] if "chat_type" in row.keys() else None,
                row["client_type"] if "client_type" in row.keys() else "ics",
                row["name"] if "name" in row.keys() else None,
            )
            for row in rows
        ]

    def delete_calendar(self, calendar_id: str, chat_id: str = None) -> bool:
        cursor = self.db_connection.cursor()
        if chat_id:
            cursor.execute(
                "DELETE FROM calendars WHERE id = ? AND user_id = ?",
                (calendar_id, chat_id),
            )
        else:
            cursor.execute("DELETE FROM calendars WHERE id = ?", (calendar_id,))
        deleted = cursor.rowcount > 0
        self.db_connection.commit()
        return deleted

    def get_calendar_by_id(self, calendar_id: str) -> Optional[Calendar]:
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM calendars WHERE id = ?", (calendar_id,))
        row = cursor.fetchone()
        if row:
            return Calendar(
                row["id"],
                row["user_id"],
                row["url"],
                row["last_sync_at"],
                row["sync_hash"],
                row["timezone"] if "timezone" in row.keys() else "GMT+3",
                row["chat_id"] if "chat_id" in row.keys() else None,
                row["chat_type"] if "chat_type" in row.keys() else None,
                row["client_type"] if "client_type" in row.keys() else "ics",
                row["name"] if "name" in row.keys() else None,
            )
        return None

    def update_calendar_sync(self, calendar_id: str, sync_hash: str):
        cursor = self.db_connection.cursor()
        cursor.execute(
            "UPDATE calendars SET last_sync_at = ?, sync_hash = ? WHERE id = ?",
            (datetime.now().isoformat(), sync_hash, calendar_id),
        )
        self.db_connection.commit()
        logger.info(f"Updated sync metadata for calendar {calendar_id}")

    def update_calendar(self, calendar_id: str, **kwargs) -> Optional[Calendar]:
        cursor = self.db_connection.cursor()
        sets = []
        params = []
        for field in ("name", "url", "client_type", "timezone", "chat_id", "chat_type"):
            if field in kwargs and kwargs[field] is not None:
                sets.append(f"{field} = ?")
                params.append(kwargs[field])
        if not sets:
            return self.get_calendar_by_id(calendar_id)
        params.append(calendar_id)
        cursor.execute(f"UPDATE calendars SET {', '.join(sets)} WHERE id = ?", params)
        self.db_connection.commit()
        logger.info(f"Updated calendar {calendar_id}")
        return self.get_calendar_by_id(calendar_id)
