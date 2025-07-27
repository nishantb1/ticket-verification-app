import sys
import os

# Add the project directory to the Python path
path = '/home/nishantb/ticket-verification-app'
if path not in sys.path:
    sys.path.append(path)

# Debug: Print current path and check if app.py exists
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Looking for app.py in: {path}")
print(f"app.py exists: {os.path.exists(os.path.join(path, 'app.py'))}")

try:
    # Import the Flask app
    from app import app
    print("✅ Successfully imported app")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Try alternative import
    try:
        import app
        app = app.app
        print("✅ Successfully imported app (alternative method)")
    except Exception as e2:
        print(f"❌ Alternative import also failed: {e2}")
        raise

# For PythonAnywhere
application = app

if __name__ == "__main__":
    app.run() 