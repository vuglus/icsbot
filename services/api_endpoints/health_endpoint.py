import logging
from flask import jsonify
from datetime import datetime
from ..api_docs import Blueprint

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for the health endpoint
health_blp = Blueprint('health', __name__, url_prefix='/health')

@health_blp.route('', methods=['GET'])
@health_blp.doc(
    summary="Health check",
    description="Returns the health status of the application"
)
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

def register_health_endpoint(app):
    """Register health check endpoint"""
    # Register the blueprint with the app
    app.register_blueprint(health_blp)
    
    # Return the view function
    return health_check