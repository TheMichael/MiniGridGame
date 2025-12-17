#!/usr/bin/env python3
"""
Check what users exist in the database.
"""
from app import create_app
from database.models import User

def check_users():
    """List all users in the database."""
    app = create_app()
    with app.app_context():
        users = User.query.all()

        print(f"\n{'='*60}")
        print(f"Total users in database: {User.query.count()}")
        print(f"{'='*60}\n")

        if not users:
            print("❌ No users found in database!")
            return

        for i, user in enumerate(users, 1):
            print(f"{i}. Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Admin: {'✅ Yes' if user.is_admin else '❌ No'}")
            print(f"   Active: {'✅ Yes' if user.is_active else '❌ No'}")
            print(f"   Created: {user.created_at}")
            print(f"   Games played: {user.games_played}")
            print(f"   Total score: {user.total_score}")
            print()

if __name__ == '__main__':
    check_users()
