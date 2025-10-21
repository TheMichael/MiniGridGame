#!/usr/bin/env python3
"""
Quick Delete All Users - Simple Version
"""

import sqlite3
import os

def quick_delete():
    db_path = os.path.join(os.path.dirname(__file__), "minigrid_game.db")
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count users before deletion
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]

        print(f"Found {user_count} users")

        if user_count == 0:
            print("No users to delete!")
            return
        
        response = input(f"Delete all {user_count} users? (yes/no): ")
        
        if response.lower() == 'yes':
            # Delete in order to respect foreign keys
            cursor.execute("DELETE FROM password_reset_token")
            cursor.execute("DELETE FROM game_result") 
            cursor.execute("DELETE FROM user")

            conn.commit()
            print("All users deleted!")
            print("Restart your app to create a fresh admin user.")
        else:
            print("Cancelled")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_delete()