import os
import logging
import yaml
from typing import Dict

# Configure logging
logger = logging.getLogger(__name__)

# Global variables

# Load configuration from YAML file
def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class Config:
    def __init__(self, config):
        self.config = config

    def _getAny(self, key: str, default=None) -> str:
        env = os.environ.get(key);
        return env if env else self.config.get(key, default)
    
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

    def get_sync_interval(self) -> int:
        return self._getAny('SYNC_INTERVAL_MINUTES', 30)
    
    def get_notify_interval(self) -> int:
        return self._getAny('NOTIFY_INTERVAL_SECONDS', 60)
    
    def getTZone(self) -> str:
        return self._getAny('TIMEZONE_DEFAULT', 'UTC')

    def get_port(self) -> str:
        return self._getAny('EXT_PORT', '8080')
