#!/usr/bin/env python3
"""
Test script to verify Cloudflare R2 connection and configuration
Run this after setting up your R2 environment variables
"""

import os
import sys
from storage_service import get_storage_service
import tempfile
import io

def test_r2_connection():
    """Test R2 connection and basic operations"""
    print("🔍 Testing Cloudflare R2 Connection...")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'R2_ACCOUNT_ID', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID', 
        'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT'
    ]
    
    print("📋 Checking environment variables:")
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {missing_vars}")
        print("\nPlease set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=<your_value>")
        return False
    
    # Test storage service initialization
    print("\n🔧 Initializing storage service...")
    storage = get_storage_service()
    
    if not storage.is_enabled():
        print("❌ R2 storage service failed to initialize")
        return False
    
    print("✅ R2 storage service initialized successfully")
    
    # Test file upload
    print("\n📤 Testing file upload...")
    test_content = b"This is a test file for R2 connectivity"
    test_file = io.BytesIO(test_content)
    test_key = "test/connectivity_test.txt"
    
    upload_success = storage.upload_file(test_file, test_key, 'text/plain')
    if upload_success:
        print("✅ File upload successful")
    else:
        print("❌ File upload failed")
        return False
    
    # Test file existence check
    print("\n🔍 Testing file existence check...")
    if storage.file_exists(test_key):
        print("✅ File existence check successful")
    else:
        print("❌ File existence check failed")
        return False
    
    # Test file download
    print("\n📥 Testing file download...")
    downloaded_path = storage.download_file(test_key)
    if downloaded_path and os.path.exists(downloaded_path):
        with open(downloaded_path, 'rb') as f:
            downloaded_content = f.read()
        
        if downloaded_content == test_content:
            print("✅ File download and content verification successful")
            # Clean up downloaded file
            os.remove(downloaded_path)
        else:
            print("❌ Downloaded content doesn't match uploaded content")
            return False
    else:
        print("❌ File download failed")
        return False
    
    # Test file listing
    print("\n📋 Testing file listing...")
    files = storage.list_files("test/")
    if test_key in files:
        print(f"✅ File listing successful (found {len(files)} files in test/ prefix)")
    else:
        print("❌ File listing failed or test file not found")
        return False
    
    # Clean up test file
    print("\n🧹 Cleaning up test file...")
    if storage.delete_file(test_key):
        print("✅ Test file cleanup successful")
    else:
        print("⚠️  Test file cleanup failed (file may still exist)")
    
    print("\n🎉 All R2 connectivity tests passed!")
    print("\nYour Cloudflare R2 storage is properly configured and ready to use.")
    return True

def main():
    """Main function"""
    print("Cloudflare R2 Connectivity Test")
    print("=" * 50)
    
    try:
        success = test_r2_connection()
        if success:
            print("\n✅ R2 setup is complete and working!")
            sys.exit(0)
        else:
            print("\n❌ R2 setup has issues that need to be resolved.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()