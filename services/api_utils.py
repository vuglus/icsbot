import logging
from flask import request
from services.config_service import Config

# Configure logging
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, app, config: Config):
        self.app = app
        self.api_key = config.getApiKey()

    def validate_api_key(self) -> bool:
        """Validate API key from request"""
        # Check header first
        data = request.get_json(silent=True) or {}
        api_key = (
            request.headers.get('X-API-Key') or 
            request.args.get('api_key') or 
            data.get("details", {}).get("payload", {})
        )       
        
        # Check query parameter if header not found
        if not api_key:
            api_key = request.args.get('api_key')
        
        # Validate against environment variable or config
        expected_key = self.api_key
        return api_key == expected_key