#!/usr/bin/env python3
"""
Authentication routes for AI Agent Galaxy.
Extracted from original app.py - handles login, register, logout, password reset.
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from database import db
from database.models import User, PasswordResetToken
from services.auth_service import get_current_user, login_user, logout_user, validate_registration_data
from services.email_service import send_password_reset_email
import secrets

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validate input
        errors = validate_registration_data(username, email, password)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            last_login=datetime.utcnow()
        )
        
        # Make first user an admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and create session."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account has been deactivated'}), 401
        
        # Log in the user
        login_user(user)
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear user session and logout."""
    logout_user()
    return jsonify({'success': True})


@auth_bp.route('/me', methods=['GET'])
def get_current_user_info():
    """Get current user information."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'total_score': user.total_score,
            'games_played': user.games_played,
            'games_won': user.games_won,
            'prediction_accuracy': user.prediction_accuracy,
            'ai_success_rate': user.ai_success_rate,
            'average_score': user.average_score_per_game,
            'created_at': user.created_at.isoformat(),
            'is_admin': user.is_admin
        }
    })


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset link."""
    try:
        data = request.get_json()
        email_or_username = data.get('identifier', '').strip()
        
        if not email_or_username:
            return jsonify({'error': 'Email or username required'}), 400
        
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if not user:
            return jsonify({'success': True, 'message': 'If the account exists, a reset link has been sent.'})
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_token)
        db.session.commit()
        send_password_reset_email(user, token)
        
        return jsonify({
            'success': True,
            'message': 'If the account exists, a reset link has been sent to your email.'
        })
        
    except Exception as e:
        return jsonify({'error': 'Password reset failed'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token."""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        
        if not token or not new_password or len(new_password) < 6:
            return jsonify({'error': 'Valid token and password (6+ chars) required'}), 400
        
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token or not reset_token.is_valid:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        user = reset_token.user
        user.password_hash = generate_password_hash(new_password)
        reset_token.used = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': 'Password reset failed'}), 500