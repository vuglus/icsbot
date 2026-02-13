import os
import logging
from flask import Flask
from flask_smorest import Api
from services.config_service import load_config, Config
from services.api_service import get_app, initialize_api
from services.init_service import initialize_app
from services.api_utils import AuthService
from services.database import set_db_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)
config = Config(load_config(
    os.environ.get('CONFIG_PATH', './config/config.yml')
))

set_db_path(config.get('DB_PATH'))
# Get Flask app instance
app = get_app()
auth_service = AuthService(app, config)

# Configure Flask-Smorest API
app.config["API_TITLE"] = "ICS Bot API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/api"
app.config["OPENAPI_REDOC_PATH"] = "/redoc"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Initialize Flask-Smorest API
api = Api(app)

# Initialize API endpoints
initialize_api(api, auth_service, config)

# Print debug info
print(f"App has {len(app.view_functions)} view functions")
for endpoint, view_func in app.view_functions.items():
    print(f"  {endpoint} -> {view_func}")


if __name__ == '__main__':
    # Initialize application
    initialize_app(
        int(config.get('SYNC_INTERVAL_MINUTES', 15)), 
        int(config.get('NOTIFY_INTERVAL_SECONDS', 60))
    )
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5800, debug=False)