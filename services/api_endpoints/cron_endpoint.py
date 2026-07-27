import logging
from flask import request, jsonify
from marshmallow import Schema, fields
from services.api_docs import Blueprint
from ..calendar_service import CalendarService
from ..api_utils import AuthService

logger = logging.getLogger(__name__)


def handle_cron_blueprint(
    auth_service: AuthService, calendar_service: CalendarService, notification_service
):
    calendar_blp = Blueprint("cron", __name__, url_prefix="/")

    @calendar_blp.route("", methods=["POST"])
    @calendar_blp.doc(
        summary="Main entry point", description="", security=[{"ApiKeyAuth": []}]
    )
    @calendar_blp.response(201, description="Job executed successfully")
    def handle_cron_api():
        logger.info(request.get_data())
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            calendar_service.sync_all_calendars()
            notification_service.check_pending_notifications()
            return jsonify({"status": "success", "message": ""}), 200
        except Exception as e:
            logger.error(f"Error handling cron job: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    return calendar_blp
