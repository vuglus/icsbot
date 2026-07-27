import logging
from flask import request, jsonify
from marshmallow import Schema, fields
from services.api_docs import Blueprint
from ..calendar_service import CalendarService

logger = logging.getLogger(__name__)


def create_calendar_blueprint(auth_service, calendar_service: CalendarService):
    calendar_blp = Blueprint("calendars", __name__, url_prefix="/calendars")

    class ListCalendarsSchema(Schema):
        user_id = fields.Str(
            required=False, metadata={"description": "Filter calendars by user ID"}
        )

    class CreateCalendarSchema(Schema):
        chat_id = fields.Str(
            required=True, metadata={"description": "Chat ID (Telegram or Max)"}
        )
        chat_type = fields.Str(
            required=True, metadata={"description": "Chat type: tg or max"}
        )
        url = fields.Str(required=True, metadata={"description": "Calendar URL"})
        client_type = fields.Str(
            required=False,
            load_default="ics",
            metadata={"description": "Calendar type: ics or caldav"},
        )

    @calendar_blp.route("", methods=["POST"])
    @calendar_blp.arguments(CreateCalendarSchema)
    @calendar_blp.doc(
        summary="Create calendar",
        description="Creates a new calendar for a chat",
        security=[{"ApiKeyAuth": []}],
    )
    @calendar_blp.response(201, description="Calendar created successfully")
    def create_calendar_api(args):
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            chat_id = args["chat_id"]
            chat_type = args["chat_type"]
            url = args["url"]
            client_type = args.get("client_type", "ics")

            if chat_type not in ("tg", "max"):
                return jsonify(
                    {
                        "error": {
                            "code": 400,
                            "message": "Invalid chat_type. Must be tg or max",
                        }
                    }
                ), 400

            if client_type not in ("ics", "caldav"):
                return jsonify(
                    {
                        "error": {
                            "code": 400,
                            "message": "Invalid client_type. Must be ics or caldav",
                        }
                    }
                ), 400

            if not url.startswith(("http://", "https://")):
                return jsonify(
                    {"error": {"code": 400, "message": "Invalid URL format"}}
                ), 400

            calendar = calendar_service.create_calendar(
                chat_id, chat_type, url, client_type
            )

            return jsonify(
                {
                    "status": "success",
                    "message": "Calendar created successfully",
                    "calendar": {
                        "id": calendar.id,
                        "chat_id": calendar.chat_id,
                        "chat_type": calendar.chat_type,
                        "url": calendar.url,
                        "client_type": calendar.client_type,
                        "timezone": calendar.timezone,
                    },
                }
            ), 201
        except Exception as e:
            logger.error(f"Error creating calendar: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    @calendar_blp.route("", methods=["GET"])
    @calendar_blp.arguments(ListCalendarsSchema, location="query")
    @calendar_blp.doc(
        summary="List calendars",
        description="Returns a list of calendars, optionally filtered by user ID",
        security=[{"ApiKeyAuth": []}],
    )
    def list_calendars_api(args):
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            user_id = args.get("user_id") if args else None
            calendars = calendar_service.get_calendars(user_id)
            calendars_data = []
            for calendar in calendars:
                calendar_data = {
                    "id": calendar.id,
                    "user_id": calendar.user_id,
                    "chat_id": calendar.chat_id,
                    "chat_type": calendar.chat_type,
                    "url": calendar.url,
                    "timezone": calendar.timezone,
                    "last_sync_at": calendar.last_sync_at,
                }
                calendars_data.append(calendar_data)
            return jsonify({"calendars": calendars_data})
        except Exception as e:
            logger.error(f"Error getting calendars: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    @calendar_blp.route("/<string:calendar_id>", methods=["DELETE"])
    @calendar_blp.doc(
        summary="Delete calendar",
        description="Deletes a calendar by ID, optionally checking user ownership",
        security=[{"ApiKeyAuth": []}],
    )
    def delete_calendar_api(calendar_id):
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            user_id = request.args.get("user_id")
            deleted = calendar_service.delete_calendar(calendar_id, user_id)
            if deleted:
                return jsonify(
                    {"status": "success", "message": "Calendar deleted successfully"}
                )
            else:
                calendar = calendar_service.get_calendar_by_id(calendar_id)
                if calendar:
                    return jsonify(
                        {
                            "error": {
                                "code": 403,
                                "message": "Forbidden: You do not have permission to delete this calendar",
                            }
                        }
                    ), 403
                else:
                    return jsonify(
                        {"error": {"code": 404, "message": "Calendar not found"}}
                    ), 404
        except Exception as e:
            logger.error(f"Error deleting calendar: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    @calendar_blp.route("/<string:calendar_id>/sync", methods=["PUT"])
    @calendar_blp.doc(
        summary="Force calendar synchronization",
        description="Triggers immediate synchronization for a specific calendar",
        security=[{"ApiKeyAuth": []}],
    )
    def sync_calendar_api(calendar_id):
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            calendar = calendar_service.get_calendar_by_id(calendar_id)
            if not calendar:
                return jsonify(
                    {"error": {"code": 404, "message": "Calendar not found"}}
                ), 404
            events = calendar_service.fetch_events(calendar)
            return jsonify(
                {
                    "status": "success",
                    "message": f"Calendar synchronized, {len(events)} events fetched",
                }
            )
        except Exception as e:
            logger.error(f"Error synchronizing calendar {calendar_id}: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    @calendar_blp.route("/sync", methods=["PUT"])
    @calendar_blp.doc(
        summary="Force calendar synchronization for all calendars",
        description="Triggers immediate synchronization",
        security=[{"ApiKeyAuth": []}],
    )
    def sync_all_calendar_api():
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            calendar_service.sync_all_calendars()
            return jsonify(
                {"status": "success", "message": "All calendars synchronized"}
            )
        except Exception as e:
            logger.error(f"Error synchronizing calendars: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    return calendar_blp
