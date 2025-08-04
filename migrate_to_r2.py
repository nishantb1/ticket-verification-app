#!/usr/bin/env python3
"""
Migration script to move existing local files to Cloudflare R2
Run this after setting up R2 to migrate existing uploads and CSV files
"""

import os
import sys
import sqlite3
from storage_service import get_storage_service
from app import get_db_path

def migrate_receipts():
    """Migrate receipt files from local uploads/ to R2"""
    print("📤 Migrating receipt files to R2...")
    
    storage = get_storage_service()
    if not storage.is_enabled():
        print("❌ R2 storage not configured. Please set up R2 first.")
        return False
    
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        print("ℹ️  No local uploads directory found, skipping receipt migration")
        return True
    
    migrated_count = 0
    failed_count = 0
    
    # Get all files in uploads directory
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            print(f"  📄 Migrating {filename}...")
            
            # Upload to R2
            r2_key = f"receipts/{filename}"
            success = storage.upload_file_from_path(file_path, r2_key)
            
            if success:
                print(f"    ✅ Uploaded to R2: {r2_key}")
                migrated_count += 1
                
                # Update database to use R2 key
                update_receipt_path_in_db(filename, r2_key)
                
                # Optionally remove local file (uncomment if you want to delete local copies)
                # os.remove(file_path)
                # print(f"    🗑️  Removed local file: {file_path}")
            else:
                print(f"    ❌ Failed to upload: {filename}")
                failed_count += 1
    
    print(f"\n📊 Receipt migration summary:")
    print(f"  ✅ Successfully migrated: {migrated_count} files")
    print(f"  ❌ Failed to migrate: {failed_count} files")
    
    return failed_count == 0

def migrate_csv_files():
    """Migrate CSV files from local csv_uploads/ to R2"""
    print("\n📤 Migrating CSV files to R2...")
    
    storage = get_storage_service()
    if not storage.is_enabled():
        print("❌ R2 storage not configured. Please set up R2 first.")
        return False
    
    csv_dir = 'csv_uploads'
    if not os.path.exists(csv_dir):
        print("ℹ️  No local csv_uploads directory found, skipping CSV migration")
        return True
    
    migrated_count = 0
    failed_count = 0
    
    # Get all files in csv_uploads directory
    for filename in os.listdir(csv_dir):
        file_path = os.path.join(csv_dir, filename)
        if os.path.isfile(file_path) and filename != '.gitkeep':
            print(f"  📄 Migrating {filename}...")
            
            # Upload to R2
            r2_key = f"csv_uploads/{filename}"
            success = storage.upload_file_from_path(file_path, r2_key, 'text/csv')
            
            if success:
                print(f"    ✅ Uploaded to R2: {r2_key}")
                migrated_count += 1
                
                # Update database to use R2 key
                update_csv_path_in_db(filename, r2_key)
                
                # Optionally remove local file (uncomment if you want to delete local copies)
                # os.remove(file_path)
                # print(f"    🗑️  Removed local file: {file_path}")
            else:
                print(f"    ❌ Failed to upload: {filename}")
                failed_count += 1
    
    print(f"\n📊 CSV migration summary:")
    print(f"  ✅ Successfully migrated: {migrated_count} files")
    print(f"  ❌ Failed to migrate: {failed_count} files")
    
    return failed_count == 0

def update_receipt_path_in_db(old_filename, new_r2_key):
    """Update receipt_path in order_table to use R2 key"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE order_table 
            SET receipt_path = ? 
            WHERE receipt_path = ?
        ''', (new_r2_key, old_filename))
        
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        if updated_rows > 0:
            print(f"    📝 Updated {updated_rows} database record(s)")
        
    except Exception as e:
        print(f"    ⚠️  Failed to update database: {e}")

def update_csv_path_in_db(old_filename, new_r2_key):
    """Update filename in csv_uploads table to use R2 key"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE csv_uploads 
            SET filename = ? 
            WHERE filename = ?
        ''', (new_r2_key, old_filename))
        
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        if updated_rows > 0:
            print(f"    📝 Updated {updated_rows} database record(s)")
        
    except Exception as e:
        print(f"    ⚠️  Failed to update database: {e}")

def main():
    """Main migration function"""
    print("🚀 Cloudflare R2 Migration Tool")
    print("=" * 50)
    print("This script will migrate existing local files to Cloudflare R2")
    print("Make sure you have configured R2 environment variables first!")
    print()
    
    # Check if R2 is configured
    storage = get_storage_service()
    if not storage.is_enabled():
        print("❌ Cloudflare R2 is not properly configured.")
        print("Please set up R2 environment variables first:")
        print("  - R2_ACCOUNT_ID")
        print("  - R2_BUCKET_NAME") 
        print("  - R2_ACCESS_KEY_ID")
        print("  - R2_SECRET_ACCESS_KEY")
        print("  - R2_ENDPOINT")
        print("\nSee CLOUDFLARE_R2_SETUP.md for detailed instructions.")
        sys.exit(1)
    
    print("✅ R2 storage is configured and ready")
    print(f"📦 Bucket: {storage.bucket_name}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed with migration? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Migration cancelled.")
        sys.exit(0)
    
    print("\n🚀 Starting migration...")
    
    # Migrate receipts
    receipts_success = migrate_receipts()
    
    # Migrate CSV files
    csv_success = migrate_csv_files()
    
    # Summary
    print("\n" + "=" * 50)
    if receipts_success and csv_success:
        print("🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test your application to ensure files are accessible")
        print("2. If everything works, you can safely delete local files:")
        print("   - rm -rf uploads/*")
        print("   - rm -rf csv_uploads/* (keep .gitkeep)")
        print("3. Monitor R2 usage in Cloudflare dashboard")
    else:
        print("⚠️  Migration completed with some failures.")
        print("Please check the errors above and retry if needed.")
        print("Your application will continue to work with the existing local files.")
    
    print("\nFor support, see CLOUDFLARE_R2_SETUP.md")

if __name__ == "__main__":
    main()