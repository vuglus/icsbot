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

if __name__ == '__main__':
    # Initialize application
    initialize_app(SYNC_INTERVAL_MINUTES, NOTIFY_INTERVAL_SECONDS)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5800, debug=False)