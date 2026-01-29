
# Testing Specification

## Overview

This document outlines the testing strategy for ICS-Gate, including unit tests, integration tests, and end-to-end tests.

## Testing Framework

### Python Testing
- **pytest**: Primary testing framework
- **pytest-cov**: Code coverage reporting
- **requests-mock**: HTTP request mocking
- **freezegun**: Time manipulation for tests

## Test Structure

### Unit Tests
Test individual functions and classes in isolation.

#### Directory Structure
```
tests/
├── unit/
│   ├── test_ics_parser.py
│   ├── test_database.py
│   ├── test_api_auth.py
│   └── test_scheduler.py
├── integration/
│   ├── test_sync_flow.py
│   ├── test_api_endpoints.py
│   └── test_notification_flow.py
└── conftest.py
```

### Test Configuration
- Use `conftest.py` for shared fixtures
- Environment-specific configurations
- Test database setup and teardown

## Unit Tests

### ICS Parser Tests
```python
def test_parse_valid_ics():
    """Test parsing a valid ICS file"""
    ics_content = load_fixture("valid_calendar.ics")
    events = parse_ics(ics_content)
    assert len(events) == 5
    assert events[0].title == "Team Meeting"

def test_parse_ics_with_description_and_location():
    """Test parsing ICS with DESCRIPTION and LOCATION fields"""
    ics_content = load_fixture("detailed_event.ics")
    events = parse_ics(ics_content)
    assert events[0].description == "Weekly team meeting"
    assert events[0].location == "Conference Room 3"

def test_parse_recurring_events():
    """Test parsing recurring events"""
    ics_content = load_fixture("recurring_events.ics")
    events = parse_ics(ics_content)
    assert len(events) == 10  # 10 instances of recurring event
```

### Database Tests
```python
def test_create_user():
    """Test creating a user"""
    user = create_user("user123")
    assert user.user_id == "user123"
    assert user.id is not None

def test_create_calendar():
    """Test creating a calendar"""
    user = create_user("user123")
    calendar = create_calendar(user.id, "https://example.com/calendar.ics")
    assert calendar.user_id == user.id
    assert calendar.url == "https://example.com/calendar.ics"

def test_create_event():
    """Test creating an event"""
    user = create_user("user123")
    calendar = create_calendar(user.id, "https://example.com/calendar.ics")
    event = create_event(
        calendar_id=calendar.id,
        uid="event123",
        title="Test Event",
        start_datetime=datetime(2023, 6, 15, 10, 0),
        end_datetime=datetime(2023, 6, 15, 11, 0)
    )
    assert event.title == "Test Event"
    assert event.uid == "event123"
```

### API Authentication Tests
```python
def test_valid_api_key_header(client):
    """Test API with valid key in header"""
    response = client.get("/events/pending", headers={"X-API-Key": "valid-key"})
    assert response.status_code == 200

def test_valid_api_key_query(client):
    """Test API with valid key in query parameter"""
    response = client.get("/events/pending?api_key=valid-key")
    assert response.status_code == 200

def test_invalid_api_key(client):
    """Test API with invalid key"""
    response = client.get("/events/pending", headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 401
```

### Scheduler Tests
```python
def test_notification_window_calculation():
    """Test notification window calculation"""
    event_time = datetime(2023, 6, 15, 10, 0)
    window = calculate_notification_window(event_time, minutes_before=10)
    assert window == datetime(2023, 6, 15, 9, 50)

def test_all_day_event_notification():
    """Test notification time for all-day events"""
    event_date = date(2023, 6, 15)
    notification_time = calculate_all_day_notification(event_date)
    assert notification_time.hour == 9  # Default notification time
```

## Integration Tests

