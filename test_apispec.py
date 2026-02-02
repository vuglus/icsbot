import os
import sys
import json

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import get_app
from services.api_endpoints import get_endpoints
from flask_smorest import Api

def test_apispec_generation():
    print("Testing OpenAPI spec generation with flask-smorest...")
    
    # Get the Flask app
    app = get_app()
    
    # Configure Flask-Smorest API
    app.config["API_TITLE"] = "ICS Bot API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/api"
    app.config["OPENAPI_REDOC_PATH"] = "/redoc"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # Initialize Flask-Smorest API
    api = Api(app)
    
    # Register all endpoints
    print("Registering endpoints...")
    blueprints = get_endpoints()
    
    # Register blueprints with the API
    for name, blueprint in blueprints.items():
        if hasattr(blueprint, 'name') and blueprint.name:
            api.register_blueprint(blueprint)
    
    print(f"Registered {len(blueprints)} blueprints with flask-smorest")
    
    # Check what's in the app's url map
    print("\nApp URL map:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    # Check what's in the app's view functions
    print(f"\nApp view functions: {len(app.view_functions)}")
    for endpoint, view_func in app.view_functions.items():
        print(f"  {endpoint} -> {view_func.__name__ if hasattr(view_func, '__name__') else view_func}")
    
    # Try to access the spec through the API object
    try:
        spec = api.spec.to_dict()
        print(f"\nOpenAPI spec generated successfully via api.spec!")
    except Exception as e:
        print(f"Could not access spec via api.spec: {e}")
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
    calendar_path = paths.get('/api/v1/calendar/calendars', {})
    
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