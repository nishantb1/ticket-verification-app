#!/usr/bin/env python3
"""
PythonAnywhere Deployment Fix Script

This script helps fix common issues when deploying the updated app to PythonAnywhere.
Run this in your PythonAnywhere bash console after pulling the latest changes.
"""

import os
import sys
import sqlite3
import subprocess

def check_and_create_directories():
    """Ensure required directories exist"""
    directories = ['uploads', 'csv_uploads', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def init_database():
    """Initialize the database with required tables"""
    try:
        from backend.api import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    return True

def check_packages():
    """Check if required packages are installed"""
    required_packages = [
        'Flask', 'Werkzeug', 'Pillow', 'pytesseract', 
        'pdf2image', 'openpyxl', 'Jinja2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    return missing_packages

def install_missing_packages(missing_packages):
    """Install missing packages"""
    if not missing_packages:
        print("✅ All required packages are installed")
        return True
    
    print(f"Installing missing packages: {', '.join(missing_packages)}")
    
    # Try installing packages individually
    for package in missing_packages:
        try:
            if package == 'pytesseract':
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytesseract==0.3.10'], check=True)
            elif package == 'pdf2image':
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pdf2image==1.16.3'], check=True)
            else:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def test_imports():
    """Test if the app can be imported correctly"""
    try:
        from backend.api import app
        print("✅ App imports successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    """Main deployment fix function"""
    print("🔧 PythonAnywhere Deployment Fix Script")
    print("=" * 50)
    
    # Check and create directories
    print("\n1. Checking directories...")
    check_and_create_directories()
    
    # Check packages
    print("\n2. Checking required packages...")
    missing_packages = check_packages()
    
    # Install missing packages
    if missing_packages:
        print("\n3. Installing missing packages...")
        if not install_missing_packages(missing_packages):
            print("❌ Failed to install some packages")
            return False
    
    # Initialize database
    print("\n4. Initializing database...")
    if not init_database():
        print("❌ Database initialization failed")
        return False
    
    # Test imports
    print("\n5. Testing app imports...")
    if not test_imports():
        print("❌ App import test failed")
        return False
    
    print("\n✅ Deployment fix completed successfully!")
    print("\nNext steps:")
    print("1. Go to your PythonAnywhere Web tab")
    print("2. Update the WSGI configuration file to use the new backend structure")
    print("3. Reload your web app")
    print("4. Test the API endpoints")
    
    return True

if __name__ == "__main__":
    main() 