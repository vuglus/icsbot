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


def get_notify_before_minutes() -> int:
    """Get notification time before event in minutes from config or environment"""
    # First check environment variable
    notify_before_minutes = os.environ.get('NOTIFY_BEFORE_MINUTES')
    if notify_before_minutes:
        return int(notify_before_minutes)
    
    # Then check config file
    # config = load_config()
    # Using a placeholder since we don't have access to the config instance here
    # This function should be refactored to accept the config instance
    notify_before_minutes = 1440  # Default to 24 hours
    return int(notify_before_minutes)