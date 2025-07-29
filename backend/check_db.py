import sqlite3
import os

def check_database():
    """Check the database schema"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tickets.db')
    
    print(f"Checking database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check order_table schema
        cursor.execute("PRAGMA table_info(order_table)")
        columns = cursor.fetchall()
        
        print("\n=== ORDER_TABLE SCHEMA ===")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - Default: {col[4]}")
        
        # Check if phone column exists
        column_names = [col[1] for col in columns]
        if 'phone' in column_names:
            print("\n✅ Phone column exists in order_table")
        else:
            print("\n❌ Phone column missing from order_table")
            
        # Check wave table schema
        cursor.execute("PRAGMA table_info(wave)")
        wave_columns = cursor.fetchall()
        
        print("\n=== WAVE TABLE SCHEMA ===")
        for col in wave_columns:
            print(f"  {col[1]} ({col[2]}) - Default: {col[4]}")
        
        # Check current data
        cursor.execute("SELECT COUNT(*) FROM order_table")
        order_count = cursor.fetchone()[0]
        print(f"\nCurrent orders in database: {order_count}")
        
        cursor.execute("SELECT COUNT(*) FROM wave")
        wave_count = cursor.fetchone()[0]
        print(f"Current waves in database: {wave_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database() 