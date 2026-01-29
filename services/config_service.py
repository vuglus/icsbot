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