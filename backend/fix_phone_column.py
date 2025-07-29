import sqlite3
import os

def fix_phone_column():
    """Add the missing phone column to order_table"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tickets.db')
    
    print(f"Connecting to database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if phone column exists
        cursor.execute("PRAGMA table_info(order_table)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns in order_table: {column_names}")
        
        if 'phone' not in column_names:
            print("Adding phone column to order_table...")
            cursor.execute("ALTER TABLE order_table ADD COLUMN phone TEXT DEFAULT ''")
            conn.commit()
            print("✅ Phone column added successfully")
        else:
            print("✅ Phone column already exists")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(order_table)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Updated columns in order_table: {column_names}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_phone_column() 