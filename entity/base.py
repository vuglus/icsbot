import abc
from typing import List, Optional
from datetime import datetime


class Calendar:
    def __init__(
        self,
        id: str,
        user_id: str,
        url: str,
        last_sync_at: str,
        sync_hash: str,
        timezone: str = "GMT+3",
        chat_id: str = None,
        chat_type: str = None,
        client_type: str = "ics",
        name: str = None,
    ):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.last_sync_at = last_sync_at
        self.sync_hash = sync_hash
        self.timezone = timezone
        self.chat_id = chat_id
        self.chat_type = chat_type
        self.client_type = client_type
        self.name = name


class SentNotification:
    def __init__(
        self,
        id: str,
        calendar_id: str,
        event_uid: str,
        chat_id: str,
        sent_at: str,
        event_data: str = None,
    ):
        self.id = id
        self.calendar_id = calendar_id
        self.event_uid = event_uid
        self.chat_id = chat_id
        self.sent_at = sent_at
        self.event_data = event_data


class Migration:
    def __init__(self, id: str, name: str, executed_at: str):
        self.id = id
        self.name = name
        self.executed_at = executed_at


class BaseMigrationEntity(abc.ABC):
    @abc.abstractmethod
    def create_migration_table(self):
        pass

    @abc.abstractmethod
    def get_executed_migrations(self) -> list:
        pass

    @abc.abstractmethod
    def record_migration(self, name: str):
        pass

    @abc.abstractmethod
    def is_migration_executed(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def migration_table_exists(self) -> bool:
        pass

    @abc.abstractmethod
    def execute(self, queries: List):
        pass


class BaseCalendarEntity(abc.ABC):
    @abc.abstractmethod
    def create_calendar(
        self,
        chat_id: str,
        chat_type: str,
        url: str,
        client_type: str = "ics",
        name: str = None,
    ) -> Calendar:
        pass

    @abc.abstractmethod
    def get_calendars(self, chat_id: str = None) -> List[Calendar]:
        pass

    @abc.abstractmethod
    def get_calendars_with_chat(self) -> List[Calendar]:
        pass

    @abc.abstractmethod
    def delete_calendar(self, calendar_id: str, chat_id: str = None) -> bool:
        pass

    @abc.abstractmethod
    def get_calendar_by_id(self, calendar_id: str) -> Calendar:
        pass

    @abc.abstractmethod
    def update_calendar_sync(self, calendar_id: str, sync_hash: str):
        pass

    @abc.abstractmethod
    def update_calendar(self, calendar_id: str, **kwargs) -> Optional[Calendar]:
        pass


class BaseSentNotificationEntity(abc.ABC):
    @abc.abstractmethod
    def is_event_sent(self, calendar_id: str, event_uid: str) -> bool:
        pass

    @abc.abstractmethod
    def record_sent(
        self, calendar_id: str, event_uid: str, chat_id: str, event_data: str
    ):
        pass

    @abc.abstractmethod
    def get_sent_notifications(
        self, calendar_id: str = None, chat_id: str = None
    ) -> List[SentNotification]:
        pass
