#!/usr/bin/env python3
"""
Debug script to add detailed logging to the form submission process
"""

import os
from dotenv import load_dotenv

def add_debug_logging():
    print("Adding Debug Logging to App")
    print("=" * 40)
    
    # Load environment variables
    if os.path.exists('.env'):
        load_dotenv('.env')
    
    # Import app and add logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    from storage_service import get_storage_service
    storage = get_storage_service()
    
    print(f"R2 Status: {'Enabled' if storage.is_enabled() else 'Disabled'}")
    print(f"Bucket: {storage.bucket_name if storage.is_enabled() else 'N/A'}")
    
    # Check if uploads directory exists
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        print(f"Local uploads directory has {len(files)} files")
        if files:
            print("Recent local files:")
            for f in files[-5:]:  # Show last 5 files
                print(f"  - {f}")
    else:
        print("Local uploads directory does not exist")
    
    # Check R2 files
    if storage.is_enabled():
        r2_files = storage.list_files("receipts/")
        print(f"R2 receipts folder has {len(r2_files)} files")
        if r2_files:
            print("Recent R2 files:")
            for f in r2_files[-5:]:  # Show last 5 files
                print(f"  - {f}")

if __name__ == "__main__":
    add_debug_logging()