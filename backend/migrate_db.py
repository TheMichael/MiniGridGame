#!/usr/bin/env python3
"""
Simple Database Migration for AI Agent Galaxy
Run this script to fix the missing columns error.
"""

import sqlite3
import os
from datetime import datetime

def fix_database():
    """Fix the database by adding missing columns"""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), "minigrid_game.db")
    
    print(f"🔍 Looking for database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database not found! Please run app.py first.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing database schema...")
        
        # Get current columns in user table
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current user table columns: {existing_columns}")
        
        # Add missing columns one by one
        columns_to_add = [
            ("good_predictions", "INTEGER DEFAULT 0"),
            ("games_won", "INTEGER DEFAULT 0"), 
            ("is_active", "BOOLEAN DEFAULT 1"),
            ("last_login", "DATETIME")
        ]
        
        for column_name, column_def in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"⚠️  Could not add {column_name}: {e}")
            else:
                print(f"✓ Column {column_name} already exists")
        
        # Update last_login for existing users
        cursor.execute("UPDATE user SET last_login = created_at WHERE last_login IS NULL")
        
        # Commit changes
        conn.commit()
        print("💾 Database updated successfully!")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(user)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Updated user table columns: {new_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Fixing AI Agent Galaxy Database...")
    print("="*50)
    
    if fix_database():
        print("="*50)
        print("✅ Database fixed! You can now run your app.")
    else:
        print("="*50)
        print("❌ Failed to fix database.")