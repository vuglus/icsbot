# Notification Management API Specification

## Overview

This document details the API endpoints for managing event notifications in ICS-Gate.

## Endpoint: Get Pending Events

### URL
```
GET /events/pending
```

### Description
Retrieves events that are approaching and need to be notified to clients.

### Authentication
Requires valid API key in header or query parameter.

### Parameters
None

### Response
```json
{
  "events": [
    {
      "id": 123,
      "uid": "event-uid-123",
      "title": "Team Meeting",
      "description": "Weekly team meeting to discuss project progress",
      "location": "Conference Room 3",
      "start_datetime": "2023-06-15T10:00:00Z",
      "end_datetime": "2023-06-15T11:00:00Z",
      "all_day": false
    }
  ]
}
```

### Response Fields
- `events`: Array of pending events
  - `id`: Internal event ID (integer)
  - `uid`: ICS event unique identifier (string)
  - `title`: Event title (string)
  - `description`: Event description from ICS DESCRIPTION field (string, optional)
  - `location`: Event location from ICS LOCATION field (string, optional)
  - `start_datetime`: Event start time in ISO 8601 format (string)
  - `end_datetime`: Event end time in ISO 8601 format (string)
  - `all_day`: Whether this is an all-day event (boolean)

### Response Codes
- 200: Success
- 401: Unauthorized
- 500: Internal server error

### Implementation Logic
1. Query database for events where:
   - `notified` = false
   - `start_datetime` is within notification window
   - `start_datetime` is in the future
2. Return events ordered by start time

## Endpoint: Mark Notification as Delivered

### URL
```
POST /notifications/{id}/delivered
```

### Description
Confirms that a notification has been successfully delivered to the client.

### Authentication
Requires valid API key in header or query parameter.

### Parameters
- Path parameter: `id` - The internal event ID (integer)

### Request Body
```json
{
  "delivered_at": "2023-06-15T09:30:00Z"
}
```

### Request Fields
- `delivered_at`: Timestamp when notification was delivered in ISO 8601 format (string, optional)

### Response
```json
{
  "status": "success",
  "message": "Notification marked as delivered",
  "event_id": 123
}
```

### Response Fields
- `status`: Operation status (string)
- `message`: Human-readable message (string)
- `event_id`: The ID of the event that was updated (integer)

### Response Codes
- 200: Success
- 400: Bad request (missing/invalid parameters)
- 401: Unauthorized
- 404: Event not found
- 500: Internal server error

### Implementation Logic
1. Validate event ID exists
2. Update event `notified` field to true
3. Optionally update delivered timestamp
4. Return success response

## Endpoint: Health Check

### URL
```
GET /health
```

### Description
Returns the health status of the service.

### Authentication
No authentication required.

### Parameters
None

### Response
```json
{
  "status": "healthy",
  "timestamp": "2023-06-15T09:30:00Z",
  "version": "1.0.0"
}
```

### Response Fields
- `status`: Service status (string)
- `timestamp`: Current server time in ISO 8601 format (string)
- `version`: Service version (string)

### Response Codes
- 200: Success

## Error Responses

### Format
All error responses follow this format:
```json
{
  "error": {
    "code": 401,
    "message": "Unauthorized",
    "details": "Invalid API key provided"
  }
}
```

### Common Error Codes
- 400: Bad Request - Invalid input parameters
- 401: Unauthorized - Missing or invalid API key
- 404: Not Found - Resource not found
- 500: Internal Server Error - Unexpected server error

## Security Considerations

### API Key Protection
- API key must be provided for protected endpoints
- Use HTTPS in production to prevent key interception
- Rate limit requests per API key

### Input Validation
- Validate all input parameters
- Sanitize user-provided data
- Limit request body size

### Rate Limiting
- Implement rate limiting to prevent abuse
- Default: 100 requests per minute per API key
- Return appropriate headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Performance Considerations

### Caching
- Use appropriate cache headers for read-only endpoints
- `Cache-Control: no-cache` for dynamic data
- ETags for conditional requests

### Pagination
For future expansion, design with pagination in mind:
```
GET /events/pending?page=1&limit=50
```

## Implementation Details

### Database Queries

#### Get Pending Events
```sql
SELECT e.id, e.uid, e.title, e.description, e.location, e.start_datetime, e.end_datetime, e.all_day
FROM events e
JOIN calendars c ON e.calendar_id = c.id
WHERE e.notified = FALSE
  AND e.start_datetime <= datetime('now', '+' || ? || ' minutes')
  AND e.start_datetime > datetime('now')
ORDER BY e.start_datetime ASC
```

#### Mark Notification as Delivered
```sql
UPDATE events
SET notified = TRUE
WHERE id = ? AND notified = FALSE
```

### Notification Window Calculation
- Default notification time: 10 minutes before event
- Configurable via `NOTIFY_BEFORE_MINUTES` environment variable
- All-day events: Notify at a specific time (e.g., 9:00 AM)

### Timezone Handling
- Store all datetimes in UTC
- Convert to user's timezone for display if needed
- Handle timezone information from ICS files

## Monitoring and Logging

### Request Logging
- Log all API requests with:
  - Timestamp
  - Method and path
  - Response code
  - Response time
  - Client IP (if applicable)

### Error Logging
- Log detailed error information for 5xx errors
- Include request context for troubleshooting
- Log security events (invalid API keys, rate limiting)

## Testing

### Unit Tests
- Test each endpoint with valid and invalid inputs
- Test authentication logic
- Test edge cases (empty results, invalid IDs)

### Integration Tests
- Test complete workflow from pending events to delivery confirmation
- Test database interactions
- Test error conditions

### Performance Tests
- Test response times under load
- Test concurrent requests
- Test large result sets