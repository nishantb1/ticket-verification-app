# 🚀 Deployment Guide for ΔΕΨ Ticket Verifier

## 🐍 **PythonAnywhere (Recommended)**

### **Quick Setup:**
1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)
2. **Upload code** to `/home/yourusername/ticket-verification-app/`
3. **Install dependencies:**
   ```bash
   cd /home/yourusername/ticket-verification-app
   pip3 install -r requirements.txt
   ```
4. **Set up database:**
   ```bash
   python3 setup_complete.py
   ```
5. **Configure WSGI file** (replace `yourusername`):
   ```python
   import sys
   path = '/home/yourusername/ticket-verification-app'
   if path not in sys.path:
       sys.path.append(path)
   from app import app
   application = app
   ```
6. **Reload web app** in PythonAnywhere Web tab

**✅ Your app will be live at: `yourusername.pythonanywhere.com`**

---

## 🔒 **Post-Deployment Security**

1. **Change admin password** (default: `admin/admin123`)
2. **Set environment variables:**
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secure-secret-key`
3. **Configure wave settings** in admin dashboard

---

## 🆘 **Troubleshooting**

**Common Issues:**
- **Missing packages:** Run `pip3 install -r requirements.txt`
- **Import errors:** Check WSGI file path
- **Database issues:** Run `python3 setup_complete.py`

**For detailed deployment options (Heroku, Railway, Render), see the full guide in the repository.** 