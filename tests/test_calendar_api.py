import unittest
import json
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_smorest import Api
from services.config_service import Config
from services.database import Database
from services.database_provider import DatabaseProvider
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService
from services.api_endpoints import create_endpoints


class TestCalendarAPI(unittest.TestCase):
    """Test cases for calendar API endpoints"""

    def setUp(self):
        """Set up test environment"""
        os.environ["ICS_GATE_API_KEY"] = "test-api-key"
        os.environ["API_KEY"] = "test-api-key"

        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db_file.close()

        config_data = {
            "api_key": "test-api-key",
            "DB_PROVIDER": "sqlite",
            "DB_PATH": self.temp_db_file.name,
            "notify_before_minutes": 10,
        }
        self.config = Config(config_data)

        provider = DatabaseProvider(self.config)
        self.database = Database(provider, self.config)

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"

        self.auth_service = AuthService(self.app, self.config)
        self.calendar_service = CalendarService(self.database, self.config)
        self.notification_service = NotificationService(
            self.database, self.config, self.calendar_service
        )

        api = Api(self.app)
        blueprints = create_endpoints(
            self.auth_service, self.calendar_service, self.notification_service
        )
        for name, blueprint in blueprints.items():
            if hasattr(blueprint, "name") and blueprint.name:
                api.register_blueprint(blueprint)

        self.client = self.app.test_client()

    def tearDown(self):
        """Tear down test environment"""
        if (
            hasattr(self.database.provider, "_sqlite_connection")
            and self.database.provider._sqlite_connection
        ):
            self.database.provider._sqlite_connection.close()
        if os.path.exists(self.temp_db_file.name):
            os.unlink(self.temp_db_file.name)

    def test_create_calendar_success(self):
        """Test successful calendar creation"""
        test_data = {
            "chat_id": "12345",
            "chat_type": "tg",
            "url": "https://example.com/calendar.ics",
        }

        response = self.client.post(
            "/calendars", json=test_data, headers={"X-Auth-Token": "test-api-key"}
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("calendar", data)
        self.assertEqual(data["calendar"]["url"], "https://example.com/calendar.ics")
        self.assertEqual(data["calendar"]["chat_id"], "12345")
        self.assertEqual(data["calendar"]["chat_type"], "tg")

    def test_create_calendar_duplicate(self):
        """Test creating duplicate calendar (should return existing)"""
        test_data = {
            "chat_id": "12345",
            "chat_type": "tg",
            "url": "https://example.com/calendar.ics",
        }

        response1 = self.client.post(
            "/calendars", json=test_data, headers={"X-Auth-Token": "test-api-key"}
        )

        response2 = self.client.post(
            "/calendars", json=test_data, headers={"X-Auth-Token": "test-api-key"}
        )

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)

        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        self.assertEqual(data1["calendar"]["id"], data2["calendar"]["id"])

        calendars = self.calendar_service.calendars.get_calendars()
        self.assertEqual(len(calendars), 1)

    def test_create_calendar_invalid_url(self):
        """Test creating calendar with invalid URL"""
        test_data = {
            "chat_id": "12345",
            "chat_type": "tg",
            "url": "invalid-url",
        }

        response = self.client.post(
            "/calendars", json=test_data, headers={"X-Auth-Token": "test-api-key"}
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_create_calendar_missing_fields(self):
        """Test creating calendar with missing required fields"""
        test_data = {
            "chat_id": "12345",
        }

        response = self.client.post(
            "/calendars", json=test_data, headers={"X-Auth-Token": "test-api-key"}
        )

        self.assertEqual(response.status_code, 422)

    def test_create_calendar_unauthorized(self):
        """Test creating calendar without valid API key"""
        test_data = {
            "chat_id": "12345",
            "chat_type": "tg",
            "url": "https://example.com/calendar.ics",
        }

        response = self.client.post("/calendars", json=test_data)

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_list_calendars(self):
        """Test listing calendars"""
        test_data = {
            "chat_id": "12345",
            "chat_type": "tg",
            "url": "https://example.com/calendar.ics",
        }

        self.client.post(
            "/calendars", json=test_data, headers={"X-Auth-Token": "test-api-key"}
        )

        response = self.client.get(
            "/calendars", headers={"X-Auth-Token": "test-api-key"}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("calendars", data)
        self.assertEqual(len(data["calendars"]), 1)


if __name__ == "__main__":
    unittest.main()
