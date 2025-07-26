import sys
import os

# Add the project directory to the Python path
path = '/home/yourusername/zelle_venmo_verifier'  # Change this to your PythonAnywhere username
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from app import app

# For PythonAnywhere
application = app

if __name__ == "__main__":
    app.run() 