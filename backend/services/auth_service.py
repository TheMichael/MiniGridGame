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
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.is_active:
            return user
    return None


def admin_required():
    """Check if current user has admin privileges."""
    user = get_current_user()
    return user and user.is_admin


def login_user(user):
    """Log in a user by setting session."""
    session.permanent = True  # ADDED: Make session permanent
    session['user_id'] = user.id
    user.last_login = db.func.now()
    db.session.commit()


def logout_user():
    """Log out current user by clearing session."""
    session.pop('user_id', None)
    session.permanent = False  # ADDED: Reset session to non-permanent


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