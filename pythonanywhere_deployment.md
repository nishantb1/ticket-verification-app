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
pip install -r requirements.txt
```

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

1. Check the PythonAnywhere error logs
2. Verify all dependencies are installed
3. Ensure the database file has proper permissions
4. Check that upload directories exist and are writable

### API Endpoints

The main API endpoints are:
- `/api/waves` - Wave management
- `/api/orders` - Order management  
- `/api/auth/*` - Authentication
- `/api/csv/*` - CSV upload and management
- `/api/analytics` - Analytics data
- `/api/receipts/*` - Receipt file serving

The old HTML templates have been removed as the app now uses React for the frontend. 