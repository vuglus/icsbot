import unittest
import tempfile
import os
import sys
import importlib
from services.config_service import Config
from services.database_provider import DatabaseProvider
from services.database import Database


class TestAppStart(unittest.TestCase):
    """Test app startup"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self._orig_environ = os.environ.copy()

    def tearDown(self):
        """Tear down test environment"""
        os.environ.clear()
        os.environ.update(self._orig_environ)
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                pass

    def test_app_creation(self):
        """Test that app can be created"""
        # Set environment variables for testing
        os.environ["API_KEY"] = "test-api-key"
        os.environ["DB_PROVIDER"] = "sqlite"
        os.environ["DB_PATH"] = self.temp_db.name

        # Import app after setting environment variables
        if "app" in sys.modules:
            del sys.modules["app"]
        app_module = importlib.import_module("app")
        app_instance = app_module.app
        flask_app = app_instance.get_app()

        # Check that app was created successfully
        self.assertIsNotNone(flask_app)
        self.assertEqual(flask_app.config["API_TITLE"], "ICS Bot API")
        self.assertEqual(flask_app.config["API_VERSION"], "v1")
        self.assertEqual(flask_app.config["OPENAPI_VERSION"], "3.0.2")

        # Test that we can create a test client
        client = flask_app.test_client()
        self.assertIsNotNone(client)

        # Test that basic routes exist
        response = client.get("/health")
        # Health endpoint should exist (200 or 401 if auth is required)
        self.assertIn(response.status_code, [200, 401])


if __name__ == "__main__":
    unittest.main()
