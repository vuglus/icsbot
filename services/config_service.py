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
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def getApiKey(self):
        key = os.environ.get('API_KEY')
        return key if key else self.config.get('api_key')
    
    def getDBProvider(self):        
        return self.config.get('DB_PROVIDER')

    def getDBPath(self):
        return self.config.get('DB_PATH')

    def get_notify_before_minutes(self) -> int:
        """Get notification time before event in minutes from config or environment"""
        # First check environment variable
        notify_before_minutes = os.environ.get('NOTIFY_BEFORE_MINUTES')
        if notify_before_minutes:
            return int(notify_before_minutes)
        
        notify_before_minutes = 1440  # Default to 24 hours
        return int(notify_before_minutes)