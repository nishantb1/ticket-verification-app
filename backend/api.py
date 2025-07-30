import os
import uuid
import sqlite3
import re
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import pytesseract
from PIL import Image
import pdf2image
import csv
import io
import tempfile
from functools import wraps
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from logging_config import setup_logging, get_logger, log_order_submission, log_ocr_processing, log_csv_upload, log_admin_action, log_error, log_performance

# Setup logging
setup_logging()
logger = get_logger('api')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app, origins=['http://localhost:3000', 'https://yourdomain.com'], supports_credentials=True)

# Configuration
UPLOAD_FOLDER = 'uploads'
CSV_UPLOAD_FOLDER = 'csv_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_UPLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)

def get_db_path():
    """Get the absolute path to the database file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tickets.db')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    """Initialize database with all tables"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            boys_price REAL DEFAULT 14.0,
            girls_price REAL DEFAULT 14.0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            boys_count INTEGER DEFAULT 0,
            girls_count INTEGER DEFAULT 0,
            expected_amount REAL NOT NULL,
            receipt_filename TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            wave_id INTEGER,
            FOREIGN KEY (wave_id) REFERENCES wave (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venmo_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            type TEXT,
            note TEXT,
            from_user TEXT,
            to_user TEXT,
            amount REAL,
            fee REAL,
            net_amount REAL,
            csv_filename TEXT,
            csv_upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zelle_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT,
            amount REAL,
            type TEXT,
            balance REAL,
            payer_identifier TEXT,
            csv_filename TEXT,
            csv_upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            admin_user TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS csv_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_size INTEGER,
            upload_type TEXT NOT NULL,
            records_processed INTEGER,
            new_records INTEGER,
            updated_records INTEGER,
            admin_user TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM admin_users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO admin_users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', ('admin', generate_password_hash('admin123'), 'admin'))
    
        conn.commit()
        conn.close()
        
# Initialize database
init_db()

# OCR Functions
def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    start_time = time.time()
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        
        duration = time.time() - start_time
        log_performance(logger, "OCR Image Processing", duration, f"File: {os.path.basename(image_path)}")
        
        return text
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, f"OCR failed for image: {image_path}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using OCR"""
    start_time = time.time()
    try:
        images = pdf2image.convert_from_path(pdf_path)
        text = ""
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
            logger.debug(f"PDF OCR - Page {i+1}: {len(page_text)} characters")
        
        duration = time.time() - start_time
        log_performance(logger, "OCR PDF Processing", duration, f"File: {os.path.basename(pdf_path)}, Pages: {len(images)}")
        
        return text
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, f"PDF OCR failed for file: {pdf_path}")
        return ""

def parse_ocr_data(text):
    """Parse OCR text to extract amount, date, and payer name"""
    lines = text.split('\n')
    amount = None
    date = None
    name = None
    
    # Debug: Log the raw OCR text
    logger.debug(f"OCR Raw text length: {len(text)}")
    logger.debug(f"OCR Raw text (first 200 chars): {text[:200]}...")
    
    # Common patterns for Venmo/Zelle receipts
    for line in lines:
        line = line.strip()
        
        # Look for amount patterns - enhanced for Venmo
        if '$' in line:
            try:
                amount_match = re.search(r'[\-\+]?\s*\$?\s*(\d+\.?\d*)', line)
                if amount_match:
                    amount = float(amount_match.group(1))
                    logger.debug(f"OCR Debug - Found amount: {amount} in line: {line}")
            except:
                pass
        
        # Look for date patterns - enhanced for Venmo format
        date_patterns = [
            r'(\w+ \d{1,2}, \d{4})',  # January 28, 2025
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 01/28/2025
            r'(\d{4}-\d{2}-\d{2})',  # 2025-01-28
            r'(\w+ \d{1,2}, \d{4}, \d{1,2}:\d{2} [AP]M)',  # January 28, 2025, 7:16 PM
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, line)
            if date_match:
                try:
                    date_str = date_match.group(1)
                    for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d', '%B %d, %Y, %I:%M %p']:
                        try:
                            if fmt == '%B %d, %Y, %I:%M %p':
                                date = datetime.strptime(date_str, fmt).date()
                            else:
                                date = datetime.strptime(date_str, fmt).date()
                            logger.debug(f"OCR Debug - Found date: {date} in line: {line}")
                            break
                        except:
                            continue
                    if date:
                        break
                except:
                    pass
        
        # Look for payer name patterns - enhanced for Venmo
        if not name and len(line) > 2 and len(line) < 100:
            if '@' in line and '.' in line:
                email_name = line.split('@')[0]
                if '.' in email_name:
                    name_parts = email_name.split('.')
                    name = ' '.join(part.capitalize() for part in name_parts)
                else:
                    name = email_name.capitalize()
                logger.debug(f"OCR Debug - Found name from email: {name} in line: {line}")
            elif ' ' in line and not any(char.isdigit() for char in line):
                skip_words = ['complete', 'status', 'payment', 'transaction', 'details', 'depsi', 'utd', 'beta', 'chapter']
                if not any(word in line.lower() for word in skip_words):
                    name = line
                    logger.debug(f"OCR Debug - Found name: {name} in line: {line}")
    
    # Fallback name search
    if not name:
        for line in lines:
            line = line.strip()
            if (len(line) > 3 and len(line) < 50 and
                ' ' in line and
                not any(char.isdigit() for char in line) and
                not line.lower() in ['complete', 'status', 'payment', 'transaction', 'details', 'depsi', 'utd']):
                name = line
                logger.debug(f"OCR Debug - Found name (fallback): {name} in line: {line}")
                break
    
    result = {
        'amount': amount,
        'date': date,
        'name': name
    }
    logger.debug(f"OCR Debug - Final parsed data: {result}")
    return result

