#!/usr/bin/env python3
"""
Debug script to simulate form submission and trace the upload process
"""

import os
import io
from dotenv import load_dotenv

def simulate_form_submission():
    print("Debugging Form Submission Process")
    print("=" * 50)
    
    # Load environment variables
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("Loaded .env file")
    
    # Import the functions used in the actual form submission
    from storage_service import get_storage_service, upload_receipt
    from werkzeug.utils import secure_filename
    import uuid
    
    storage = get_storage_service()
    print(f"R2 enabled: {storage.is_enabled()}")
    
    # Simulate the exact process from app.py
    print("\nSimulating form submission process...")
    
    # Step 1: Generate UUID (like in the form)
    order_uuid = str(uuid.uuid4())
    print(f"Generated order UUID: {order_uuid}")
    
    # Step 2: Create a test file (simulating uploaded file)
    test_content = b"This is a test receipt image content"
    test_file = io.BytesIO(test_content)
    
    # Step 3: Secure filename (like in the form)
    original_filename = "test_receipt.jpg"
    filename = secure_filename(f"{order_uuid}_{original_filename}")
    print(f"Secure filename: {filename}")
    
    # Step 4: Upload using the same function as the form
    print(f"Calling upload_receipt with filename: {filename}")
    success, storage_path = upload_receipt(test_file, filename)
    
    print(f"Upload result:")
    print(f"  Success: {success}")
    print(f"  Storage path: {storage_path}")
    
    if success:
        # Check if file exists
        if storage_path.startswith('receipts/'):
            exists = storage.file_exists(storage_path)
            print(f"  File exists in R2: {exists}")
        else:
            local_path = os.path.join('uploads', storage_path)
            exists = os.path.exists(local_path)
            print(f"  File exists locally: {exists}")
    
    # List all files in receipts folder
    print(f"\nAll files in receipts/ folder:")
    receipt_files = storage.list_files("receipts/")
    for i, file in enumerate(receipt_files, 1):
        print(f"  {i}. {file}")
    
    return success, storage_path

def check_app_configuration():
    print("\nChecking App Configuration")
    print("=" * 30)
    
    # Check if the app is importing storage_service correctly
    try:
        import app
        print("App module imported successfully")
        
        # Check if storage service is imported in app
        if hasattr(app, 'upload_receipt'):
            print("upload_receipt function available in app")
        else:
            print("WARNING: upload_receipt not found in app module")
            
        if hasattr(app, 'get_storage_service'):
            print("get_storage_service function available in app")
        else:
            print("WARNING: get_storage_service not found in app module")
            
    except Exception as e:
        print(f"ERROR importing app: {e}")

def main():
    print("Form Submission Debug Tool")
    print("=" * 50)
    
    # Check app configuration
    check_app_configuration()
    
    # Simulate form submission
    success, path = simulate_form_submission()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: Form submission simulation worked!")
        print(f"File stored at: {path}")
        print("\nIf this works but your real form doesn't, the issue might be:")
        print("1. File upload errors in the web form")
        print("2. File size limits")
        print("3. File type restrictions")
        print("4. Missing error handling in the form")
    else:
        print("FAILED: Form submission simulation failed")
        print("This indicates an issue with the upload process")

if __name__ == "__main__":
    main()