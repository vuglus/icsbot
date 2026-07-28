import logging
import ydb
import uuid
from datetime import datetime
from typing import List, Optional
from entity.base import BaseCalendarEntity, Calendar

logger = logging.getLogger(__name__)


class CalendarEntity(BaseCalendarEntity):
    def __init__(self, session_pool):
        self.session_pool = session_pool

    def create_calendar(
        self,
        chat_id: str,
        chat_type: str,
        url: str,
        client_type: str = "ics",
        name: str = None,
    ) -> Calendar:
        def callee(session):
            existing = self._get_by_chat_and_url(chat_id, url, session)
            if existing is not None:
                return existing
            cal_id = uuid.uuid4().hex
            query = """
            DECLARE $id AS Utf8;
            DECLARE $user_id AS Utf8;
            DECLARE $chat_id AS Utf8;
            DECLARE $chat_type AS Utf8;
            DECLARE $url AS Utf8;
            DECLARE $client_type AS Utf8;
            DECLARE $name AS Utf8;
            UPSERT INTO calendars (id, user_id, chat_id, chat_type, url, client_type, timezone, name)
            VALUES ($id, $user_id, $chat_id, $chat_type, $url, $client_type, 'GMT+3', $name);
            """
            prepared = session.prepare(query)
            session.transaction().execute(
                prepared,
                parameters={
                    "$id": cal_id,
                    "$user_id": chat_id,
                    "$chat_id": chat_id,
                    "$chat_type": chat_type,
                    "$url": url,
                    "$client_type": client_type,
                    "$name": name or "",
                },
                commit_tx=True,
            )
            return self._get_by_chat_and_url(chat_id, url, session)

        return self.session_pool.retry_operation_sync(callee)

    def _get_by_chat_and_url(
        self, chat_id: str, url: str, session
    ) -> Optional[Calendar]:
        query = """
        DECLARE $chat_id AS Utf8;
        DECLARE $url AS Utf8;
        SELECT id, user_id, url, last_sync_at, sync_hash, timezone, chat_id, chat_type, client_type, name
        FROM calendars WHERE user_id = $chat_id AND url = $url;
        """
        prepared = session.prepare(query)
        result = session.transaction().execute(
            prepared,
            parameters={"$chat_id": chat_id, "$url": url},
            commit_tx=True,
        )
        if result[0].rows:
            row = result[0].rows[0]
            return Calendar(
                row.id,
                row.user_id,
                row.url,
                str(row.last_sync_at) if row.last_sync_at else None,
                row.sync_hash,
                row.timezone,
                row.chat_id if hasattr(row, "chat_id") else None,
                row.chat_type if hasattr(row, "chat_type") else None,
                row.client_type if hasattr(row, "client_type") else "ics",
                row.name if hasattr(row, "name") else None,
            )
        return None

    def get_calendars(self, chat_id: str = None) -> List[Calendar]:
        def callee(session):
            if chat_id:
                query = """
                DECLARE $chat_id AS Utf8;
                SELECT id, user_id, url, last_sync_at, sync_hash, timezone, chat_id, chat_type, client_type, name
                FROM calendars WHERE user_id = $chat_id;
                """
                prepared = session.prepare(query)
                result = session.transaction().execute(
                    prepared,
                    parameters={"$chat_id": chat_id},
                    commit_tx=True,
                )
            else:
                query = "SELECT id, user_id, url, last_sync_at, sync_hash, timezone, chat_id, chat_type, client_type, name FROM calendars;"
                prepared = session.prepare(query)
                result = session.transaction().execute(prepared, commit_tx=True)
            calendars = []
            for row in result[0].rows:
                calendars.append(
                    Calendar(
                        row.id,
                        row.user_id,
                        row.url,
                        str(row.last_sync_at) if row.last_sync_at else None,
                        row.sync_hash,
                        row.timezone,
                        row.chat_id if hasattr(row, "chat_id") else None,
                        row.chat_type if hasattr(row, "chat_type") else None,
                        row.client_type if hasattr(row, "client_type") else "ics",
                        row.name if hasattr(row, "name") else None,
                    )
                )
            return calendars

        return self.session_pool.retry_operation_sync(callee)

    def get_calendars_with_chat(self) -> List[Calendar]:
        def callee(session):
            query = """
            SELECT id, user_id, url, last_sync_at, sync_hash, timezone, chat_id, chat_type, client_type, name
            FROM calendars WHERE chat_id IS NOT NULL;
            """
            prepared = session.prepare(query)
            result = session.transaction().execute(prepared, commit_tx=True)
            calendars = []
            for row in result[0].rows:
                calendars.append(
                    Calendar(
                        row.id,
                        row.user_id,
                        row.url,
                        str(row.last_sync_at) if row.last_sync_at else None,
                        row.sync_hash,
                        row.timezone,
                        row.chat_id if hasattr(row, "chat_id") else None,
                        row.chat_type if hasattr(row, "chat_type") else None,
                        row.client_type if hasattr(row, "client_type") else "ics",
                        row.name if hasattr(row, "name") else None,
                    )
                )
            return calendars

        return self.session_pool.retry_operation_sync(callee)

    def delete_calendar(self, calendar_id: str, chat_id: str = None) -> bool:
        def callee(session):
            if chat_id:
                query = """
                DECLARE $id AS Utf8;
                DECLARE $chat_id AS Utf8;
                DELETE FROM calendars WHERE id = $id AND user_id = $chat_id;
                """
                prepared = session.prepare(query)
                session.transaction().execute(
                    prepared,
                    parameters={"$id": calendar_id, "$chat_id": chat_id},
                    commit_tx=True,
                )
            else:
                query = "DECLARE $id AS Utf8; DELETE FROM calendars WHERE id = $id;"
                prepared = session.prepare(query)
                session.transaction().execute(
                    prepared, parameters={"$id": calendar_id}, commit_tx=True
                )
            check = "DECLARE $id AS Utf8; SELECT id FROM calendars WHERE id = $id;"
            check_prep = session.prepare(check)
            check_result = session.transaction().execute(
                check_prep, parameters={"$id": calendar_id}, commit_tx=True
            )
            return len(check_result[0].rows) == 0

        return self.session_pool.retry_operation_sync(callee)

    def get_calendar_by_id(self, calendar_id: str) -> Optional[Calendar]:
        def callee(session):
            query = """
            DECLARE $id AS Utf8;
            SELECT id, user_id, url, last_sync_at, sync_hash, timezone, chat_id, chat_type, client_type, name
            FROM calendars WHERE id = $id;
            """
            prepared = session.prepare(query)
            result = session.transaction().execute(
                prepared, parameters={"$id": calendar_id}, commit_tx=True
            )
            if result[0].rows:
                row = result[0].rows[0]
                return Calendar(
                    row.id,
                    row.user_id,
                    row.url,
                    str(row.last_sync_at) if row.last_sync_at else None,
                    row.sync_hash,
                    row.timezone,
                    row.chat_id if hasattr(row, "chat_id") else None,
                    row.chat_type if hasattr(row, "chat_type") else None,
                    row.client_type if hasattr(row, "client_type") else "ics",
                    row.name if hasattr(row, "name") else None,
                )
            return None

        return self.session_pool.retry_operation_sync(callee)

    def update_calendar_sync(self, calendar_id: str, sync_hash: str):
        def callee(session):
            query = """
            DECLARE $id AS Utf8;
            DECLARE $sync_hash AS Utf8;
            UPDATE calendars SET last_sync_at = CurrentUtcTimestamp(), sync_hash = $sync_hash WHERE id = $id;
            """
            prepared = session.prepare(query)
            session.transaction().execute(
                prepared,
                parameters={"$id": calendar_id, "$sync_hash": sync_hash},
                commit_tx=True,
            )
            logger.info(f"Updated sync metadata for calendar {calendar_id}")

        return self.session_pool.retry_operation_sync(callee)

    def update_calendar(self, calendar_id: str, **kwargs) -> Optional[Calendar]:
        def callee(session):
            sets = []
            declares = ["DECLARE $id AS Utf8;"]
            params = {"$id": calendar_id}
            for field, value in kwargs.items():
                if value is not None and field in (
                    "name",
                    "url",
                    "client_type",
                    "timezone",
                    "chat_id",
                    "chat_type",
                ):
                    param = f"${field}"
                    sets.append(f"{field} = {param}")
                    params[param] = value
                    declares.append(f"DECLARE ${field} AS Utf8;")
            if not sets:
                return self.get_calendar_by_id(calendar_id)
            query = f"{' '.join(declares)} UPDATE calendars SET {', '.join(sets)} WHERE id = $id;"
            prepared = session.prepare(query)
            session.transaction().execute(prepared, parameters=params, commit_tx=True)
            return self.get_calendar_by_id(calendar_id)

        return self.session_pool.retry_operation_sync(callee)
