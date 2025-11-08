#!/usr/bin/env python3
"""
Database Import Script for cinda_db
Imports the database_schema.sql file into MySQL
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': 3306
}

def create_database():
    """Create the database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Drop existing database if it exists
        cursor.execute("DROP DATABASE IF EXISTS `cinda_db`")
        print("✅ Dropped existing database (if any)")
        
        # Create new database
        cursor.execute("CREATE DATABASE `cinda_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Created database 'cinda_db'")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def import_schema():
    """Import the database schema"""
    try:
        # Connect to the specific database
        config = DB_CONFIG.copy()
        config['database'] = 'cinda_db'
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Read the schema file
        schema_file = 'database_schema.sql'
        if not os.path.exists(schema_file):
            print(f"❌ Schema file {schema_file} not found")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as file:
            schema_content = file.read()
        
        # Split the content by semicolons to execute individual statements
        statements = []
        current_statement = ""
        in_delimiter_block = False
        
        for line in schema_content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('--') or not line:
                continue
                
            # Handle DELIMITER changes
            if line.startswith('DELIMITER'):
                in_delimiter_block = line != 'DELIMITER ;'
                continue
                
            current_statement += " " + line
            
            # Execute statement when we find a semicolon (and not in delimiter block)
            if line.endswith(';') and not in_delimiter_block:
                if current_statement.strip():
                    try:
                        # Clean up the statement
                        stmt = current_statement.strip()
                        if stmt and not stmt.startswith('--'):
                            cursor.execute(stmt)
                            print(f"✅ Executed: {stmt[:50]}...")
                    except Error as e:
                        print(f"⚠️  Warning executing statement: {e}")
                        print(f"   Statement: {current_statement[:100]}...")
                
                current_statement = ""
        
        # Execute any remaining statement
        if current_statement.strip():
            try:
                cursor.execute(current_statement.strip())
                print(f"✅ Executed final statement")
            except Error as e:
                print(f"⚠️  Warning executing final statement: {e}")
        
        connection.commit()
        print("✅ Schema imported successfully")
        
        # Show table count
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✅ Created {len(tables)} tables")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Error importing schema: {e}")
        return False

def main():
    """Main function"""
    print("🗄️  CI-NDA Database Import")
    print("=" * 40)
    
    if not create_database():
        sys.exit(1)
    
    if not import_schema():
        sys.exit(1)
    
    print("\n🎉 Database import completed successfully!")
    print("\nYou can now:")
    print("1. Start your Flask server: python server.py")
    print("2. Access your webapp at: http://localhost:5000")
    print("3. Register a new account to get started")

if __name__ == "__main__":
    main()