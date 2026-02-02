import sys
print("Python path:")
for p in sys.path:
    print(f"  {p}")

try:
    import flask_smorest
    print("flask-smorest imported successfully")
except ImportError as e:
    print(f"Failed to import flask-smorest: {e}")

try:
    from app import app
    print("app imported successfully")
    print("Endpoints:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
except Exception as e:
    print(f"Failed to import app: {e}")
    import traceback
    traceback.print_exc()