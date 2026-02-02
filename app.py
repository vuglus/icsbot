import os
import logging
from services.api_service import get_app
from services.init_service import initialize_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
DB_PATH = os.environ.get('DB_PATH', 'icsgate.db')
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'config.yml')
SYNC_INTERVAL_MINUTES = int(os.environ.get('SYNC_INTERVAL_MINUTES', 15))
NOTIFY_INTERVAL_SECONDS = int(os.environ.get('NOTIFY_INTERVAL_SECONDS', 60))

# Get Flask app instance
app = get_app()

# Initialize FlaskApiSpec and register endpoints
def init_apispec(app):
    """Initialize FlaskApiSpec after app is created"""
    from flask_apispec import FlaskApiSpec
    from apispec import APISpec
    from apispec.ext.marshmallow import MarshmallowPlugin
    
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='ICS-Gate API',
            version='1.0.0',
            openapi_version='3.0.0',
            plugins=[MarshmallowPlugin()],
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
    })
    docs = FlaskApiSpec(app)
    return docs

# Register endpoints with FlaskApiSpec
def register_endpoints_with_apispec(app, docs):
    """Register endpoints with FlaskApiSpec"""
    # Import and register API endpoints
    from services.api_endpoints.health_endpoint import register_health_endpoint
    from services.api_endpoints.pending_events_endpoint import register_pending_events_endpoint
    from services.api_endpoints.notification_endpoint import register_notification_endpoint
    from services.api_endpoints.calendar_endpoint import register_calendar_endpoint
    from services.api_endpoints.openapi_endpoint import register_openapi_endpoint

    # Register all endpoints and collect view functions for flask-apispec
    view_functions = []
    view_functions.extend(register_health_endpoint(app) or [])
    view_functions.extend(register_pending_events_endpoint(app) or [])
    view_functions.extend(register_notification_endpoint(app) or [])
    view_functions.extend(register_calendar_endpoint(app) or [])
    register_openapi_endpoint(app)  # This doesn't need to be registered with flask-apispec
    
    # Register endpoints with FlaskApiSpec
    for view_func in view_functions:
        try:
            docs.register(view_func)
        except Exception as e:
            logger.warning(f"Could not register {view_func.__name__} with FlaskApiSpec: {e}")

# Register endpoints with FlaskApiSpec
with app.app_context():
    docs = init_apispec(app)
    register_endpoints_with_apispec(app, docs)

if __name__ == '__main__':
    # Initialize application
    initialize_app(SYNC_INTERVAL_MINUTES, NOTIFY_INTERVAL_SECONDS)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5800, debug=False)