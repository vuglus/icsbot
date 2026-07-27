import unittest
import json
import tempfile
import os
from flask import Flask
from flask_smorest import Api
from services.api_service import App
from services.api_utils import AuthService
from services.database import Database
from services.config_service import Config
from services.database_provider import DatabaseProvider


class TestAPIUserFiltering(unittest.TestCase):
    """Test API calendar endpoints"""

    def setUp(self):
        """Set up test environment"""
        os.environ["ICS_GATE_API_KEY"] = "test-api-key"

        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        config = Config(
            {
                "api_key": "test-api-key",
                "DB_PROVIDER": "sqlite",
                "DB_PATH": self.temp_db.name,
            }
        )

        self.provider = DatabaseProvider(config)
        self.db = Database(self.provider, config)

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"

        api = Api(self.app)

        class MockAuthService:
            def validate_api_key(self):
                return True

        self.auth_service = MockAuthService()

        from services.calendar_service import CalendarService
        from services.notification_service import NotificationService
        from services.api_endpoints import create_endpoints

        self.calendar_service = CalendarService(self.db, config)
        self.notification_service = NotificationService(
            self.db, config, self.calendar_service
        )

        blueprints = create_endpoints(
            self.auth_service, self.calendar_service, self.notification_service
        )
        for name, blueprint in blueprints.items():
            if hasattr(blueprint, "name") and blueprint.name:
                api.register_blueprint(blueprint)

        self.client = self.app.test_client()

    def tearDown(self):
        """Tear down test environment"""
        if hasattr(self, "provider") and self.provider:
            self.provider.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_get_calendars(self):
        """Test getting calendars via API"""
        calendar_entity, _, _ = self.provider.get_entities()

        calendar_entity.create_calendar("chat1", "tg", "https://example.com/cal1.ics")
        calendar_entity.create_calendar("chat2", "max", "https://example.com/cal2.ics")

        response = self.client.get(
            "/calendars", headers={"X-Auth-Token": "test-api-key"}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("calendars", data)
        self.assertEqual(len(data["calendars"]), 2)

        chat_ids = [c["chat_id"] for c in data["calendars"]]
        self.assertIn("chat1", chat_ids)
        self.assertIn("chat2", chat_ids)


if __name__ == "__main__":
    unittest.main()
