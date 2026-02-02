import logging
from flask import jsonify
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def register_health_endpoint(app):
    """Register health check endpoint"""
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })