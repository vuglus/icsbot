import unittest
import json
import os
from flask import Flask
from flask_smorest import Api
from services.database import Database
from services.config_service import Config
from services.database_provider import DatabaseProvider


class TestAPIIntegration(unittest.TestCase):
    """Test API integration endpoints"""

    def setUp(self):
        """Set up test environment"""
        os.environ["ICS_GATE_API_KEY"] = "test-api-key"
        config = Config(
            {
                "api_key": "test-api-key",
                "DB_PROVIDER": "sqlite",
                "DB_PATH": ":memory:",
            }
        )
        self.provider = DatabaseProvider(config=config)
        self.db = Database(self.provider, config=config)
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"

        api = Api(self.app)

        from services.api_utils import AuthService
        from services.calendar_service import CalendarService
        from services.notification_service import NotificationService
        from services.api_endpoints import create_endpoints

        class MockAuthService:
            def validate_api_key(self):
                from flask import request

                api_key = request.headers.get("X-Auth-Token")
                return api_key == "test-api-key"

        self.auth_service = MockAuthService()
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
        self.provider.close()

    def test_full_api_flow(self):
        """Test full API flow: create calendar and verify via direct DB access"""
        calendar_data = {
            "chat_id": "test_chat",
            "chat_type": "tg",
            "url": "https://example.com/calendar.ics",
        }

        response = self.client.post(
            "/calendars", json=calendar_data, headers={"X-Auth-Token": "test-api-key"}
        )

        self.assertEqual(response.status_code, 201)
        calendar_response = json.loads(response.data)
        self.assertEqual(calendar_response["status"], "success")
        calendar_id = calendar_response["calendar"]["id"]

        calendar_entity, sent_notification_entity, _ = self.provider.get_entities()

        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)
        self.assertEqual(calendars[0].chat_id, "test_chat")
        self.assertEqual(calendars[0].chat_type, "tg")
        self.assertEqual(calendars[0].url, "https://example.com/calendar.ics")


if __name__ == "__main__":
    unittest.main()
