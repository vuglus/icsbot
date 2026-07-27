import os
import logging

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config):
        self.config = config

    def _getAny(self, key: str, default=None) -> str:
        val = self.config.get(key)
        if val is not None:
            return val
        return os.environ.get(key, default)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def getApiKey(self):
        key = os.environ.get("API_KEY")
        return key if key else self.config.get("api_key")

    def getDBProvider(self):
        return self._getAny("DB_PROVIDER")

    def getDBPath(self):
        return self._getAny("DB_PATH")

    def getDBEndpoint(self):
        return self._getAny("DB_ENDPOINT")

    def get_notify_before_minutes(self) -> int:
        return int(self._getAny("NOTIFY_BEFORE_MINUTES", 15))

    def get_notify_interval_seconds(self) -> int:
        return int(self._getAny("NOTIFY_INTERVAL_SECONDS", 60))

    def getTZone(self) -> str:
        return self._getAny("TIMEZONE_DEFAULT", "UTC")

    def get_port(self) -> int:
        return int(self._getAny("EXT_PORT", 8080))

    def get_tg_bot_url(self) -> str:
        return self._getAny("TG_BOT_URL", "")

    def get_tg_bot_token(self) -> str:
        return self._getAny("TG_BOT_TOKEN", "")
