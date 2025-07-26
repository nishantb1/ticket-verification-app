import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pytesseract
from PIL import Image
import pdf2image
import uuid
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# For Heroku with PostgreSQL
if DATABASE_URL:
    import psycopg2
    from urllib.parse import urlparse
    
    def get_db_connection():
        result = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
else:
    # For SQLite (local development and PythonAnywhere)
    def get_db_connection():
        conn = sqlite3.connect('tickets.db')
        conn.row_factory = sqlite3.Row
        return conn

# ... existing code ... 