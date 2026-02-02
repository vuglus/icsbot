# ICS-Gate REST API Specification

## Overview

The ICS-Gate API provides endpoints for external clients to retrieve pending event notifications and confirm delivery. All endpoints require authentication via API key.

## Authentication

### API Key
The API key can be provided in two ways:
1. HTTP Header: `X-API-Key: <api_key>`
2. Query Parameter: `?api_key=<api_key>`

### Authentication Flow
1. Check for API key in header `X-API-Key`
2. If not found, check for `api_key` query parameter
3. Validate against `ICS_GATE_API_KEY` environment variable
4. Return 401 Unauthorized if invalid or missing

## Endpoints

### Get Pending Events
```
GET /events/pending
```

#### Description
Returns a list of events that are ready for notification.

#### Parameters
- `user_id` (optional): Filter events by user ID. When provided, only events for the specified user will be returned. When omitted, all pending events for all users will be returned.

#### Response
```json
{
  "events": [
    {
      "id": 123,
      "uid": "event-uid-123",
      "title": "Team Meeting",
      "description": "Weekly team meeting",
      "location": "Conference Room 1",
      "start_datetime": "2023-06-15T10:00:00+03:00",
      "end_datetime": "2023-06-15T11:00:00+03:00",
      "all_day": false,
      "user_id": "user123",
      "calendar_timezone": "GMT+3"
    }
  ]
}
```

#### Notes
- The `start_datetime` and `end_datetime` values are in the timezone of the calendar (`calendar_timezone`).
- All datetime values follow the ISO 8601 format with timezone information.

#### Response Codes
- 200: Success
- 401: Unauthorized
- 500: Internal server error

#### Example Usage
```
GET /events/pending?user_id=user123
```

### Mark Notification as Delivered
```
POST /notifications/{id}/delivered
```

#### Description
Confirms that a notification has been successfully delivered to the client.

#### Parameters
- Path parameter: `id` - The event ID

#### Request Body
```json
{
  "delivered_at": "2023-06-15T09:30:00Z"
}
```

#### Response
```json
{
  "status": "success",
  "message": "Notification marked as delivered"
}
```

#### Response Codes
- 200: Success
- 400: Bad request (missing/invalid parameters)
- 401: Unauthorized
- 404: Event not found
- 500: Internal server error

### Create Calendar
```
POST /calendars
```

#### Description
Creates a new calendar for a user. If a calendar with the same URL already exists for the user, returns the existing calendar.

#### Request Body
```json
{
  "user_id": "user123",
  "url": "https://example.com/calendar.ics"
}
```

#### Response
```json
{
  "status": "success",
  "message": "Calendar created successfully",
  "calendar": {
    "id": 123,
    "user_id": 1,
    "url": "https://example.com/calendar.ics",
    "timezone": "GMT+3"
  }
}
```

#### Response Codes
- 201: Created (new calendar) or existing calendar returned
- 400: Bad request (missing/invalid parameters)
- 401: Unauthorized
- 500: Internal server error

#### Example Usage
```
POST /calendars
Content-Type: application/json
X-API-Key: your-api-key

{
  "user_id": "user123",
  "url": "https://example.com/calendar.ics"
}
```
## Data Models

### Event
```json
{
  "id": 123,
  "uid": "event-uid-123",
  "title": "Team Meeting",
  "description": "Weekly team meeting",
  "location": "Conference Room 1",
  "start_datetime": "2023-06-15T10:00:00+03:00",
  "end_datetime": "2023-06-15T11:00:00+03:00",
  "all_day": false,
  "user_id": "user123",
  "calendar_timezone": "GMT+3"
}
```

### Notification Confirmation
```json
{
  "delivered_at": "2023-06-15T09:30:00Z"
}
```

## Security Considerations

### API Key Protection
- API key should be at least 32 characters
- Use HTTPS in production to prevent key interception
- API key should be stored securely (environment variable)
- Consider API key rotation mechanism

### Rate Limiting
- Implement rate limiting to prevent abuse
- Default: 100 requests per minute per API key
- Return appropriate headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

### Input Validation
- Validate all input parameters
- Sanitize user-provided data
- Limit request body size

## Error Handling

### Error Response Format
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
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Unexpected server error
- 503: Service Unavailable - Temporary server issue

## CORS Support

For web-based clients, CORS headers should be configured:
- `Access-Control-Allow-Origin: *` (or specific domains)
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: X-API-Key, Content-Type`

## Versioning

API versioning will be handled through the URL path:
```
/v1/events/pending
```

## Performance Considerations

### Pagination
For endpoints that return lists, implement pagination:
```
GET /events/pending?page=1&limit=50
```

### Caching
Use appropriate cache headers for read-only endpoints:
- `Cache-Control: no-cache` for dynamic data
- ETags for conditional requests

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

## Health Check Endpoint

```
GET /health
```

#### Description
Returns the health status of the service.

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2023-06-15T09:30:00Z",
  "version": "1.0.0"
}
```

## Implementation Considerations

### Framework
Use a lightweight web framework like Flask or FastAPI for Python implementation.

### Database Access
- Use connection pooling for database connections
- Implement proper transaction handling
- Use prepared statements to prevent SQL injection

### Concurrency
- Handle concurrent requests properly
- Use thread-safe operations where needed
- Consider async processing for long-running operations

### Testing
- Unit tests for each endpoint
- Integration tests for API workflows
- Load testing for performance validation