# API Routes

@app.route('/api/auth/validate', methods=['GET'])
def api_validate_session():
    """API endpoint to validate if user session is still active"""
    if session.get('admin_logged_in'):
        return jsonify({'success': True, 'authenticated': True});
    else:
        return jsonify({'success': True, 'authenticated': False});

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for admin login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash, role FROM admin_users WHERE username = ? AND is_active = 1', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[2], password):
        session['admin_logged_in'] = True
        session['admin_username'] = user[1]
        session['admin_role'] = user[3]
        
        log_admin_action(logger, 'login', f"Admin login: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'admin_user': {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for admin logout"""
    username = session.get('admin_username', 'Unknown')
    session.clear()
    log_admin_action(logger, 'logout', f"Admin logout: {username}")
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/change-password', methods=['POST'])
@login_required
def api_change_password():
    """API endpoint for changing admin password"""
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'Old and new password required'}), 400
    
    username = session.get('admin_username')
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM admin_users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user[0], old_password):
        new_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE admin_users SET password_hash = ? WHERE username = ?', (new_hash, username))
        conn.commit()
        conn.close()
        
        log_admin_action(logger, 'password_change', f"Password changed for: {username}")
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid old password'}), 400

@app.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    """API endpoint to get all orders with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status')
    wave_id = request.args.get('wave_id', type=int)
    search = request.args.get('search')
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Build query with filters
    query = '''
        SELECT o.*, w.name as wave_name 
        FROM order_table o 
        LEFT JOIN wave w ON o.wave_id = w.id 
        WHERE 1=1
    '''
    params = []
    
    if status:
        query += ' AND o.status = ?'
        params.append(status)
    
    if wave_id:
        query += ' AND o.wave_id = ?'
        params.append(wave_id)
    
    if search:
        query += ' AND (o.name LIKE ? OR o.email LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term])
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM ({query})"
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # Get paginated results
    query += ' ORDER BY o.created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    orders = []
    for row in cursor.fetchall():
        orders.append({
            'id': row[0],
            'uuid': row[1],
            'name': row[2],
            'email': row[3],
            'referral': row[4],
            'boys_count': row[5],
            'girls_count': row[6],
            'wave_id': row[7],
            'expected_amount': row[8],
            'ocr_amount': row[9],
            'ocr_date': row[10],
            'ocr_name': row[11],
            'status': row[12],
            'receipt_path': row[13],
            'created_at': row[14],
            'notes': row[15],
            'phone': row[16],
            'wave_name': row[17]
        })
    
    conn.close()
    
    return jsonify({
        'data': orders,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/orders', methods=['POST'])
def api_create_order():
    """API endpoint to create a new order"""
    try:
        print("=== ORDER CREATION DEBUG ===")
        print(f"Form data: {request.form}")
        print(f"Files: {request.files}")
        
        name = request.form.get('name')
        email = request.form.get('email')
        # phone = request.form.get('phone', '')  # Remove phone since it's not in schema
        boys_tickets = int(request.form.get('boys_tickets', 0))
        girls_tickets = int(request.form.get('girls_tickets', 0))
        
        print(f"Parsed data - name: {name}, email: {email}")
        print(f"Tickets - boys: {boys_tickets}, girls: {girls_tickets}")
        
        if not all([name, email]):  # Remove phone from required fields
            print("Validation failed: missing name or email")
            return jsonify({'success': False, 'message': 'Name and email are required'}), 400
        
        if boys_tickets < 0 or girls_tickets < 0:
            print("Validation failed: negative ticket counts")
            return jsonify({'success': False, 'message': 'Ticket counts must be non-negative'}), 400
        
        if boys_tickets == 0 and girls_tickets == 0:
            print("Validation failed: no tickets selected")
            return jsonify({'success': False, 'message': 'At least one ticket must be selected'}), 400
        
        # Get current wave
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT id, boys_price, girls_price FROM wave WHERE is_active = 1 AND start_date <= date("now") AND end_date >= date("now")')
        current_wave = cursor.fetchone()
        wave_id = current_wave[0] if current_wave else None
        boys_price = current_wave[1] if current_wave else 14.0
        girls_price = current_wave[2] if current_wave else 14.0
        
        print(f"Current wave - ID: {wave_id}, boys_price: {boys_price}, girls_price: {girls_price}")
        
        # Calculate total amount using wave prices
        total_amount = (boys_tickets * boys_price) + (girls_tickets * girls_price)
        print(f"Total amount: {total_amount}")
        
        # Handle file upload
        receipt_filename = None
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                receipt_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, receipt_filename)
                file.save(file_path)
                print(f"File saved: {receipt_filename}")
                
                # Process OCR
                start_time = time.time()
                if filename.lower().endswith('.pdf'):
                    ocr_text = extract_text_from_pdf(file_path)
                else:
                    ocr_text = extract_text_from_image(file_path)
                
                ocr_data = parse_ocr_data(ocr_text)
                log_ocr_processing(logger, receipt_filename, ocr_data, time.time() - start_time)
        else:
            print("No receipt file provided")
        
        # Generate UUID for the order
        order_uuid = str(uuid.uuid4())
        
        # Insert order
        cursor.execute('''
            INSERT INTO order_table (uuid, name, email, boys_count, girls_count, expected_amount, receipt_path, wave_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_uuid, name, email, boys_tickets, girls_tickets, total_amount, receipt_filename, wave_id))
        
        order_id = cursor.lastrowid
        conn.commit()
        
        print(f"Order created with ID: {order_id}")
        
        # Try to match transaction
        if receipt_filename:
            match_result = match_transaction(order_id)
            if match_result['matched']:
                # Update order status to Verified if match found
                cursor.execute('UPDATE order_table SET status = ? WHERE id = ?', ('Verified', order_id))
                print("Transaction matched, order marked as completed")
        
        conn.close()
        
        # Log the order submission
        order_data = {
            'uuid': order_uuid,
            'name': name,
            'email': email,
            'boys_count': boys_tickets,
            'girls_count': girls_tickets,
            'expected_amount': total_amount,
            'receipt_filename': receipt_filename,
            'wave_id': wave_id
        }
        log_order_submission(logger, order_data)
        
        print("Order creation successful")
        return jsonify({
            'success': True, 
            'message': 'Order submitted successfully!',
            'order': {
                'id': order_id,
                'name': name,
                'email': email,
                'boys_tickets': boys_tickets,
                'girls_tickets': girls_tickets,
                'total_amount': total_amount,
                'receipt_filename': receipt_filename,
                'status': 'Pending'
            }
        })
        
    except Exception as e:
        print(f"Order creation error: {str(e)}")
        log_error(logger, e, "Order creation failed")
        return jsonify({'success': False, 'message': 'Error creating order'}), 500

@app.route('/api/orders/<int:order_id>/approve', methods=['POST'])
@login_required
def api_approve_order(order_id):
    """API endpoint to approve an order"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('UPDATE order_table SET status = ? WHERE id = ?', ('Verified', order_id))
        conn.commit()
        conn.close()
        
        log_admin_action(logger, 'approve_order', f"Order {order_id} approved by {session.get('admin_username')}")
        return jsonify({'success': True, 'message': 'Order approved successfully'})
    except Exception as e:
        log_error(logger, e, f"Failed to approve order {order_id}")
        return jsonify({'success': False, 'message': 'Error approving order'}), 500

