import os
import sys
import json

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import get_app
from services.api_endpoints.health_endpoint import register_health_endpoint
from services.api_endpoints.pending_events_endpoint import register_pending_events_endpoint
from services.api_endpoints.notification_endpoint import register_notification_endpoint
from services.api_endpoints.calendar_endpoint import register_calendar_endpoint
from services.api_endpoints.openapi_endpoint import register_openapi_endpoint
from flask_apispec import FlaskApiSpec
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

def test_apispec_generation():
    print("Testing OpenAPI spec generation...")
    
    # Get the Flask app
    app = get_app()
    
    # Initialize FlaskApiSpec
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='ICS-Gate API',
            version='1.0.0',
            openapi_version='3.0.0',
            plugins=[MarshmallowPlugin()],
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
    })
    
    docs = FlaskApiSpec(app)
    
    # Register all endpoints and collect view functions
    print("Registering endpoints...")
    view_functions = []
    
    # Register health endpoint
    health_funcs = register_health_endpoint(app) or []
    view_functions.extend(health_funcs)
    print(f"Registered health endpoint with {len(health_funcs)} functions")
    
    # Register pending events endpoint
    pending_funcs = register_pending_events_endpoint(app) or []
    view_functions.extend(pending_funcs)
    print(f"Registered pending events endpoint with {len(pending_funcs)} functions")
    
    # Register notification endpoint
    notification_funcs = register_notification_endpoint(app) or []
    view_functions.extend(notification_funcs)
    print(f"Registered notification endpoint with {len(notification_funcs)} functions")
    
    # Register calendar endpoint
    calendar_funcs = register_calendar_endpoint(app) or []
    view_functions.extend(calendar_funcs)
    print(f"Registered calendar endpoint with {len(calendar_funcs)} functions")
    
    # Register openapi endpoint (doesn't need to be registered with flask-apispec)
    register_openapi_endpoint(app)
    print("Registered openapi endpoint")
    
    print(f"Total view functions to register with flask-apispec: {len(view_functions)}")
    
    # Register view functions with flask-apispec
    registered_count = 0
    for view_func in view_functions:
        try:
            print(f"Registering {view_func.__name__} with flask-apispec")
            docs.register(view_func)
            registered_count += 1
        except Exception as e:
            print(f"Could not register {view_func.__name__} with FlaskApiSpec: {e}")
    
    print(f"Successfully registered {registered_count} functions with flask-apispec")
    
    # Check what's in the app's url map
    print("\nApp URL map:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    # Check what's in the app's view functions
    print(f"\nApp view functions: {len(app.view_functions)}")
    for endpoint, view_func in app.view_functions.items():
        print(f"  {endpoint} -> {view_func.__name__ if hasattr(view_func, '__name__') else view_func}")
    
    # Try to access the spec through the docs object
    try:
        spec = docs.spec.to_dict()
        print(f"\nOpenAPI spec generated successfully via docs.spec!")
    except Exception as e:
        print(f"Could not access spec via docs.spec: {e}")
        raise
    
    print(f"Spec title: {spec.get('info', {}).get('title', 'Unknown')}")
    print(f"Spec version: {spec.get('info', {}).get('version', 'Unknown')}")
    print(f"Number of paths: {len(spec.get('paths', {}))}")
    
    # Print detailed path information
    paths = spec.get('paths', {})
    for path, methods in paths.items():
        print(f"  Path: {path}")
        for method, details in methods.items():
            print(f"    Method: {method.upper()}")
            if 'parameters' in details:
                print(f"      Parameters: {details['parameters']}")
            if 'requestBody' in details:
                print(f"      Request Body: {details['requestBody']}")
    
    # Save the spec to a file
    with open('openapi_spec.json', 'w') as f:
        json.dump(spec, f, indent=2)
    print("\nOpenAPI spec saved to openapi_spec.json")
    
    # Print the calendar endpoints details
    calendar_path = paths.get('/calendars', {})
    
    # POST endpoint
    calendar_post = calendar_path.get('post', {})
    print(f"\nCalendar POST endpoint details:")
    print(f"  Summary: {calendar_post.get('summary', 'N/A')}")
    print(f"  Description: {calendar_post.get('description', 'N/A')}")
    print(f"  Parameters: {calendar_post.get('parameters', 'N/A')}")
    print(f"  Request Body: {calendar_post.get('requestBody', 'N/A')}")
    
    # GET endpoint
    calendar_get = calendar_path.get('get', {})
    print(f"\nCalendar GET endpoint details:")
    print(f"  Summary: {calendar_get.get('summary', 'N/A')}")
    print(f"  Description: {calendar_get.get('description', 'N/A')}")
    print(f"  Parameters: {calendar_get.get('parameters', 'N/A')}")
    
    return spec

if __name__ == "__main__":
    try:
        spec = test_apispec_generation()
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()