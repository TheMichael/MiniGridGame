#!/usr/bin/env python3
"""
Quick script to make a user an admin.
Usage: python make_admin.py <username>
"""
import sys
from app import create_app
from database import db
from database.models import User

def make_admin(username):
    """Make a user an admin."""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found!")
            print(f"\nAvailable users:")
            for u in User.query.all():
                print(f"  - {u.username} (Admin: {u.is_admin})")
            return False

        if user.is_admin:
            print(f"✓ User '{username}' is already an admin!")
            return True

        user.is_admin = True
        db.session.commit()
        print(f"✅ User '{username}' is now an admin!")
        return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    success = make_admin(username)
    sys.exit(0 if success else 1)
