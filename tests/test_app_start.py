import unittest
import tempfile
import os
import sys
import importlib
from services.database import set_db_path, set_db_provider


class TestAppStart(unittest.TestCase):
    """Test app startup"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        set_db_provider('sqlite')
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
    def test_app_creation(self):
        """Test that app can be created"""
        # Set environment variables for testing
        os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
        
        # Import app after setting environment variables
        if 'app' in sys.modules:
            del sys.modules['app']
        app_module = importlib.import_module('app')
        app = app_module.app
        
        # Check that app was created successfully
        self.assertIsNotNone(app)
        self.assertEqual(app.config["API_TITLE"], "ICS Bot API")
        self.assertEqual(app.config["API_VERSION"], "v1")
        self.assertEqual(app.config["OPENAPI_VERSION"], "3.0.2")
        
        # Test that we can create a test client
        client = app.test_client()
        self.assertIsNotNone(client)
        
        # Test that basic routes exist
        response = client.get('/health')
        # Health endpoint should exist (200 or 401 if auth is required)
        self.assertIn(response.status_code, [200, 401])

if __name__ == '__main__':
    unittest.main()