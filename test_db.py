#!/usr/bin/env python3
"""
Quick database connection test for CI-NDA
"""
import mysql.connector
from mysql.connector import Error

# Database configuration (minimal)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'cinda_db',
    'port': 3306
}
def test_connection():
    """Test database connection"""
    try:
        print("🔍 Testing database connection...")
        
        # Create connection without collation
        config = DB_CONFIG.copy()
        connection = mysql.connector.connect(**config)
        
        print("✅ Connection successful!")
        
        # Test charset/collation (use compatible version)
        cursor = connection.cursor()
        cursor.execute("SET NAMES utf8mb4")
        print("✅ Charset set successfully")
        
        # Check if database exists
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"✅ Connected to database: {db_name}")
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Test a simple query
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users table has {user_count} records")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()