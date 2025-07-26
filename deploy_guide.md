# 🚀 Deployment Guide for ΔΕΨ Ticket Verifier

## 📋 Prerequisites
- Python 3.11+
- Git repository
- All dependencies installed (`pip install -r requirements.txt`)

---

## 🐍 **Option 1: PythonAnywhere (Recommended)**

### **Step 1: Create PythonAnywhere Account**
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for free account
3. Note your username

### **Step 2: Upload Your Code**
1. **Option A: Git Clone**
   ```bash
   git clone https://github.com/yourusername/zelle_venmo_verifier.git
   ```

2. **Option B: Upload Files**
   - Go to Files tab
   - Upload all project files
   - Create `uploads/` directory

### **Step 3: Set Up Virtual Environment**
```bash
# In PythonAnywhere bash console
cd zelle_venmo_verifier
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Step 4: Configure WSGI File**
1. Go to Web tab
2. Create new web app
3. Choose Manual configuration
4. Choose Python 3.11
5. Edit WSGI file:
   ```python
   import sys
   path = '/home/YOUR_USERNAME/zelle_venmo_verifier'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

### **Step 5: Set Up Database**
```bash
# In bash console
cd zelle_venmo_verifier
python setup_complete.py
```

### **Step 6: Configure Environment**
1. Go to Web tab → Environment variables
2. Add:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key`

### **Step 7: Reload Web App**
- Click "Reload" button in Web tab

**✅ Your app will be available at: `yourusername.pythonanywhere.com`**

---

## ☁️ **Option 2: Heroku**

### **Step 1: Install Heroku CLI**
```bash
# Download from heroku.com
heroku login
```

### **Step 2: Prepare for PostgreSQL**
```python
# Add to app.py (replace SQLite with PostgreSQL)
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
```

### **Step 3: Update Requirements**
```bash
# Add to requirements.txt
psycopg2-binary==2.9.7
gunicorn==21.2.0
```

### **Step 4: Deploy**
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Create Heroku app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main

# Run database setup
heroku run python setup_complete.py
```

**✅ Your app will be available at: `your-app-name.herokuapp.com`**

---

## 🚂 **Option 3: Railway**

### **Step 1: Connect GitHub**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub account
3. Select your repository

### **Step 2: Configure Environment**
1. Add environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key`

### **Step 3: Deploy**
1. Railway will automatically detect Flask app
2. Deploy from GitHub
3. Add PostgreSQL database

**✅ Railway will provide a URL automatically**

---

## 🔧 **Option 4: Render**

### **Step 1: Connect Repository**
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Choose "Web Service"

### **Step 2: Configure**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Environment:** Python 3.11

### **Step 3: Add Database**
1. Create PostgreSQL database
2. Add database URL to environment variables

**✅ Render will provide a URL automatically**

---

## 🛠️ **Post-Deployment Setup**

### **1. Update Admin Credentials**
```bash
# Access your deployed app
# Go to /admin/login
# Default: admin/admin123
# Change password immediately!
```

### **2. Configure Wave Settings**
1. Go to Admin Dashboard
2. Set up your wave pricing
3. Configure dates

### **3. Test File Uploads**
1. Submit a test order
2. Verify receipt upload works
3. Check OCR functionality

### **4. Set Up Custom Domain (Optional)**
- **PythonAnywhere:** Requires paid plan
- **Heroku:** Free with SSL
- **Railway/Render:** Usually free

---

## 🔒 **Security Checklist**

- ✅ Change default admin password
- ✅ Set strong SECRET_KEY
- ✅ Enable HTTPS (automatic on most platforms)
- ✅ Regular database backups
- ✅ Monitor application logs

---

## 📊 **Performance Tips**

### **For PythonAnywhere:**
- Use static file serving for uploads
- Optimize database queries
- Monitor bandwidth usage

### **For Heroku:**
- Use connection pooling
- Optimize for cold starts
- Monitor dyno usage

### **For All Platforms:**
- Compress images before upload
- Use efficient database queries
- Monitor error logs

---

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **Import Errors**
   - Check Python version compatibility
   - Verify all dependencies installed

2. **Database Issues**
   - Ensure database file is writable
   - Check file permissions

3. **File Upload Issues**
   - Verify uploads/ directory exists
   - Check file size limits

4. **OCR Issues**
   - Ensure tesseract is installed
   - Check image quality

### **Getting Help:**
- Check platform-specific documentation
- Review application logs
- Test locally first

---

## 🎯 **Quick Start Recommendation**

**For immediate deployment, use PythonAnywhere:**

1. Sign up at pythonanywhere.com
2. Upload your code
3. Follow the PythonAnywhere steps above
4. Your app will be live in 15 minutes!

**For production use, consider Heroku or Railway for better performance and features.** 