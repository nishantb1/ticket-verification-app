#!/usr/bin/env python3
"""
Quick R2 status checker
Use this to verify your R2 connection and see current status
"""

import os
import sys
from datetime import datetime

def check_environment_variables():
    """Check if all required R2 environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("-" * 40)
    
    required_vars = {
        'R2_ACCOUNT_ID': 'Your Cloudflare Account ID',
        'R2_BUCKET_NAME': 'Your R2 bucket name',
        'R2_ACCESS_KEY_ID': 'R2 access key ID',
        'R2_SECRET_ACCESS_KEY': 'R2 secret access key',
        'R2_ENDPOINT': 'R2 endpoint URL'
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set ({description})")
            all_set = False
    
    return all_set

def check_storage_service():
    """Check if storage service initializes properly"""
    print("\n🔧 Checking Storage Service")
    print("-" * 40)
    
    try:
        from storage_service import get_storage_service
        storage = get_storage_service()
        
        print(f"Service initialized: ✅")
        print(f"R2 enabled: {'✅' if storage.is_enabled() else '❌'}")
        
        if storage.is_enabled():
            print(f"Account ID: {storage.account_id}")
            print(f"Bucket name: {storage.bucket_name}")
            print(f"Endpoint: {storage.endpoint}")
            return True
        else:
            print("❌ R2 storage service failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing storage service: {e}")
        return False

def test_bucket_access():
    """Test basic bucket operations"""
    print("\n🪣 Testing Bucket Access")
    print("-" * 40)
    
    try:
        from storage_service import get_storage_service
        storage = get_storage_service()
        
        if not storage.is_enabled():
            print("❌ Storage service not enabled, skipping bucket tests")
            return False
        
        # Test bucket access by listing files
        print("📋 Testing bucket listing...")
        files = storage.list_files()
        print(f"✅ Bucket accessible - found {len(files)} files")
        
        if len(files) > 0:
            print("📁 Recent files in bucket:")
            for file in files[:5]:  # Show first 5 files
                print(f"   - {file}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
        
        return True
        
    except Exception as e:
        print(f"❌ Bucket access test failed: {e}")
        return False

def test_upload_download():
    """Test upload and download operations"""
    print("\n📤📥 Testing Upload/Download")
    print("-" * 40)
    
    try:
        from storage_service import get_storage_service
        import io
        
        storage = get_storage_service()
        
        if not storage.is_enabled():
            print("❌ Storage service not enabled, skipping upload/download tests")
            return False
        
        # Test upload
        test_content = f"R2 connection test - {datetime.now().isoformat()}".encode()
        test_file = io.BytesIO(test_content)
        test_key = f"connection_test_{int(datetime.now().timestamp())}.txt"
        
        print(f"📤 Testing upload: {test_key}")
        upload_success = storage.upload_file(test_file, test_key, 'text/plain')
        
        if upload_success:
            print("✅ Upload successful")
        else:
            print("❌ Upload failed")
            return False
        
        # Test download
        print(f"📥 Testing download: {test_key}")
        downloaded_path = storage.download_file(test_key)
        
        if downloaded_path and os.path.exists(downloaded_path):
            with open(downloaded_path, 'rb') as f:
                downloaded_content = f.read()
            
            if downloaded_content == test_content:
                print("✅ Download successful - content matches")
                # Clean up downloaded file
                os.remove(downloaded_path)
            else:
                print("❌ Download failed - content mismatch")
                return False
        else:
            print("❌ Download failed")
            return False
        
        # Clean up test file
        print(f"🧹 Cleaning up test file")
        if storage.delete_file(test_key):
            print("✅ Cleanup successful")
        else:
            print("⚠️  Cleanup failed (test file may still exist)")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload/download test failed: {e}")
        return False

def check_application_integration():
    """Check if the main application can use R2"""
    print("\n🔗 Checking Application Integration")
    print("-" * 40)
    
    try:
        from storage_service import upload_receipt, upload_csv, get_file_path
        import io
        
        # Test receipt upload function
        print("📄 Testing receipt upload function...")
        test_receipt = io.BytesIO(b"Test receipt content")
        success, path = upload_receipt(test_receipt, "test_receipt.jpg")
        
        if success:
            print(f"✅ Receipt upload function works")
            print(f"   Storage path: {path}")
            
            # Test file retrieval
            local_path = get_file_path(path)
            if local_path:
                print(f"✅ File retrieval works")
                # Clean up if it's a temp file
                if local_path.startswith('/tmp/'):
                    from storage_service import cleanup_temp_file
                    cleanup_temp_file(local_path)
            else:
                print(f"❌ File retrieval failed")
                return False
        else:
            print(f"❌ Receipt upload function failed")
            return False
        
        # Test CSV upload function
        print("📊 Testing CSV upload function...")
        test_csv = io.BytesIO(b"Date,Amount,Description\n2024-01-01,25.00,Test")
        success, path = upload_csv(test_csv, "test_transactions.csv")
        
        if success:
            print(f"✅ CSV upload function works")
            print(f"   Storage path: {path}")
        else:
            print(f"❌ CSV upload function failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Application integration test failed: {e}")
        return False

def main():
    """Main status check function"""
    print("🌩️  Cloudflare R2 Connection Status Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Load environment variables if .env exists
    if os.path.exists('.env'):
        try:
            from dotenv import load_dotenv
            load_dotenv('.env')
            print("📁 Loaded environment variables from .env file")
        except ImportError:
            print("⚠️  python-dotenv not available, using system environment variables")
    
    # Run all checks
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Storage Service", check_storage_service),
        ("Bucket Access", test_bucket_access),
        ("Upload/Download", test_upload_download),
        ("Application Integration", check_application_integration)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 R2 Connection Status Summary")
    print("-" * 50)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("-" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - R2 is properly connected!")
        print("\nYour application is ready to use Cloudflare R2 storage.")
    else:
        print("⚠️  SOME CHECKS FAILED - R2 connection has issues")
        print("\nTroubleshooting steps:")
        print("1. Verify your R2 credentials in environment variables")
        print("2. Check that your R2 bucket exists and is accessible")
        print("3. Ensure your access key has read/write permissions")
        print("4. See CLOUDFLARE_R2_SETUP.md for detailed setup instructions")
    
    print(f"\nFor more detailed testing, run: python test_r2_connection.py")

if __name__ == "__main__":
    main()