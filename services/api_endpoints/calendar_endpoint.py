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
        name = fields.Str(
            required=False,
            load_default=None,
            metadata={"description": "Calendar display name"},
        )

    class UpdateCalendarSchema(Schema):
        name = fields.Str(
            required=False, metadata={"description": "Calendar display name"}
        )
        url = fields.Str(required=False, metadata={"description": "Calendar URL"})
        client_type = fields.Str(
            required=False, metadata={"description": "Calendar type: ics or caldav"}
        )
        timezone = fields.Str(
            required=False, metadata={"description": "Timezone (e.g. GMT+3)"}
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
            name = args.get("name")

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
                chat_id, chat_type, url, client_type, name
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
                        "name": calendar.name,
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
                    "client_type": calendar.client_type,
                    "timezone": calendar.timezone,
                    "last_sync_at": calendar.last_sync_at,
                    "name": calendar.name,
                }
                calendars_data.append(calendar_data)
            return jsonify({"calendars": calendars_data})
        except Exception as e:
            logger.error(f"Error getting calendars: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    @calendar_blp.route("/<string:calendar_id>", methods=["PUT"])
    @calendar_blp.arguments(UpdateCalendarSchema)
    @calendar_blp.doc(
        summary="Update calendar",
        description="Updates an existing calendar's fields",
        security=[{"ApiKeyAuth": []}],
    )
    @calendar_blp.response(200, description="Calendar updated successfully")
    def update_calendar_api(args, calendar_id):
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            calendar = calendar_service.get_calendar_by_id(calendar_id)
            if not calendar:
                return jsonify(
                    {"error": {"code": 404, "message": "Calendar not found"}}
                ), 404

            update_kwargs = {}
            for field in ("name", "url", "client_type", "timezone"):
                if field in args and args[field] is not None:
                    if field == "client_type" and args[field] not in ("ics", "caldav"):
                        return jsonify(
                            {
                                "error": {
                                    "code": 400,
                                    "message": "Invalid client_type. Must be ics or caldav",
                                }
                            }
                        ), 400
                    update_kwargs[field] = args[field]

            if not update_kwargs:
                return jsonify(
                    {"error": {"code": 400, "message": "No fields to update"}}
                ), 400

            updated = calendar_service.update_calendar(calendar_id, **update_kwargs)
            return jsonify(
                {
                    "status": "success",
                    "message": "Calendar updated successfully",
                    "calendar": {
                        "id": updated.id,
                        "chat_id": updated.chat_id,
                        "chat_type": updated.chat_type,
                        "url": updated.url,
                        "client_type": updated.client_type,
                        "timezone": updated.timezone,
                        "name": updated.name,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
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

    class CreateEventSchema(Schema):
        summary = fields.Str(required=True, metadata={"description": "Event title"})
        description = fields.Str(
            required=False,
            load_default="",
            metadata={"description": "Event description"},
        )
        location = fields.Str(
            required=False, load_default="", metadata={"description": "Event location"}
        )
        start = fields.Str(
            required=True, metadata={"description": "Start time (ISO 8601)"}
        )
        end = fields.Str(
            required=False,
            load_default=None,
            metadata={"description": "End time (ISO 8601)"},
        )
        all_day = fields.Bool(
            required=False,
            load_default=False,
            metadata={"description": "All day event"},
        )

    @calendar_blp.route("/<string:calendar_id>/events", methods=["POST"])
    @calendar_blp.arguments(CreateEventSchema)
    @calendar_blp.doc(
        summary="Create calendar event",
        description="Creates a new event in the calendar (CalDAV only)",
        security=[{"ApiKeyAuth": []}],
    )
    @calendar_blp.response(201, description="Event created successfully")
    def create_event_api(args, calendar_id):
        if not auth_service.validate_api_key():
            return jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
        try:
            calendar = calendar_service.get_calendar_by_id(calendar_id)
            if not calendar:
                return jsonify(
                    {"error": {"code": 404, "message": "Calendar not found"}}
                ), 404

            if calendar.client_type == "ics":
                return jsonify(
                    {
                        "error": {
                            "code": 400,
                            "message": "Adding events is not supported for ICS calendars",
                        }
                    }
                ), 400

            event_uid = calendar_service.add_event(
                calendar=calendar,
                summary=args["summary"],
                start=args["start"],
                end=args.get("end"),
                description=args.get("description", ""),
                location=args.get("location", ""),
                all_day=args.get("all_day", False),
            )

            if not event_uid:
                return jsonify(
                    {"error": {"code": 500, "message": "Failed to create event"}}
                ), 500

            return jsonify(
                {
                    "status": "success",
                    "message": "Event created successfully",
                    "event": {"uid": event_uid},
                }
            ), 201
        except ValueError as e:
            return jsonify({"error": {"code": 400, "message": str(e)}}), 400
        except PermissionError as e:
            return jsonify({"error": {"code": 403, "message": str(e)}}), 403
        except Exception as e:
            logger.error(f"Error creating event for calendar {calendar_id}: {e}")
            return jsonify(
                {"error": {"code": 500, "message": "Internal Server Error"}}
            ), 500

    return calendar_blp
