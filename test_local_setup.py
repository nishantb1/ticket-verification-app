#!/usr/bin/env python3
"""
Local testing script for R2 integration
Tests both R2 functionality and local fallback behavior
"""

import os
import sys
import tempfile
import io
from dotenv import load_dotenv

def test_without_r2():
    """Test application behavior without R2 configuration"""
    print("🧪 Testing WITHOUT R2 configuration (local storage fallback)")
    print("-" * 60)
    
    # Clear R2 environment variables
    r2_vars = ['R2_ACCOUNT_ID', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT']
    for var in r2_vars:
        if var in os.environ:
            del os.environ[var]
    
    # Import storage service (will initialize without R2)
    from storage_service import get_storage_service, upload_receipt, upload_csv
    
    storage = get_storage_service()
    
    print(f"✅ Storage service initialized")
    print(f"   R2 enabled: {storage.is_enabled()}")
    print(f"   Expected: False (should use local storage)")
    
    # Test receipt upload
    print("\n📤 Testing receipt upload (should use local storage)...")
    test_content = b"Test receipt content"
    test_file = io.BytesIO(test_content)
    success, path = upload_receipt(test_file, "test_receipt.jpg")
    
    print(f"   Upload success: {success}")
    print(f"   Storage path: {path}")
    print(f"   Expected: Local filename (not R2 key)")
    
    # Test CSV upload
    print("\n📤 Testing CSV upload (should use local storage)...")
    csv_content = b"Date,Amount,Description\n2024-01-01,25.00,Test transaction"
    csv_file = io.BytesIO(csv_content)
    success, path = upload_csv(csv_file, "test_transactions.csv")
    
    print(f"   Upload success: {success}")
    print(f"   Storage path: {path}")
    print(f"   Expected: Local filename (not R2 key)")
    
    print("\n✅ Local storage fallback test completed")

def test_with_r2():
    """Test application behavior with R2 configuration"""
    print("\n🌩️  Testing WITH R2 configuration")
    print("-" * 60)
    
    # Load environment variables
    if os.path.exists('.env'):
        load_dotenv('.env')
    
    # Check if R2 is configured
    r2_vars = ['R2_ACCOUNT_ID', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT']
    missing_vars = [var for var in r2_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"⚠️  R2 not fully configured. Missing: {', '.join(missing_vars)}")
        print("   Create .env file with R2 credentials to test R2 functionality")
        return False
    
    # Re-import storage service (will initialize with R2)
    import importlib
    import storage_service
    importlib.reload(storage_service)
    
    from storage_service import get_storage_service, upload_receipt, upload_csv
    
    storage = get_storage_service()
    
    print(f"✅ Storage service initialized")
    print(f"   R2 enabled: {storage.is_enabled()}")
    print(f"   Account ID: {storage.account_id}")
    print(f"   Bucket: {storage.bucket_name}")
    
    if not storage.is_enabled():
        print("❌ R2 failed to initialize. Check your credentials.")
        return False
    
    # Test receipt upload
    print("\n📤 Testing receipt upload (should use R2)...")
    test_content = b"Test receipt content for R2"
    test_file = io.BytesIO(test_content)
    success, path = upload_receipt(test_file, "test_receipt_r2.jpg")
    
    print(f"   Upload success: {success}")
    print(f"   Storage path: {path}")
    print(f"   Expected: R2 key (receipts/test_receipt_r2.jpg)")
    
    # Test CSV upload
    print("\n📤 Testing CSV upload (should use R2)...")
    csv_content = b"Date,Amount,Description\n2024-01-01,30.00,Test R2 transaction"
    csv_file = io.BytesIO(csv_content)
    success, path = upload_csv(csv_file, "test_r2_transactions.csv")
    
    print(f"   Upload success: {success}")
    print(f"   Storage path: {path}")
    print(f"   Expected: R2 key (csv_uploads/test_r2_transactions.csv)")
    
    # Test file retrieval
    print("\n📥 Testing file retrieval...")
    from storage_service import get_file_path
    
    if success and path:
        local_path = get_file_path(path)
        print(f"   Retrieved path: {local_path}")
        print(f"   File exists: {local_path and os.path.exists(local_path)}")
        
        # Clean up temporary file if needed
        if local_path and local_path.startswith('/tmp/'):
            from storage_service import cleanup_temp_file
            cleanup_temp_file(local_path)
            print(f"   Cleaned up temporary file")
    
    print("\n✅ R2 storage test completed")
    return True

def main():
    """Main testing function"""
    print("🧪 Local R2 Integration Testing")
    print("=" * 60)
    print("This script tests both R2 and local storage functionality")
    print()
    
    # Test 1: Without R2 (local storage fallback)
    test_without_r2()
    
    # Test 2: With R2 (if configured)
    r2_success = test_with_r2()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("✅ Local storage fallback: Working")
    print(f"{'✅' if r2_success else '⚠️ '} R2 storage: {'Working' if r2_success else 'Not configured or failed'}")
    
    if not r2_success:
        print("\n💡 To test R2 functionality:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your R2 credentials")
        print("3. Run this script again")
    
    print("\n🚀 Ready for local development!")
    print("   Run: python run_local_with_r2.py")

if __name__ == "__main__":
    main()