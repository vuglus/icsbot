import logging
from flask import request, jsonify
from services.api_docs import Blueprint

logger = logging.getLogger(__name__)


def create_notification_blueprint(auth_service, notification_service):
    notification_blp = Blueprint("notifications", __name__, url_prefix="/notifications")

    @notification_blp.route("/<string:event_id>/delivered", methods=["POST"])
    @notification_blp.doc(
        summary="Mark notification as delivered",
        description="Marks a notification as delivered",
        security=[{"ApiKeyAuth": []}],
    )
    def mark_notification_delivered_api(event_id):
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        return jsonify(
            {
                "status": "success",
                "message": "Notification tracking removed",
                "event_id": event_id,
            }
        )

    return notification_blp
