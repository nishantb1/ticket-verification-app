import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    # Import the Flask app from app.py
    from app import app
    print("✅ Successfully imported app from app.py")
except ImportError as e:
    print(f"❌ Import error: {e}")
    raise

# For PythonAnywhere and other WSGI servers
application = app

if __name__ == "__main__":
    app.run() 