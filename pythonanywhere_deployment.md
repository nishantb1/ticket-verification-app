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
- The `wsgi.py` file has been updated to import from `backend/api.py` instead of `app.py`

### 2. Install Dependencies

In the PythonAnywhere bash console:

```bash
cd /home/nishantb/ticket-verification-app
```

**Option 1: Try the standard requirements file**
```bash
pip install -r requirements.txt
```

**Option 2: If Option 1 fails, use the PythonAnywhere-specific requirements**
```bash
pip install -r requirements-pythonanywhere.txt
```

**Option 3: Install packages individually if both fail**
```bash
pip install Flask==2.3.3
pip install Werkzeug==2.3.7
pip install Pillow==10.0.1
pip install openpyxl==3.1.2
pip install Jinja2==3.1.2
pip install MarkupSafe==2.1.3
pip install itsdangerous==2.1.2
pip install click==8.1.7
pip install blinker==1.6.3
```

**Note:** Some packages like `pytesseract` and `pdf2image` may not be available on PythonAnywhere's free tier. The app will work without them, but OCR functionality will be disabled.

### 3. Build Frontend (Optional)

If you want to serve the React frontend from PythonAnywhere:

```bash
cd frontend
npm install
npm run build
```

This will create a `build` folder that you can serve statically.

### 4. Database Migration

The database structure has been updated. The `tickets.db` file should work as-is, but if you encounter issues:

```bash
cd /home/nishantb/ticket-verification-app
python -c "from backend.api import init_db; init_db()"
```

### 5. Restart Web App

1. Go back to the "Web" tab in PythonAnywhere
2. Click "Reload" to restart your web app

### 6. Test the API

The Flask API endpoints should now be working. You can test them at:
- `https://yourusername.pythonanywhere.com/api/waves`
- `https://yourusername.pythonanywhere.com/api/orders`

### 7. Frontend Development

For local development of the React frontend:

```bash
cd frontend
npm start
```

This will run the React dev server on `http://localhost:3000` and proxy API calls to your PythonAnywhere backend.

### 8. Environment Variables

Make sure your `.env` file is properly configured with:
- Database path
- Upload folders
- Any API keys

### Troubleshooting

If you encounter issues:

1. **Pip Installation Errors:**
   - Try using `requirements-pythonanywhere.txt` instead of `requirements.txt`
   - Install packages individually if needed
   - Some packages may not be available on PythonAnywhere's free tier

2. **Import Errors:**
   - Check the PythonAnywhere error logs
   - Verify all dependencies are installed
   - Ensure the database file has proper permissions
   - Check that upload directories exist and are writable

3. **OCR/PDF Issues:**
   - `pytesseract` and `pdf2image` may not work on PythonAnywhere
   - The app will function without OCR, but receipt processing will be manual

4. **Database Issues:**
   - Make sure `tickets.db` has proper read/write permissions
   - Try running the database initialization script

### API Endpoints

The main API endpoints are:
- `/api/waves` - Wave management
- `/api/orders` - Order management  
- `/api/auth/*` - Authentication
- `/api/csv/*` - CSV upload and management
- `/api/analytics` - Analytics data
- `/api/receipts/*` - Receipt file serving

The old HTML templates have been removed as the app now uses React for the frontend. 