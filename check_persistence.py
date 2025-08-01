#!/usr/bin/env python3
"""
Check database persistence on Render
"""

import os
import sqlite3
from datetime import datetime

def check_database_persistence():
    """Check if database persists across deployments"""
    
    # Check environment
    db_path = os.environ.get('DATABASE_PATH', 'tickets.db')
    print(f"Database path: {db_path}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if database exists
    if os.path.exists(db_path):
        print(f"✅ Database exists at: {db_path}")
        
        # Check database size
        size = os.path.getsize(db_path)
        print(f"Database size: {size} bytes")
        
        # Check database contents
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Count orders
            cursor.execute("SELECT COUNT(*) FROM order_table")
            order_count = cursor.fetchone()[0]
            print(f"Total orders in database: {order_count}")
            
            # Check recent orders
            cursor.execute("SELECT id, name, status, created_at FROM order_table ORDER BY created_at DESC LIMIT 5")
            recent_orders = cursor.fetchall()
            
            print("\nRecent orders:")
            for order in recent_orders:
                print(f"  ID: {order[0]}, Name: {order[1]}, Status: {order[2]}, Created: {order[3]}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error reading database: {e}")
    else:
        print(f"❌ Database does not exist at: {db_path}")
    
    # Check mount point
    mount_path = "/var/data"
    if os.path.exists(mount_path):
        print(f"✅ Mount point exists: {mount_path}")
        
        # List contents
        try:
            contents = os.listdir(mount_path)
            print(f"Mount point contents: {contents}")
        except Exception as e:
            print(f"❌ Error listing mount point: {e}")
    else:
        print(f"❌ Mount point does not exist: {mount_path}")
    
    # Create a test file to check persistence
    test_file = os.path.join(os.path.dirname(db_path), 'persistence_test.txt')
    try:
        with open(test_file, 'w') as f:
            f.write(f"Test file created at: {datetime.now()}\n")
        print(f"✅ Created test file: {test_file}")
    except Exception as e:
        print(f"❌ Error creating test file: {e}")

if __name__ == "__main__":
    check_database_persistence()