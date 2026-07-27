import logging
from flask import Flask
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService
from .api_endpoints import create_endpoints

logger = logging.getLogger(__name__)


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"
        self.app.config["OPENAPI_URL_PREFIX"] = "/api"
        self.app.config["OPENAPI_REDOC_PATH"] = "/redoc"
        self.app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
        self.app.config["OPENAPI_SWAGGER_UI_URL"] = (
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
        )

    def get_app(self):
        return self.app

    def initialize_api(
        self,
        api,
        auth_service: AuthService,
        calendar_service: CalendarService,
        notification_service: NotificationService,
    ):
        blueprints = create_endpoints(
            auth_service, calendar_service, notification_service
        )
        for name, blueprint in blueprints.items():
            if hasattr(blueprint, "name") and blueprint.name:
                api.register_blueprint(blueprint)
