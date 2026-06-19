import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global variables

class Config:
    def __init__(self, config):
        self.config = config

    def _getAny(self, key: str, default=None) -> str:
        # Check config dict first, then env vars (config takes precedence)
        val = self.config.get(key)
        if val is not None:
            return val
        return os.environ.get(key, default)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def getApiKey(self):
        key = os.environ.get('API_KEY')
        return key if key else self.config.get('api_key')
    
    def getDBProvider(self):        
        return self._getAny('DB_PROVIDER')

    def getDBPath(self):
        return self._getAny('DB_PATH')

    def getDBEndpoint(self):
        return self._getAny('DB_ENDPOINT')

    def get_notify_before_minutes(self) -> int:
        return int(self._getAny('NOTIFY_BEFORE_MINUTES', 15))

    def getTZone(self) -> str:
        return self._getAny('TIMEZONE_DEFAULT', 'UTC')

    def get_port(self) -> int:
        return int(self._getAny('EXT_PORT', 8080))
