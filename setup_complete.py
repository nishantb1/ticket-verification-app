#!/usr/bin/env python3
"""
Complete setup script for Zelle/Venmo Ticket Verifier
Initializes database, imports Chase CSV, and provides setup instructions
"""

import sqlite3
import os
import re
import csv
from datetime import datetime

def init_database():
    """Initialize the database with tables"""
    print("Initializing database...")
    
    try:
        conn = sqlite3.connect('tickets.db')
        cursor = conn.cursor()
        
        # Create Wave table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wave (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                price_boy REAL NOT NULL,
                price_girl REAL NOT NULL
            )
        ''')
        
        # Create Order table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                referral TEXT,
                boys_count INTEGER NOT NULL,
                girls_count INTEGER NOT NULL,
                wave_id INTEGER,
                expected_amount REAL NOT NULL,
                ocr_amount REAL,
                ocr_date DATE,
                ocr_name TEXT,
                status TEXT DEFAULT 'Pending',
                receipt_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wave_id) REFERENCES wave (id)
            )
        ''')
        
        # Create Transaction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_transaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                amount REAL NOT NULL,
                payer_identifier TEXT NOT NULL,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create Ticket table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (order_id) REFERENCES order_table (id)
            )
        ''')
        
        # Insert default waves if they don't exist
        cursor.execute('SELECT COUNT(*) FROM wave')
        if cursor.fetchone()[0] == 0:
            waves = [
                ('Wave 1', '2024-01-01', '2024-01-31', 25.00, 20.00),
                ('Wave 2', '2024-02-01', '2024-02-29', 30.00, 25.00),
                ('Wave 3', '2024-03-01', '2024-03-31', 35.00, 30.00)
            ]
            cursor.executemany('INSERT INTO wave (name, start_date, end_date, price_boy, price_girl) VALUES (?, ?, ?, ?, ?)', waves)
            print("✓ Default waves created")
        
        conn.commit()
        conn.close()
        print("✓ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = ['uploads', 'templates']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")
    
    return True

def parse_chase_csv(filename):
    """Parse Chase CSV format specifically"""
    transactions = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # Skip header row
            next(file)
            
            for line in file:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse Chase CSV format: Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
                parts = line.split(',')
                if len(parts) >= 4:
                    try:
                        # Extract date (format: 3/6/25)
                        date_str = parts[1].strip()
                        if date_str:
                            # Convert to YYYY-MM-DD format
                            date_parts = date_str.split('/')
                            if len(date_parts) == 3:
                                month, day, year = date_parts
                                year = '20' + year if len(year) == 2 else year
                                date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            else:
                                continue
                        else:
                            continue
                        
                        # Extract amount (remove any currency symbols and convert to float)
                        amount_str = parts[3].strip()
                        amount = float(amount_str.replace('$', '').replace(',', ''))
                        
                        # Extract payer name from description
                        description = parts[2].strip()
                        
                        # Parse Zelle payment descriptions
                        # Format: "ZELLE PAYMENT FROM JOHN DOE" or "Zelle payment from JOHN DOE"
                        payer_match = re.search(r'(?:ZELLE PAYMENT FROM|Zelle payment from)\s+(.+)', description, re.IGNORECASE)
                        if payer_match:
                            payer_name = payer_match.group(1).strip()
                        else:
                            # Fallback: use description as payer name
                            payer_name = description
                        
                        transactions.append({
                            'date': date,
                            'amount': amount,
                            'payer_identifier': payer_name
                        })
                        
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Error parsing line: {line}, Error: {e}")
                        continue
        
        return transactions
    except FileNotFoundError:
        print(f"Warning: Chase CSV file {filename} not found")
        return []

def import_chase_transactions():
    """Import Chase CSV transactions"""
    print("Importing Chase CSV transactions...")
    
    filename = "Chase9856_Activity_20250306.CSV"
    
    if not os.path.exists(filename):
        print(f"⚠  Chase CSV file {filename} not found - skipping import")
        return True
    
    transactions = parse_chase_csv(filename)
    
    if not transactions:
        print("⚠  No valid transactions found in CSV")
        return True
    
    try:
        conn = sqlite3.connect('tickets.db')
        cursor = conn.cursor()
        
        imported_count = 0
        for transaction in transactions:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO payment_transaction (date, amount, payer_identifier)
                    VALUES (?, ?, ?)
                ''', (transaction['date'], transaction['amount'], transaction['payer_identifier']))
                imported_count += 1
            except Exception as e:
                print(f"Warning: Error importing transaction: {transaction}, Error: {e}")
        
        conn.commit()
        
        # Check total transactions
        cursor.execute("SELECT COUNT(*) FROM payment_transaction")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✓ Imported {imported_count} new transactions")
        print(f"✓ Total transactions in database: {total_count}")
        
        # Show some examples
        print("\nSample transactions:")
        for i, transaction in enumerate(transactions[:5]):
            print(f"  {i+1}. {transaction['date']} - ${transaction['amount']} - {transaction['payer_identifier']}")
        
        if len(transactions) > 5:
            print(f"  ... and {len(transactions) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"✗ Error importing transactions: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")
    
    # Check Python packages
    try:
        import flask
        print("✓ Flask")
    except ImportError:
        print("✗ Flask - Install with: pip install flask")
    
    try:
        import pytesseract
        print("✓ pytesseract")
    except ImportError:
        print("✗ pytesseract - Install with: pip install pytesseract")
    
    try:
        from PIL import Image
        print("✓ Pillow")
    except ImportError:
        print("✗ Pillow - Install with: pip install Pillow")
    
    try:
        import pdf2image
        print("✓ pdf2image")
    except ImportError:
        print("✗ pdf2image - Install with: pip install pdf2image")
    
    
    
    # Check system dependencies
    print("\nSystem dependencies (install manually):")
    print("  - Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
    print("  - Poppler (for PDF processing): http://blog.alivate.com.au/poppler-windows/")
    
    return True

def main():
    """Main setup function"""
    print("ΔΕΨ Ticket Verifier - Complete Setup")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    print("\n" + "=" * 50)
    
    # Create directories
    dirs_ok = create_directories()
    
    # Initialize database
    db_ok = init_database()
    
    # Import Chase CSV
    csv_ok = import_chase_transactions()
    
    print("\n" + "=" * 50)
    print("Setup Results:")
    print(f"Directories: {'✓ PASS' if dirs_ok else '✗ FAIL'}")
    print(f"Database: {'✓ PASS' if db_ok else '✗ FAIL'}")
    print(f"CSV Import: {'✓ PASS' if csv_ok else '✗ FAIL'}")
    
    if all([dirs_ok, db_ok, csv_ok]):
        print("\n🎉 Setup completed successfully!")
        
        print("\n" + "=" * 50)
        print("NEXT STEPS:")
        print("=" * 50)
        
        print("\n1. INSTALL PYTHON DEPENDENCIES:")
        print("   pip install -r requirements.txt")
        
        print("\n2. START THE FLASK APPLICATION:")
        print("   python app.py")
        print("   (Application will run on http://localhost:5000)")
        
        print("\n3. CONFIGURE SMTP SETTINGS:")
        print("   Edit app.py and update SMTP settings:")
        print("   - sender_email")
        print("   - sender_password")
        
        print("\n4. TEST THE APPLICATION:")
        print("   - Open http://localhost:5000")
        print("   - Submit a test order")
        print("   - Check admin dashboard at /admin")
        print("   - View analytics at /analytics")
        
        print("\n" + "=" * 50)
        print("DEPLOYMENT:")
        print("=" * 50)
        
        print("\nFor Heroku deployment:")
        print("1. Create Heroku app")
        print("2. Add buildpacks for Python and system dependencies")
        print("3. Deploy with: git push heroku main")
        
        print("\nFor PythonAnywhere:")
        print("1. Upload files to PythonAnywhere")
        print("2. Install system dependencies via SSH")
        print("3. Configure WSGI file")
        
        print("\n" + "=" * 50)
        print("SUPPORT:")
        print("=" * 50)
        print("For issues and questions, check the README.md file")
        print("or create an issue on the GitHub repository.")
        
    else:
        print("\n❌ Setup failed. Please check the errors above and try again.")

if __name__ == "__main__":
    main() 