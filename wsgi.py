import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    # Import the Flask app from the backend structure
    from backend.api import app
    print("✅ Successfully imported app from backend/api.py")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Try alternative import
    try:
        import backend.api
        app = backend.api.app
        print("✅ Successfully imported app (alternative method)")
    except Exception as e2:
        print(f"❌ Alternative import also failed: {e2}")
        raise

# For PythonAnywhere and other WSGI servers
application = app

if __name__ == "__main__":
    app.run() 