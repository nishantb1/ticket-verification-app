#!/usr/bin/env python3
"""
Add detailed logging to the form submission process
Run this to patch the app with extra logging
"""

import os
from dotenv import load_dotenv

def patch_app_with_logging():
    """Add detailed logging to app.py submit_order function"""
    
    # Load environment variables
    if os.path.exists('.env'):
        load_dotenv('.env')
    
    print("Patching app with detailed logging...")
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Add logging statements to the submit_order function
    # Look for the file upload section and add logging
    
    old_upload_section = '''        # Handle file upload
        receipt_path = None
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{order_uuid}_{file.filename}")
                
                # Upload to R2 or local storage
                success, storage_path = upload_receipt(file, filename)
                if success:
                    receipt_path = storage_path
                else:
                    flash('Failed to upload receipt file', 'error')
                    return redirect(url_for('index'))'''
    
    new_upload_section = '''        # Handle file upload
        receipt_path = None
        logger.info(f"DEBUG: Starting file upload process for order {order_uuid}")
        
        if 'receipt' in request.files:
            file = request.files['receipt']
            logger.info(f"DEBUG: File found in request: {file.filename if file else 'None'}")
            
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{order_uuid}_{file.filename}")
                logger.info(f"DEBUG: Secure filename created: {filename}")
                
                # Check storage service status
                from storage_service import get_storage_service
                storage = get_storage_service()
                logger.info(f"DEBUG: R2 storage enabled: {storage.is_enabled()}")
                
                # Upload to R2 or local storage
                logger.info(f"DEBUG: Calling upload_receipt with filename: {filename}")
                success, storage_path = upload_receipt(file, filename)
                logger.info(f"DEBUG: Upload result - Success: {success}, Path: {storage_path}")
                
                if success:
                    receipt_path = storage_path
                    logger.info(f"DEBUG: Receipt path set to: {receipt_path}")
                else:
                    logger.error(f"DEBUG: Upload failed for file: {filename}")
                    flash('Failed to upload receipt file', 'error')
                    return redirect(url_for('index'))
            else:
                logger.warning(f"DEBUG: File not allowed or empty: {file.filename if file else 'None'}")
                flash('Invalid file type', 'error')
                return redirect(url_for('index'))
        else:
            logger.info(f"DEBUG: No receipt file in request for order {order_uuid}")'''
    
    # Replace the section
    if old_upload_section in content:
        content = content.replace(old_upload_section, new_upload_section)
        
        # Write back to app.py
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("SUCCESS: Added detailed logging to app.py")
        print("Now when you submit a form, you'll see detailed logs about the upload process")
        print("Look for lines starting with 'DEBUG:' in your application logs")
        
    else:
        print("WARNING: Could not find the upload section to patch")
        print("The app.py file might have been modified")

def main():
    print("Adding Debug Logging to Form Submission")
    print("=" * 50)
    
    patch_app_with_logging()
    
    print("\nNext steps:")
    print("1. Restart your application: python run_local_with_r2.py")
    print("2. Submit a test order with a receipt")
    print("3. Check the console output for DEBUG messages")
    print("4. Look for where the upload process might be failing")

if __name__ == "__main__":
    main()