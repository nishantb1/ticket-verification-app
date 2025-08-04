# Local Testing Guide for Cloudflare R2 Integration

This guide explains how to test the R2 integration locally on your development machine.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Without R2 (Local Storage Fallback)
```bash
python test_local_setup.py
```
This tests that the application works with local storage when R2 is not configured.

### 3. Set Up R2 for Local Testing (Optional)

If you want to test actual R2 functionality locally:

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in your R2 credentials in `.env`:**
   ```bash
   # Edit .env with your actual values
   R2_ACCOUNT_ID=your_actual_account_id
   R2_BUCKET_NAME=your_actual_bucket_name
   R2_ACCESS_KEY_ID=your_actual_access_key
   R2_SECRET_ACCESS_KEY=your_actual_secret_key
   R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
   ```

3. **Test R2 connection:**
   ```bash
   python test_r2_connection.py
   ```

4. **Test complete local setup:**
   ```bash
   python test_local_setup.py
   ```

### 4. Run the Application Locally

**With R2 support:**
```bash
python run_local_with_r2.py
```

**Or standard Flask development:**
```bash
# Load environment variables first
export $(cat .env | xargs)
python app.py
```

## Testing Scenarios

### Scenario 1: No R2 Configuration
- Application uses local `uploads/` and `csv_uploads/` directories
- Files are stored locally
- Perfect for development without cloud dependencies

### Scenario 2: R2 Configured and Working
- Application uploads files to your R2 bucket
- Files are retrieved from R2 when needed
- Temporary files are automatically cleaned up

### Scenario 3: R2 Configured but Failing
- Application detects R2 failure and falls back to local storage
- Error messages logged but application continues working

## Manual Testing Steps

### Test File Uploads

1. **Start the local server:**
   ```bash
   python run_local_with_r2.py
   ```

2. **Open your browser:** http://localhost:5000

3. **Submit a ticket with a receipt:**
   - Fill out the form
   - Upload an image or PDF receipt
   - Submit the form

4. **Check the logs** to see if R2 or local storage was used

5. **Access admin panel:** http://localhost:5000/admin/login
   - Default credentials: `admin` / `admin123`
   - Upload a CSV file to test CSV storage

### Test File Retrieval

1. **View uploaded receipts** in the admin panel
2. **Click on receipt links** to verify files are accessible
3. **Check logs** for any temporary file cleanup messages

## Debugging Tips

### Check Storage Status
```python
from storage_service import get_storage_service

storage = get_storage_service()
print(f"R2 enabled: {storage.is_enabled()}")
if storage.is_enabled():
    print(f"Bucket: {storage.bucket_name}")
    print(f"Endpoint: {storage.endpoint}")
```

### View Application Logs
The application logs will show:
- R2 initialization status
- File upload/download operations
- Fallback to local storage
- Temporary file cleanup

### Common Issues

1. **"Missing R2 environment variables" warning**
   - This is normal if you haven't set up R2
   - Application will use local storage

2. **"Failed to initialize R2 client" error**
   - Check your R2 credentials in `.env`
   - Verify your bucket exists
   - Test with `python test_r2_connection.py`

3. **Files not found after upload**
   - Check if files are in `uploads/` directory (local storage)
   - Or check R2 bucket in Cloudflare dashboard

## Environment Variables Reference

### Required for R2
```bash
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_BUCKET_NAME=your_r2_bucket_name
R2_ACCESS_KEY_ID=your_r2_access_key_id
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
```

### Optional for Local Development
```bash
SECRET_KEY=your-local-secret-key
FLASK_ENV=development
DATABASE_PATH=tickets.db
TESSERACT_CMD=/usr/local/bin/tesseract  # if tesseract is in non-standard location
```

## File Structure After Testing

```
your-project/
├── .env                    # Your local R2 credentials (gitignored)
├── .env.example           # Template for R2 credentials
├── uploads/               # Local receipt storage (if R2 not used)
├── csv_uploads/           # Local CSV storage (if R2 not used)
├── tickets.db             # Local SQLite database
├── logs/                  # Application logs
└── ...
```

## Production vs Local Differences

| Aspect | Local Development | Production (Render) |
|--------|------------------|-------------------|
| Environment Variables | `.env` file | Render dashboard |
| Database | Local SQLite | Persistent disk SQLite |
| File Storage | Local dirs or R2 | R2 (recommended) |
| Logs | Console + files | Render logs |

## Next Steps

After local testing works:

1. **Deploy to production** with R2 environment variables
2. **Test production deployment** with real file uploads
3. **Monitor R2 usage** in Cloudflare dashboard
4. **Migrate existing files** if needed with `python migrate_to_r2.py`

## Troubleshooting

If you encounter issues:

1. **Check the logs** for error messages
2. **Run the test scripts** to isolate the problem
3. **Verify R2 credentials** with the connection test
4. **Test without R2** to ensure basic functionality works
5. **Check file permissions** in local directories

For more help, see:
- `CLOUDFLARE_R2_SETUP.md` for R2 configuration
- Application logs in `logs/` directory
- Cloudflare R2 documentation