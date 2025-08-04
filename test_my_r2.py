#!/usr/bin/env python3
"""
Test your R2 connection using .env file
"""

import os
from dotenv import load_dotenv

def main():
    print("Testing R2 Connection with .env file")
    print("=" * 40)
    
    # Load environment variables from .env file
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("Loaded environment variables from .env file")
    else:
        print("ERROR: .env file not found")
        return
    
    # Check if all variables are loaded
    required_vars = ['R2_ACCOUNT_ID', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT']
    
    print("\nEnvironment Variables:")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if 'SECRET' in var:
                display_value = f"{value[:8]}..."
            else:
                display_value = value
            print(f"  {var}: {display_value}")
        else:
            print(f"  {var}: NOT SET")
            return
    
    # Test R2 connection
    print("\nTesting R2 connection...")
    try:
        from storage_service import get_storage_service
        storage = get_storage_service()
        
        if storage.is_enabled():
            print("SUCCESS: R2 storage is enabled")
            print(f"Account ID: {storage.account_id}")
            print(f"Bucket: {storage.bucket_name}")
            
            # Test bucket access
            print("\nTesting bucket access...")
            files = storage.list_files()
            print(f"SUCCESS: Found {len(files)} files in bucket")
            
            # Test upload
            print("\nTesting file upload...")
            import io
            test_content = b"Test file content"
            test_file = io.BytesIO(test_content)
            success = storage.upload_file(test_file, "test_connection.txt", "text/plain")
            
            if success:
                print("SUCCESS: File upload works")
                
                # Test download
                print("Testing file download...")
                downloaded_path = storage.download_file("test_connection.txt")
                if downloaded_path:
                    print("SUCCESS: File download works")
                    os.remove(downloaded_path)  # Clean up
                    
                    # Clean up test file from R2
                    storage.delete_file("test_connection.txt")
                    print("SUCCESS: Test file cleaned up")
                else:
                    print("ERROR: File download failed")
            else:
                print("ERROR: File upload failed")
        else:
            print("ERROR: R2 storage failed to initialize")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()