@app.route('/api/orders/<int:order_id>/reject', methods=['POST'])
@login_required
def api_reject_order(order_id):
    """API endpoint to reject an order"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('UPDATE order_table SET status = ? WHERE id = ?', ('Rejected', order_id))
        conn.commit()
        conn.close()
        
        log_admin_action(logger, 'reject_order', f"Order {order_id} rejected by {session.get('admin_username')}")
        return jsonify({'success': True, 'message': 'Order rejected successfully'})
    except Exception as e:
        log_error(logger, e, f"Failed to reject order {order_id}")
        return jsonify({'success': False, 'message': 'Error rejecting order'}), 500

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
@login_required
def api_delete_order(order_id):
    """API endpoint to delete an order"""
    print(f"=== DELETE ORDER DEBUG ===")
    print(f"Order ID to delete: {order_id}")
    print(f"Admin user: {session.get('admin_username')}")
    
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Check if order exists first
        cursor.execute('SELECT id, name, email FROM order_table WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            print(f"Order {order_id} not found")
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        print(f"Found order: {order}")
        
        # Delete the order
        cursor.execute('DELETE FROM order_table WHERE id = ?', (order_id,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Deleted {deleted_rows} rows")
        
        log_admin_action(logger, 'delete_order', f"Order {order_id} deleted by {session.get('admin_username')}")
        return jsonify({'success': True, 'message': 'Order deleted successfully'})
    except Exception as e:
        print(f"Error deleting order: {str(e)}")
        log_error(logger, e, f"Failed to delete order {order_id}")
        return jsonify({'success': False, 'message': 'Error deleting order'}), 500

@app.route('/api/orders/verified-emails', methods=['GET'])
@login_required
def api_get_verified_emails():
    """Get all verified email addresses for Ticketbud export"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, name, expected_amount, created_at
            FROM order_table 
            WHERE status = 'Verified'
            ORDER BY created_at DESC
        ''')
        
        verified_orders = cursor.fetchall()
        conn.close()
        
        # Format emails for easy copying
        emails = [order[0] for order in verified_orders]
        email_list = '\n'.join(emails)
        
        return jsonify({
            'success': True,
            'emails': emails,
            'email_list': email_list,
            'count': len(emails),
            'orders': [
                {
                    'email': order[0],
                    'name': order[1],
                    'amount': order[2],
                    'created_at': order[3]
                }
                for order in verified_orders
            ]
        })
        
    except Exception as e:
        log_error(logger, e, "Error getting verified emails")
        return jsonify({'success': False, 'message': 'Error getting verified emails'}), 500

@app.route('/api/waves', methods=['GET'])
@login_required
def api_get_waves():
    """API endpoint to get all waves"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wave ORDER BY created_at DESC')
    waves = []
    for row in cursor.fetchall():
        waves.append({
            'id': row[0],
            'name': row[1],
            'start_date': row[2],
            'end_date': row[3],
            'boys_price': row[4],
            'girls_price': row[5],
            'is_active': bool(row[6]),
            'created_at': row[7]
        })
    conn.close()
    return jsonify(waves)

@app.route('/api/waves/current', methods=['GET'])
def api_get_current_wave():
    """API endpoint to get the current active wave"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, start_date, end_date, boys_price, girls_price, is_active, created_at 
        FROM wave 
        WHERE is_active = 1 
        ORDER BY created_at DESC 
        LIMIT 1
    ''')
    wave = cursor.fetchone()
    conn.close()
    
    if wave:
        return jsonify({
            'id': wave[0],
            'name': wave[1],
            'start_date': wave[2],
            'end_date': wave[3],
            'boys_price': wave[4],
            'girls_price': wave[5],
            'is_active': bool(wave[6]),
            'created_at': wave[7]
        })
    else:
        return jsonify(None)

