# ΔΕΨ Ticket Verifier

A Flask web application designed for free-tier hosting (Heroku, PythonAnywhere) to automate Zelle/Venmo ticket verification for Delta Epsilon Psi fraternity events. The application uses SQLite for storage and pytesseract for OCR processing.

A Flask web application designed for free-tier hosting (Heroku, PythonAnywhere) to automate Zelle/Venmo ticket verification. The application uses SQLite for storage and pytesseract for OCR processing.

## Features

### 1. Admin Authentication System
- **Secure Login**: Password-protected admin access with session management
- **User Management**: Admin user accounts with roles (admin, super_admin)
- **Password Security**: Hashed passwords using Werkzeug security
- **Audit Trail**: Complete logging of all admin actions
- **Session Management**: Secure session handling with automatic logout
- **Password Change**: Admin password change functionality

### 2. Customer Intake Form
- **Fields**: Purchaser name, email, referral code
- **Ticket Counts**: Numeric inputs for boys' and girls' tickets
- **Wave Selection**: Manual wave selection or auto-assignment based on date
- **File Upload**: Support for Zelle/Venmo receipt images and PDFs
- **UUID Generation**: Unique identifier for each submission

### 2. Database Models (SQLite)
- **Wave**: Pricing tiers with date ranges
- **Order**: Complete order information with OCR results
- **Transaction**: Imported CSV transaction data
- **Ticket**: Individual ticket records

### 3. OCR & Matching Logic
- **Text Extraction**: Uses pytesseract for OCR processing
- **Amount Calculation**: Automatic expected amount computation
- **Transaction Matching**: Matches OCR results with imported transactions
- **Status Updates**: Automatic verification or flagging

### 4. Admin Dashboard
- **Secure Access**: Login-required admin dashboard with role-based access
- **Kanban View**: Visual organization by status (Pending, Verified, Flagged, Completed)
- **Order Management**: Inline editing of ticket counts and wave assignment
- **Actions**: Approve, reject, and resend upload links
- **CSV Import**: Upload daily/weekly transaction data
- **User Management**: Admin user information and logout functionality

### 5. Order Management
- **Order Approval**: Approve orders and mark them as completed
- **Status Tracking**: Track order status through the verification process
- **Audit Trail**: Complete logging of all actions

### 6. Analytics & Reporting
- **Real-time Statistics**: Order counts, verification rates, daily volume
- **Performance Metrics**: Auto-verification success rates
- **Activity Logging**: Timestamp tracking for all operations

## Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR (for pytesseract)
- Poppler (for PDF processing)

### System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

#### macOS:
```bash
brew install tesseract poppler
```

#### Windows:
Download and install:
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)

### Python Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd zelle_venmo_verifier
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run setup script**:
```bash
python setup_complete.py
```

5. **Start the application**:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Troubleshooting OCR Issues

If you encounter OCR errors like "Tesseract OCR not found":

1. **Verify Tesseract Installation**:
   ```bash
   tesseract --version
   ```

2. **Check Python can find Tesseract**:
   ```python
   import pytesseract
   print(pytesseract.get_tesseract_version())
   ```

3. **Common Solutions**:
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Ensure Tesseract is in your system PATH
   - **Render/Heroku**: Add buildpack: `heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt`

4. **Test OCR Functionality**:
   - Upload a clear image with text
   - Check the admin logs for OCR processing details
   - Verify the image format is supported (PNG, JPG, PDF)

### Render Deployment

For Render deployment, system dependencies are automatically installed via the `apt-packages` file:
- `tesseract-ocr` - OCR engine for text extraction
- `poppler-utils` - PDF processing utilities

The `render.yaml` configuration handles the deployment automatically.

#### Database Persistence on Render

The application uses a persistent disk on Render to store the database:
- **Database Path**: `/var/data/tickets.db` (configured via `DATABASE_PATH` environment variable)
- **Disk Mount**: `/var/data` with 1GB storage
- **Persistence**: Data survives deployments and restarts

