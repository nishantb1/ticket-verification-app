import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Add the parent directory to access shared modules
parent_path = os.path.dirname(backend_path)
sys.path.insert(0, parent_path)

from api import app

if __name__ == "__main__":
    app.run() 