import sys
import os

# Add the project directory to the Python path
path = '/home/nishantb/ticket-verification-app'
if path not in sys.path:
    sys.path.append(path)

# Debug: Print current path and check if backend/api.py exists
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Looking for backend/api.py in: {path}")
print(f"backend/api.py exists: {os.path.exists(os.path.join(path, 'backend', 'api.py'))}")

try:
    # Import the Flask app from the new backend structure
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

# For PythonAnywhere
application = app

if __name__ == "__main__":
    app.run() 