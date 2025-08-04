#!/usr/bin/env python3
"""
Debug script to trace the upload flow and see where files are going
"""

import os
from dotenv import load_dotenv

def check_upload_flow():
    print("Debugging Upload Flow")
    print("=" * 40)
    
    # Load environment variables
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("Loaded .env file")
    
    # Check storage service
    from storage_service import get_storage_service, upload_receipt
    storage = get_storage_service()
    
    print(f"R2 enabled: {storage.is_enabled()}")
    print(f"Bucket: {storage.bucket_name}")
    
    # Test receipt upload function (this is what the app uses)
    print("\nTesting receipt upload function...")
    import io
    test_file = io.BytesIO(b"Test receipt content")
    success, storage_path = upload_receipt(test_file, "debug_test_receipt.jpg")
    
    print(f"Upload success: {success}")
    print(f"Storage path: {storage_path}")
    
    if success:
        # Check if file exists in R2
        if storage_path.startswith('receipts/'):
            print("File should be in R2 under receipts/ folder")
            exists = storage.file_exists(storage_path)
            print(f"File exists in R2: {exists}")
        else:
            print("File was stored locally (not in R2)")
            local_path = os.path.join('uploads', storage_path)
            exists = os.path.exists(local_path)
            print(f"File exists locally: {exists}")
    
    # List current files in R2
    print(f"\nCurrent files in R2 bucket:")
    files = storage.list_files()
    for file in files:
        print(f"  - {file}")
    
    # List files in receipts folder specifically
    print(f"\nFiles in receipts/ folder:")
    receipt_files = storage.list_files("receipts/")
    for file in receipt_files:
        print(f"  - {file}")

if __name__ == "__main__":
    check_upload_flow()