### Synchronization Flow Tests
```python
def test_full_sync_flow():
    """Test complete synchronization flow"""
    # Setup
    mock_ics_content = load_fixture("valid_calendar.ics")
    mock_http_response(mock_ics_content)
    
    # Execute
    sync_calendars()
    
    # Verify
    events = get_all_events()
    assert len(events) == 5
    assert all(e.notified == False for e in events)

def test_incremental_sync():
    """Test incremental synchronization"""
    # Setup initial state
    initial_ics = load_fixture("calendar_v1.ics")
    mock_http_response(initial_ics)
    sync_calendars()
    
    # Update with new content
    updated_ics = load_fixture("calendar_v2.ics")
    mock_http_response(updated_ics)
    sync_calendars()
    
    # Verify
    events = get_all_events()
    assert len(events) == 6  # 5 original + 1 new
```

### API Endpoints Tests
```python
def test_get_pending_events(client):
    """Test getting pending events"""
    # Setup
    create_test_events()
    
    # Execute
    response = client.get("/events/pending", headers={"X-API-Key": "valid-key"})
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert len(data["events"]) == 3

def test_mark_notification_delivered(client):
    """Test marking notification as delivered"""
    # Setup
    event = create_test_event()
    
    # Execute
    response = client.post(
        f"/notifications/{event.id}/delivered",
        headers={"X-API-Key": "valid-key"},
        json={"delivered_at": "2023-06-15T09:30:00Z"}
    )
    
    # Verify
    assert response.status_code == 200
    updated_event = get_event(event.id)
    assert updated_event.notified == True
```

### Notification Flow Tests
```python
def test_complete_notification_flow():
    """Test complete notification flow from sync to delivery"""
    # Setup
    mock_ics_content = load_fixture("upcoming_events.ics")
    mock_http_response(mock_ics_content)
    
    # Execute sync
    sync_calendars()
    
    # Check pending notifications
    pending_events = get_pending_events()
    assert len(pending_events) == 2
    
    # Simulate client retrieving notifications
    # (This would be done via the API in a real test)
    
    # Mark as delivered
    for event in pending_events:
        mark_notification_delivered(event.id)
    
    # Verify
    delivered_events = get_notified_events()
    assert len(delivered_events) == 2
    assert all(e.notified == True for e in delivered_events)
```

## End-to-End Tests

### Docker Environment Tests
```python
def test_docker_deployment():
    """Test complete Docker deployment"""
    # This would be run against a deployed Docker container
    # 1. Start container with test configuration
    # 2. Verify health endpoint
    # 3. Add test calendar
    # 4. Trigger sync
    # 5. Check API endpoints
    # 6. Verify notifications
    pass
```

## Test Data

### Fixtures
- Sample ICS files with various event types
- Database fixtures for different scenarios
- Configuration files for testing

### Mock Data
- HTTP responses for calendar URLs
- Database states for different test scenarios
- Time-based scenarios using freezegun

## Test Execution

### Continuous Integration
- Run all tests on every commit
- Separate unit, integration, and end-to-end test stages
- Report coverage metrics
- Block deployment on test failures

### Test Commands
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run with coverage
pytest --cov=icsgate --cov-report=html

# Run specific test file
pytest tests/unit/test_ics_parser.py
```

## Performance Tests

### Load Testing
- Test API response times under load
- Test concurrent calendar synchronization
- Test database performance with large datasets

### Stress Testing
- Test behavior with very large ICS files
- Test memory usage with many calendars
- Test recovery from resource exhaustion

## Test Coverage Goals

### Minimum Coverage
- Unit tests: 80% coverage
- Integration tests: 70% coverage
- Critical paths: 100% coverage

### Coverage Measurement
- Line coverage
- Branch coverage
- Path coverage for critical functions

## Test Environment

### Development
- SQLite in-memory database
- Mocked HTTP requests
- Fast test execution

### CI/CD
- Isolated test databases
- Real HTTP mocking
- Parallel test execution

### Production-like
- Docker containers
- Real database instances
- Network isolation

## Test Data Management

### Data Isolation
- Separate test databases
- Transaction rollback for unit tests
- Fresh database for integration tests

### Data Generation
- Factory patterns for test data
- Faker library for realistic data
- Deterministic data for reproducible tests

## Monitoring Test Health

### Test Metrics
- Test execution time
- Failure rates
- Coverage trends
- Flaky test detection

### Test Reporting
- Detailed failure reports
- Performance metrics
- Coverage reports
- Trend analysis