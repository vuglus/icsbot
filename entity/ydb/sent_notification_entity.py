import logging
import ydb
import uuid
from datetime import datetime
from typing import List, Optional
from entity.base import BaseSentNotificationEntity, SentNotification

logger = logging.getLogger(__name__)


class SentNotificationEntity(BaseSentNotificationEntity):
    def __init__(self, session_pool):
        self.session_pool = session_pool

    def is_event_sent(self, calendar_id: str, event_uid: str) -> bool:
        def callee(session):
            query = """
            DECLARE $calendar_id AS Utf8;
            DECLARE $event_uid AS Utf8;
            SELECT 1 FROM sent_notifications WHERE calendar_id = $calendar_id AND event_uid = $event_uid LIMIT 1;
            """
            prepared = session.prepare(query)
            result = session.transaction().execute(
                prepared,
                parameters={"$calendar_id": calendar_id, "$event_uid": event_uid},
                commit_tx=True,
            )
            return len(result[0].rows) > 0

        return self.session_pool.retry_operation_sync(callee)

    def record_sent(
        self, calendar_id: str, event_uid: str, chat_id: str, event_data: str
    ):
        def callee(session):
            notif_id = uuid.uuid4().hex
            query = """
            DECLARE $id AS Utf8;
            DECLARE $calendar_id AS Utf8;
            DECLARE $event_uid AS Utf8;
            DECLARE $chat_id AS Utf8;
            DECLARE $event_data AS Utf8;
            UPSERT INTO sent_notifications (id, calendar_id, event_uid, chat_id, event_data, sent_at)
            VALUES ($id, $calendar_id, $event_uid, $chat_id, $event_data, CurrentUtcTimestamp());
            """
            prepared = session.prepare(query)
            session.transaction().execute(
                prepared,
                parameters={
                    "$id": notif_id,
                    "$calendar_id": calendar_id,
                    "$event_uid": event_uid,
                    "$chat_id": chat_id,
                    "$event_data": event_data,
                },
                commit_tx=True,
            )
            logger.info(
                f"Recorded sent notification for event {event_uid} in calendar {calendar_id}"
            )

        return self.session_pool.retry_operation_sync(callee)

    def get_sent_notifications(
        self, calendar_id: str = None, chat_id: str = None
    ) -> List[SentNotification]:
        def callee(session):
            if calendar_id and chat_id:
                query = """
                DECLARE $calendar_id AS Utf8;
                DECLARE $chat_id AS Utf8;
                SELECT id, calendar_id, event_uid, chat_id, sent_at, event_data
                FROM sent_notifications WHERE calendar_id = $calendar_id AND chat_id = $chat_id
                ORDER BY sent_at DESC;
                """
                prepared = session.prepare(query)
                result = session.transaction().execute(
                    prepared,
                    parameters={"$calendar_id": calendar_id, "$chat_id": chat_id},
                    commit_tx=True,
                )
            elif calendar_id:
                query = """
                DECLARE $calendar_id AS Utf8;
                SELECT id, calendar_id, event_uid, chat_id, sent_at, event_data
                FROM sent_notifications WHERE calendar_id = $calendar_id ORDER BY sent_at DESC;
                """
                prepared = session.prepare(query)
                result = session.transaction().execute(
                    prepared,
                    parameters={"$calendar_id": calendar_id},
                    commit_tx=True,
                )
            elif chat_id:
                query = """
                DECLARE $chat_id AS Utf8;
                SELECT id, calendar_id, event_uid, chat_id, sent_at, event_data
                FROM sent_notifications WHERE chat_id = $chat_id ORDER BY sent_at DESC;
                """
                prepared = session.prepare(query)
                result = session.transaction().execute(
                    prepared,
                    parameters={"$chat_id": chat_id},
                    commit_tx=True,
                )
            else:
                query = "SELECT id, calendar_id, event_uid, chat_id, sent_at, event_data FROM sent_notifications ORDER BY sent_at DESC;"
                prepared = session.prepare(query)
                result = session.transaction().execute(prepared, commit_tx=True)
            notifications = []
            for row in result[0].rows:
                notifications.append(
                    SentNotification(
                        row.id,
                        row.calendar_id,
                        row.event_uid,
                        row.chat_id,
                        str(row.sent_at) if hasattr(row, "sent_at") else None,
                        row.event_data if hasattr(row, "event_data") else None,
                    )
                )
            return notifications

        return self.session_pool.retry_operation_sync(callee)
