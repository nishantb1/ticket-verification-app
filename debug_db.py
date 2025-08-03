#!/usr/bin/env python3
"""
Debug script to check database persistence on Render
"""
import os
import sqlite3
import sys

def check_database():
    """Check database status and contents"""
    print("=== Database Debug Information ===")
    
    # Check environment variables
    db_path = os.environ.get('DATABASE_PATH', 'tickets.db')
    print(f"DATABASE_PATH: {db_path}")
    
    # Check if database file exists
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"Database exists: {db_path}")
        print(f"Database size: {size} bytes")
        
        # Check database contents
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            # Check order count
            cursor.execute("SELECT COUNT(*) FROM order_table")
            order_count = cursor.fetchone()[0]
            print(f"Orders in database: {order_count}")
            
            # Check admin users
            cursor.execute("SELECT COUNT(*) FROM admin_users")
            admin_count = cursor.fetchone()[0]
            print(f"Admin users: {admin_count}")
            
            # Check waves
            cursor.execute("SELECT COUNT(*) FROM wave")
            wave_count = cursor.fetchone()[0]
            print(f"Waves: {wave_count}")
            
            conn.close()
            
        except Exception as e:
            print(f"Error reading database: {e}")
    else:
        print(f"Database does not exist: {db_path}")
    
    # Check directory permissions
    db_dir = os.path.dirname(db_path)
    if db_dir:
        print(f"Database directory: {db_dir}")
        print(f"Directory exists: {os.path.exists(db_dir)}")
        if os.path.exists(db_dir):
            print(f"Directory writable: {os.access(db_dir, os.W_OK)}")
    
    print("=== End Debug Information ===")

if __name__ == "__main__":
    check_database() 