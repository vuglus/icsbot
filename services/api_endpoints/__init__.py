"""
API Endpoints Package
Each API endpoint is implemented in a separate file.
"""


def create_endpoints(auth_service, calendar_service, notification_service):
    from .health_endpoint import health_blp as health_blueprint
    from .calendar_endpoint import create_calendar_blueprint
    from .cron_endpoint import handle_cron_blueprint
    from .notification_endpoint import create_notification_blueprint
    from .pending_events_endpoint import create_pending_events_blueprint
    from .openapi_endpoint import openapi_blp as openapi_blueprint

    blueprints = {}
    blueprints["health"] = health_blueprint
    blueprints["calendar"] = create_calendar_blueprint(auth_service, calendar_service)
    blueprints["notification"] = create_notification_blueprint(
        auth_service, notification_service
    )
    blueprints["pending_events"] = create_pending_events_blueprint(
        auth_service, notification_service
    )
    blueprints["openapi"] = openapi_blueprint
    blueprints["cron"] = handle_cron_blueprint(
        auth_service, calendar_service, notification_service
    )

    return blueprints