@app.route('/api/waves', methods=['POST'])
@login_required
def api_create_wave():
    data = request.get_json()
    name = data.get('name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    boys_price = float(data.get('boys_price', 14.0))
    girls_price = float(data.get('girls_price', 14.0))
    
    if not name or not start_date or not end_date:
        return jsonify({'success': False, 'message': 'Name, start date, and end date are required'}), 400
    
    if boys_price < 0 or girls_price < 0:
        return jsonify({'success': False, 'message': 'Prices must be non-negative'}), 400
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
        
    try:
        cursor.execute('''
            INSERT INTO wave (name, start_date, end_date, boys_price, girls_price, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        ''', (name, start_date, end_date, boys_price, girls_price))
        conn.commit()
        wave_id = cursor.lastrowid
        
        log_admin_action(logger, 'create_wave', f"Wave '{name}' created by {session.get('admin_username')}")
        
        return jsonify({
            'success': True,
            'message': 'Wave created successfully',
            'data': {
                'id': wave_id,
            'name': name,
                'start_date': start_date,
                'end_date': end_date,
                'boys_price': boys_price,
                'girls_price': girls_price,
                'is_active': True
            }
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error creating wave: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/waves/<int:wave_id>', methods=['PUT'])
@login_required
def api_update_wave(wave_id):
    """API endpoint to update a wave"""
    data = request.get_json()
    print(f"Update wave request for wave_id: {wave_id}")
    print(f"Received data: {data}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Get current wave data first
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    try:
        # Get current wave data
        cursor.execute('SELECT * FROM wave WHERE id = ?', (wave_id,))
        current_wave = cursor.fetchone()
        if not current_wave:
            return jsonify({'success': False, 'message': 'Wave not found'}), 404
        
        print(f"Current wave: {current_wave}")
        
        # Update only the fields that are provided
        name = data.get('name', current_wave[1])
        start_date = data.get('start_date', current_wave[2])
        end_date = data.get('end_date', current_wave[3])
        boys_price = float(data.get('boys_price', current_wave[4]))
        girls_price = float(data.get('girls_price', current_wave[5]))
        is_active = data.get('is_active', current_wave[6])
        
        print(f"Parsed data - name: {name}, start_date: {start_date}, end_date: {end_date}")
        print(f"boys_price: {boys_price}, girls_price: {girls_price}, is_active: {is_active}")
        print(f"is_active type: {type(is_active)}")
        
        # Only validate required fields if they are being updated
        if 'name' in data and not name:
            return jsonify({'success': False, 'message': 'Name is required'}), 400
        if 'start_date' in data and not start_date:
            return jsonify({'success': False, 'message': 'Start date is required'}), 400
        if 'end_date' in data and not end_date:
            return jsonify({'success': False, 'message': 'End date is required'}), 400
        
        if boys_price < 0 or girls_price < 0:
            return jsonify({'success': False, 'message': 'Prices must be non-negative'}), 400
        
        cursor.execute('''
            UPDATE wave 
            SET name = ?, start_date = ?, end_date = ?, boys_price = ?, girls_price = ?, is_active = ?
            WHERE id = ?
        ''', (name, start_date, end_date, boys_price, girls_price, is_active, wave_id))
        
        print(f"Rows affected: {cursor.rowcount}")
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Wave not found'}), 404
        
        conn.commit()
        
        # Verify the update
        cursor.execute('SELECT * FROM wave WHERE id = ?', (wave_id,))
        updated_wave = cursor.fetchone()
        print(f"Updated wave: {updated_wave}")
        
        log_admin_action(logger, 'update_wave', f"Wave {wave_id} updated by {session.get('admin_username')}")
        
        return jsonify({
            'success': True,
            'message': 'Wave updated successfully',
            'data': {
                'id': wave_id,
                'name': name,
                'start_date': start_date,
                'end_date': end_date,
                'boys_price': boys_price,
                'girls_price': girls_price,
                'is_active': is_active
            }
        })
    except Exception as e:
        conn.rollback()
        print(f"Error updating wave: {str(e)}")
        return jsonify({'success': False, 'message': f'Error updating wave: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/waves/<int:wave_id>', methods=['DELETE'])
@login_required
def api_delete_wave(wave_id):
    """API endpoint to delete a wave"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    try:
        # Check if wave exists
        cursor.execute('SELECT name FROM wave WHERE id = ?', (wave_id,))
        wave = cursor.fetchone()
        
        if not wave:
            return jsonify({'success': False, 'message': 'Wave not found'}), 404
        
        # Check if wave has associated orders
        cursor.execute('SELECT COUNT(*) FROM order_table WHERE wave_id = ?', (wave_id,))
        order_count = cursor.fetchone()[0]
        
        if order_count > 0:
            return jsonify({'success': False, 'message': f'Cannot delete wave: {order_count} orders are associated with this wave'}), 400
        
        cursor.execute('DELETE FROM wave WHERE id = ?', (wave_id,))
        conn.commit()
        
        log_admin_action(logger, 'delete_wave', f"Wave {wave_id} deleted by {session.get('admin_username')}")
        
        return jsonify({'success': True, 'message': 'Wave deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error deleting wave: {str(e)}'}), 500
    finally:
        conn.close()
    
@app.route('/api/analytics', methods=['GET'])
@login_required
def api_get_analytics():
    """API endpoint to get analytics data"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Get basic stats
    cursor.execute('SELECT COUNT(*) FROM order_table')
    total_orders = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM order_table WHERE status = ?', ('Pending',))
    pending_orders = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM order_table WHERE status = ?', ('Verified',))
    approved_orders = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM order_table WHERE status = ?', ('Rejected',))
    rejected_orders = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(expected_amount) FROM order_table WHERE status = ?', ('Verified',))
    total_revenue = cursor.fetchone()[0] or 0
    
    # Get transaction counts
    cursor.execute('SELECT COUNT(*) FROM venmo_transactions')
    venmo_transactions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM zelle_transactions')
    zelle_transactions = cursor.fetchone()[0]
    
    # Get orders by status
    cursor.execute('''
        SELECT status, COUNT(*) 
        FROM order_table 
        GROUP BY status
    ''')
    orders_by_status = dict(cursor.fetchall())
    
    # Get orders by wave
    cursor.execute('''
        SELECT w.name, COUNT(*) 
        FROM order_table o 
        LEFT JOIN wave w ON o.wave_id = w.id 
        GROUP BY o.wave_id, w.name
    ''')
    orders_by_wave = dict(cursor.fetchall())
    
    # Get recent orders
    cursor.execute('''
        SELECT o.*, w.name as wave_name 
        FROM order_table o 
        LEFT JOIN wave w ON o.wave_id = w.id 
        ORDER BY o.created_at DESC 
        LIMIT 10
    ''')
    recent_orders = []
    for row in cursor.fetchall():
        recent_orders.append({
            'id': row[0],
            'uuid': row[1],
            'name': row[2],
            'email': row[3],
            'referral': row[4],
            'boys_count': row[5],
            'girls_count': row[6],
            'wave_id': row[7],
            'expected_amount': row[8],
            'ocr_amount': row[9],
            'ocr_date': row[10],
            'ocr_name': row[11],
            'status': row[12],
            'receipt_path': row[13],
            'created_at': row[14],
            'notes': row[15],
            'phone': row[16],
            'wave_name': row[17]
        })
    
    conn.close()
    
    return jsonify({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'approved_orders': approved_orders,
        'rejected_orders': rejected_orders,
        'total_revenue': total_revenue,
        'venmo_transactions': venmo_transactions,
        'zelle_transactions': zelle_transactions,
        'orders_by_status': orders_by_status,
        'orders_by_wave': orders_by_wave,
        'recent_orders': recent_orders
    })

@app.route('/api/csv/upload', methods=['POST'])
@login_required
def api_upload_csv():
    """API endpoint to upload CSV files"""
    if 'csv_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    try:
        # Ensure csv_uploads directory exists
        csv_uploads_dir = 'csv_uploads'
        os.makedirs(csv_uploads_dir, exist_ok=True)
        
        # Generate unique filename for storage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = secure_filename(file.filename)
        stored_filename = f"{timestamp}_{original_filename}"
        file_path = os.path.join(csv_uploads_dir, stored_filename)
        
        # Save the CSV file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Read CSV content for parsing
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Detect CSV format
        format_type = detect_csv_format(csv_content)
        logger.info(f"CSV format detected: {format_type} for file: {original_filename}")
        
        # Parse CSV based on format
        if format_type == 'venmo':
            transactions = parse_venmo_csv(csv_content)
            upload_type = 'venmo'
        elif format_type == 'chase':
            transactions = parse_chase_csv(csv_content)
            upload_type = 'zelle'
        else:
            # Try both parsers
            venmo_transactions = parse_venmo_csv(csv_content)
            chase_transactions = parse_chase_csv(csv_content)
            
            if len(venmo_transactions) > len(chase_transactions):
                transactions = venmo_transactions
                upload_type = 'venmo'
            else:
                transactions = chase_transactions
                upload_type = 'zelle'
        
        if not transactions:
            logger.warning(f"No valid transactions found in CSV file: {original_filename}")
            return jsonify({'success': False, 'message': 'No valid transactions found in CSV. Please check the file format.'}), 400
        
        # Connect to database
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        new_records = 0
        updated_records = 0
        
        # Process transactions based on type
        if upload_type == 'venmo':
            for transaction in transactions:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO venmo_transactions 
                        (datetime, type, note, from_user, to_user, amount, fee, net_amount, csv_filename, csv_upload_date, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        transaction['datetime'],
                        transaction['type'],
                        transaction['note'],
                        transaction['from_user'],
                        transaction['to_user'],
                        transaction['amount'],
                        transaction['fee'],
                        transaction['net_amount'],
                        stored_filename,
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    if cursor.rowcount > 0:
                        new_records += 1
                    else:
                        updated_records += 1
                        
                except Exception as e:
                    print(f"Error inserting Venmo transaction: {e}")
                    continue
                    
        else:  # zelle
            for transaction in transactions:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO zelle_transactions 
                        (date, description, amount, type, balance, payer_identifier, csv_filename, csv_upload_date, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        transaction['date'],
                        transaction['description'],
                        transaction['amount'],
                        transaction['type'],
                        transaction['balance'],
                        transaction['payer_identifier'],
                        stored_filename,
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    if cursor.rowcount > 0:
                        new_records += 1
                    else:
                        updated_records += 1
                        
                except Exception as e:
                    print(f"Error inserting Zelle transaction: {e}")
                    continue
        
        # Record upload in csv_uploads table
        cursor.execute('''
            INSERT INTO csv_uploads 
            (filename, original_filename, file_size, upload_type, records_processed, new_records, updated_records, admin_user)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stored_filename,
            original_filename,
            file_size,
            upload_type,
            len(transactions),
            new_records,
            updated_records,
            session.get('admin_username', 'Unknown')
        ))
        
        conn.commit()
        conn.close()
        
        # Log the upload action
        log_csv_upload(logger, original_filename, upload_type, len(transactions), new_records, updated_records)
        log_admin_action(logger, 'csv_upload', 
                        f'Uploaded {upload_type} CSV: {original_filename}, '
                        f'Processed {len(transactions)} transactions, '
                        f'New: {new_records}, Updated: {updated_records}')
        
        return jsonify({
            'success': True,
            'message': f'Successfully uploaded {upload_type} CSV: {original_filename}. '
                      f'Processed {len(transactions)} transactions (New: {new_records}, Updated: {updated_records}).',
            'data': {
                'filename': stored_filename,
                'original_filename': original_filename,
                'upload_type': upload_type,
                'records_processed': len(transactions),
                'new_records': new_records,
                'updated_records': updated_records
            }
        })
        
    except Exception as e:
        log_error(logger, e, f"CSV upload failed for file: {original_filename}")
        return jsonify({'success': False, 'message': f'Error uploading CSV: {str(e)}'}), 500
    
@app.route('/api/csv/uploads', methods=['GET'])
@login_required
def api_get_csv_uploads():
    """API endpoint to get CSV upload history"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, original_filename, file_size, upload_date, upload_type, 
                   records_processed, new_records, updated_records, admin_user, status
            FROM csv_uploads 
            ORDER BY upload_date DESC
        ''')
        
        uploads = []
        for row in cursor.fetchall():
            uploads.append({
                'id': row[0],
                'filename': row[1],
                'original_filename': row[2],
                'file_size': row[3],
                'upload_date': row[4],
                'upload_type': row[5],
                'records_processed': row[6],
                'new_records': row[7],
                'updated_records': row[8],
                'admin_user': row[9],
                'status': row[10]
            })
        
        conn.close()
        return jsonify(uploads)
        
    except Exception as e:
        log_error(logger, e, "Failed to get CSV uploads")
        return jsonify({'success': False, 'message': 'Error getting CSV uploads'}), 500

# Helper functions (keep existing ones)
def match_transaction(order_id):
    """Match an order with a transaction from CSV data"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Get order details
        cursor.execute('''
            SELECT name, email, expected_amount, receipt_path 
            FROM order_table 
            WHERE id = ?
        ''', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return {'matched': False, 'message': 'Order not found'}
        
        name, email, expected_amount, receipt_path = order
        
        # Search for matching transactions in both venmo and zelle tables
        # Try to match by email first, then by name and amount
        
        # Check Venmo transactions - be more flexible with matching
        cursor.execute('''
            SELECT id, datetime, type, note, from_user, to_user, amount, fee, net_amount
            FROM venmo_transactions 
            WHERE (LOWER(from_user) LIKE ? OR LOWER(note) LIKE ? OR LOWER(from_user) LIKE ? OR LOWER(note) LIKE ?) 
            AND ABS(amount - ?) < 0.01
        ''', (f'%{email.lower()}%', f'%{email.lower()}%', f'%{name.lower()}%', f'%{name.lower()}%', expected_amount))
        
        venmo_match = cursor.fetchone()
        
        if venmo_match:
            return {
                'matched': True, 
                'transaction_type': 'venmo',
                'transaction_id': venmo_match[0],
                'message': f'Matched with Venmo transaction: {venmo_match[4]} -> {venmo_match[5]} for ${venmo_match[6]}'
            }
        
        # Check Zelle transactions
        cursor.execute('''
            SELECT id, date, description, amount, type, balance, payer_identifier
            FROM zelle_transactions 
            WHERE (LOWER(description) LIKE ? OR LOWER(payer_identifier) LIKE ? OR LOWER(description) LIKE ? OR LOWER(payer_identifier) LIKE ?) 
            AND ABS(amount - ?) < 0.01
        ''', (f'%{email.lower()}%', f'%{email.lower()}%', f'%{name.lower()}%', f'%{name.lower()}%', expected_amount))
        
        zelle_match = cursor.fetchone()
        
        if zelle_match:
            return {
                'matched': True, 
                'transaction_type': 'zelle',
                'transaction_id': zelle_match[0],
                'message': f'Matched with Zelle transaction: {zelle_match[2]} for ${zelle_match[3]}'
            }
        
        conn.close()
        return {'matched': False, 'message': 'No matching transaction found'}
        
    except Exception as e:
        print(f"Error in match_transaction: {e}")
        return {'matched': False, 'message': f'Error matching transaction: {str(e)}'}

def detect_csv_format(csv_content):
    """Detect whether CSV is Chase or Venmo format"""
    lines = csv_content.split('\n')
    if not lines:
        return 'unknown'
    
    # Check first few lines for format indicators
    header_line = lines[0].lower()
    
    # Chase format indicators
    if any(indicator in header_line for indicator in ['details', 'posting date', 'description', 'amount', 'type', 'balance']):
        return 'chase'
    
    # Venmo format indicators (common Venmo CSV headers)
    if any(indicator in header_line for indicator in ['datetime', 'type', 'note', 'from', 'to', 'amount', 'fee', 'net', 'status']):
        return 'venmo'
    
    # If we can't detect from header, try to infer from data structure
    if len(lines) > 1:
        first_data_line = lines[1]
        parts = first_data_line.split(',')
        
        # Chase typically has more columns and specific date format
        if len(parts) >= 6 and any('/' in part for part in parts):
            return 'chase'
        
        # Venmo typically has fewer columns and different date format
        if len(parts) <= 8:
            return 'venmo'
    
    return 'unknown'

def parse_chase_csv(csv_content):
    """Parse Chase CSV format and return structured data"""
    transactions = []
    
    # Skip header line
    lines = csv_content.split('\n')[1:]
    
    print(f"Chase CSV Debug - Processing {len(lines)} data lines")
    
    for line in lines:
        if not line.strip():
            continue
            
        # Parse Chase CSV format
        # Format: Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
        parts = line.split(',')
        if len(parts) >= 4:
            try:
                # Extract date
                date_str = parts[1].strip() if len(parts) > 1 else ""
                
                # Extract description
                description = parts[2].strip() if len(parts) > 2 else ""
                
                # Extract amount (remove any currency symbols and convert to float)
                amount_str = parts[3].strip() if len(parts) > 3 else ""
                if amount_str.startswith('$'):
                    amount = float(amount_str.replace('$', '').strip())
                else:
                    try:
                        amount = float(amount_str)
                    except ValueError:
                        continue
                
                # Extract type
                transaction_type = parts[4].strip() if len(parts) > 4 else ""
                
                # Extract balance
                balance = 0.0
                if len(parts) > 5:
                    balance_str = parts[5].strip()
                    if balance_str.startswith('$'):
                        balance = float(balance_str.replace('$', '').strip())
                    else:
                        try:
                            balance = float(balance_str)
                        except ValueError:
                            balance = 0.0
                
                # Extract payer identifier (from description)
                payer_identifier = ""
                if "ZELLE" in description.upper() or "ZELLE PAYMENT" in description.upper():
                    # Try to extract name from description
                    # Common format: "ZELLE PAYMENT FROM JOHN DOE"
                    if "FROM" in description.upper():
                        payer_identifier = description.split("FROM")[-1].strip()
                    else:
                        payer_identifier = description
                
                transactions.append({
                    'date': date_str,
                    'description': description,
                    'amount': amount,
                    'type': transaction_type,
                    'balance': balance,
                    'payer_identifier': payer_identifier
                })
            except Exception as e:
                print(f"Error parsing Chase CSV line: {line}, Error: {e}")
                continue
    
    print(f"Chase CSV Debug - Parsed {len(transactions)} transactions")
    return transactions

def parse_venmo_csv(csv_content):
    """Parse Venmo CSV format and return structured data"""
    transactions = []
    
    # Skip first 3 lines (header rows)
    lines = csv_content.split('\n')[3:]
    
    print(f"Venmo CSV Debug - Processing {len(lines)} data lines")
    
    for line in lines:
        if not line.strip():
            continue
            
        # Parse Venmo CSV format
        # Actual format: ,ID,Datetime,Type,Status,Note,From,To,Amount (total),...
        parts = line.split(',')
        if len(parts) >= 9:
            try:
                # Extract datetime (format: "2025-03-24T15:50:20")
                datetime_str = parts[2].strip()  # Datetime is in column 2
                if not datetime_str or 'T' not in datetime_str:
                    continue
                
                # Extract transaction type
                transaction_type = parts[3].strip() if len(parts) > 3 else ""
                
                # Extract note
                note = parts[5].strip() if len(parts) > 5 else ""
                
                # Extract from user
                from_user = parts[6].strip() if len(parts) > 6 else ""
                
                # Extract to user
                to_user = parts[7].strip() if len(parts) > 7 else ""
                
                # Extract amount (remove any currency symbols and convert to float)
                amount_str = parts[8].strip()  # Amount (total) is in column 8
                if amount_str.startswith('$'):
                    amount = float(amount_str.replace('$', '').strip())
                else:
                    continue
                
                # Extract fee (if available)
                fee = 0.0
                if len(parts) > 9:
                    fee_str = parts[9].strip()
                    if fee_str.startswith('$'):
                        fee = float(fee_str.replace('$', '').strip())
                
                # Calculate net amount
                net_amount = amount - fee
                
                transactions.append({
                    'datetime': datetime_str,
                    'type': transaction_type,
                    'note': note,
                    'from_user': from_user,
                    'to_user': to_user,
                    'amount': amount,
                    'fee': fee,
                    'net_amount': net_amount
                })
            except Exception as e:
                print(f"Error parsing Venmo CSV line: {line}, Error: {e}")
                continue

    print(f"Venmo CSV Debug - Parsed {len(transactions)} transactions")
    return transactions

@app.route('/api/receipts/<filename>', methods=['GET'])
@login_required
def serve_receipt(filename):
    """Serve receipt files"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=False)
        else:
            return jsonify({'success': False, 'message': 'Receipt file not found'}), 404
    except Exception as e:
        log_error(logger, e, f"Error serving receipt: {filename}")
        return jsonify({'success': False, 'message': 'Error serving receipt'}), 500

# Serve React frontend
@app.route('/', methods=['GET'])
def serve_frontend():
    """Serve the React frontend application"""
    try:
        return send_from_directory('frontend/build', 'index.html')
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'Frontend files not found. Please run "npm run build" in the frontend directory.'}), 500

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the React build directory"""
    try:
        return send_from_directory('frontend/build', path)
    except FileNotFoundError:
        # If the file doesn't exist, serve the index.html for client-side routing
        return send_from_directory('frontend/build', 'index.html')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 