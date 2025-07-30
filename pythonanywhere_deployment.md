# PythonAnywhere Deployment Guide

## After Git Pull

After pulling the latest changes from git, follow these steps:

### 1. Update PythonAnywhere Configuration

1. Go to your PythonAnywhere dashboard
2. Navigate to the "Web" tab
3. Click on your web app
4. Update the following settings:

**Source code:**
- Set to your repository directory (e.g., `/home/nishantb/ticket-verification-app`)

**Working directory:**
- Set to your repository directory (e.g., `/home/nishantb/ticket-verification-app`)

**WSGI configuration file:**
- **IMPORTANT**: Replace the current WSGI configuration with the new one
- Copy the contents of `pythonanywhere_wsgi.py` to your PythonAnywhere WSGI file
- Or use the updated `wsgi.py` file from the repository

### 2. Fix Package Installation Issues

In the PythonAnywhere bash console:

```bash
cd /home/nishantb/ticket-verification-app
```

**Option 1: Run the automated fix script**
```bash
python fix_pythonanywhere.py
```

**Option 2: Manual installation if the script fails**
```bash
# Install core packages first
pip install Flask==2.3.3
pip install Werkzeug==2.3.7
pip install Pillow==10.0.1
pip install openpyxl==3.1.2
pip install Jinja2==3.1.2
pip install MarkupSafe==2.1.3
pip install itsdangerous==2.1.2
pip install click==8.1.7
pip install blinker==1.6.3

# Install OCR packages (essential for receipt analysis)
pip install pytesseract==0.3.10
pip install pdf2image==1.16.3
```

**Option 3: If individual installation fails, try with --user flag**
```bash
pip install --user pytesseract==0.3.10
pip install --user pdf2image==1.16.3
```

### 3. Initialize Database

The database tables need to be created. Run this in the PythonAnywhere bash console:

```bash
cd /home/nishantb/ticket-verification-app
python -c "from backend.api import init_db; init_db()"
```

### 4. Create Required Directories

```bash
mkdir -p uploads csv_uploads logs
```

### 5. Update WSGI Configuration

**CRITICAL**: You need to update your PythonAnywhere WSGI configuration file. 

1. Go to your PythonAnywhere Web tab
2. Click on your web app
3. Click on the WSGI configuration file link
4. Replace the entire content with:

```python
import sys
import os

# Add the project directory to the Python path
path = '/home/nishantb/ticket-verification-app'
if path not in sys.path:
    sys.path.append(path)

# Enhanced debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Looking for backend/api.py in: {path}")
print(f"backend/api.py exists: {os.path.exists(os.path.join(path, 'backend', 'api.py'))}")

# Test flask_cors import before importing the app
try:
    import flask_cors
    print(f"✅ flask_cors is available at: {flask_cors.__file__}")
except ImportError as e:
    print(f"❌ flask_cors import failed: {e}")
    print(f"Available packages: {[pkg for pkg in sys.modules.keys() if 'flask' in pkg.lower()]}")

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
```