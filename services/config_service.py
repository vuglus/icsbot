import os
import logging
import yaml
from typing import Dict

# Configure logging
logger = logging.getLogger(__name__)

# Global variables
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'config.yml')

def load_config() -> Dict:
    """Load configuration from YAML file"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {CONFIG_PATH}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def get_api_key() -> str:
    """Get API key from environment or config"""
    api_key = os.environ.get('ICS_GATE_API_KEY', '')
    if not api_key:
        config = load_config()
        api_key = config.get('api_key', '')
    return api_key

def get_notify_before_minutes() -> int:
    """Get notification time before event in minutes from config or environment"""
    # First check environment variable
    notify_before_minutes = os.environ.get('NOTIFY_BEFORE_MINUTES')
    if notify_before_minutes:
        return int(notify_before_minutes)
    
    # Then check config file
    config = load_config()
    notify_before_minutes = config.get('NOTIFY_BEFORE_MINUTES', 1440)  # Default to 24 hours
    return int(notify_before_minutes)