**If orders are lost after deployment:**
1. Check the **DB Status** page in the admin panel (`/admin/db-status`)
2. Verify the database path points to `/var/data/tickets.db`
3. Ensure the persistent disk is properly mounted
4. Check application logs for database initialization errors

**If OCR is not working:**
1. Check the **OCR Status** page in the admin panel (`/admin/check-tesseract`)
2. Verify Tesseract is installed via the `apt-packages` file
3. Check if the `TESSERACT_CMD` environment variable is set correctly
4. Ensure all dependencies are installed: `tesseract-ocr`, `poppler-utils`, `libtesseract-dev`

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **Admin Login**: `http://localhost:5000/admin/login`

**⚠️ Important**: Change the default password immediately after first login!

## Usage

### Customer Flow

1. **Submit Order**: Customers fill out the intake form with their information
2. **Upload Receipt**: Upload Zelle/Venmo payment screenshot or PDF
3. **Auto-Processing**: OCR extracts payment details and matches with transactions
4. **Status Update**: Order is automatically verified or flagged for review

### Admin Flow

1. **Dashboard Access**: Navigate to `/admin` for the Kanban board
2. **CSV Import**: Upload transaction data via the CSV upload modal
3. **Order Review**: Review flagged orders and approve/reject as needed
4. **Order Completion**: Approved orders are marked as completed

## Database Schema

### Admin Users Table
```sql
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Audit Log Table
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_user_id) REFERENCES admin_users (id)
);
```

### Wave Table
```sql
CREATE TABLE wave (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price_boy REAL NOT NULL,
    price_girl REAL NOT NULL
);
```

### Order Table
```sql
CREATE TABLE order_table (
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
);
```

### Transaction Table
```sql
CREATE TABLE payment_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    amount REAL NOT NULL,
    payer_identifier TEXT NOT NULL,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```



## Deployment

### Heroku Deployment

1. **Create Heroku app**:
```bash
heroku create your-app-name
```

2. **Add buildpacks**:
```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
```

3. **Create Aptfile**:
```
tesseract-ocr
poppler-utils
```

4. **Deploy**:
```bash
git push heroku main
```

### PythonAnywhere Deployment

1. **Upload files** to your PythonAnywhere account
2. **Install system dependencies** via SSH:
```bash
sudo apt-get install tesseract-ocr poppler-utils
```
3. **Configure WSGI file** to point to your Flask app
4. **Set up virtual environment** and install requirements

## Configuration

### Application Settings
Update the configuration in `app.py` as needed for your deployment.

### Wave Configuration
Default waves are created automatically. Modify in `init_db()` function:
```python
waves = [
    ('Wave 1', '2024-01-01', '2024-01-31', 25.00, 20.00),
    ('Wave 2', '2024-02-01', '2024-02-29', 30.00, 25.00),
    ('Wave 3', '2024-03-01', '2024-03-31', 35.00, 30.00)
]
```

## CSV Import Format

The application supports Chase CSV format with the following columns:
- `Details`: Transaction type
- `Posting Date`: Transaction date (M/D/YY format)
- `Description`: Transaction description (parsed for payer name)
- `Amount`: Transaction amount (numeric)

Example Chase CSV:
```csv
Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
CREDIT,3/6/25,ZELLE PAYMENT FROM JOHN DOE,50.00,PARTNERFI_TO_CHASE,,
CREDIT,3/6/25,Zelle payment from JANE SMITH,75.00,QUICKPAY_CREDIT,,
```

## Security Considerations

- **File Upload**: Only allows specific file types (PNG, JPG, JPEG, PDF)
- **Input Validation**: All form inputs are validated
- **SQL Injection**: Uses parameterized queries
- **Secret Key**: Change the default secret key in production

## Troubleshooting

### OCR Issues
- Ensure Tesseract is properly installed
- Check image quality and format
- Verify file permissions



### Database Issues
- Ensure SQLite file is writable
- Check disk space
- Verify database permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository. 