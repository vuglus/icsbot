import logging
from flask import request
from services.config_service import get_api_key

# Configure logging
logger = logging.getLogger(__name__)

def validate_api_key() -> bool:
    """Validate API key from request"""
    # Check header first
    api_key = request.headers.get('X-API-Key')
    
    # Check query parameter if header not found
    if not api_key:
        api_key = request.args.get('api_key')
    
    # Validate against environment variable or config
    expected_key = get_api_key()
    
    return api_key == expected_key