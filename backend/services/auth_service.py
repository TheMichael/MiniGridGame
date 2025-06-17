#!/usr/bin/env python3
"""
Authentication service for AI Agent Galaxy.
Extracted from original app.py - handles authentication logic.
"""
from flask import session
from database import db
from database.models import User


def get_current_user():
    """Get currently logged in user from session."""
    print(f"\n=== GET_CURRENT_USER DEBUG ===")
    print(f"Session data: {dict(session)}")
    print(f"Session permanent: {session.permanent}")
    
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")
    
    if user_id:
        user = User.query.get(user_id)
        print(f"User found in DB: {user}")
        print(f"User active: {user.is_active if user else 'N/A'}")
        if user and user.is_active:
            print(f"Returning user: {user.username}")
            return user
        else:
            print("User not found or inactive")
    else:
        print("No user_id in session")
    
    print(f"==============================\n")
    return None


def admin_required():
    """Check if current user has admin privileges."""
    user = get_current_user()
    return user and user.is_admin


def login_user(user):
    """Log in a user by setting session."""
    print(f"\n=== LOGIN_USER DEBUG ===")
    print(f"Logging in user: {user.username} (ID: {user.id})")
    print(f"Session before login: {dict(session)}")
    print(f"Session permanent before: {session.permanent}")
    
    session.permanent = True  # Make session permanent
    session['user_id'] = user.id
    
    print(f"Session after login: {dict(session)}")
    print(f"Session permanent after: {session.permanent}")
    print(f"Session modified: {session.modified}")
    
    user.last_login = db.func.now()
    db.session.commit()
    
    print(f"User logged in successfully!")
    print(f"========================\n")


def logout_user():
    """Log out current user by clearing session."""
    print(f"\n=== LOGOUT_USER DEBUG ===")
    print(f"Session before logout: {dict(session)}")
    
    session.pop('user_id', None)
    session.permanent = False  # Reset session to non-permanent
    
    print(f"Session after logout: {dict(session)}")
    print(f"=========================\n")


def validate_registration_data(username, email, password):
    """Validate registration data."""
    errors = []
    
    if not username or len(username) < 3:
        errors.append('Username must be at least 3 characters')
    
    if not email or '@' not in email:
        errors.append('Valid email required')
    
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters')
    
    if User.query.filter_by(username=username).first():
        errors.append('Username already exists')
    
    if User.query.filter_by(email=email).first():
        errors.append('Email already registered')
    
    return errors