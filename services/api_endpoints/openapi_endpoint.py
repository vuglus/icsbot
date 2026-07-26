import logging
from flask import jsonify, current_app
from services.api_docs import Blueprint

# Configure logging
logger = logging.getLogger(__name__)

# Create a blueprint for this endpoint
openapi_blp = Blueprint('openapi', __name__, url_prefix='/openapi')

@openapi_blp.route('.json', methods=['GET'])
@openapi_blp.doc(
    summary="Get OpenAPI specification",
    description="Returns the OpenAPI specification for the API"
)
def get_openapi_spec():
    """Get OpenAPI specification"""
    # Note: We don't require API key authentication for the OpenAPI spec
    # as it's typically public documentation
    
    # Try to get the auto-generated spec from Flask-Smorest
    try:
        # Get the spec from the Flask app
        if hasattr(current_app, 'extensions') and 'flask-smorest' in current_app.extensions:
            api = current_app.extensions['flask-smorest']
            openapi_spec = api.spec.to_dict()
            return jsonify(openapi_spec)
    except Exception as e:
        logger.error(f"Error generating OpenAPI spec: {e}")
    
    return jsonify([])
