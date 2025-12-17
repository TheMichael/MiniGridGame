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
    """Register a new user account.
    ---
    tags:
      - Authentication
    summary: Register a new user
    description: Create a new user account. The first registered user automatically becomes an admin.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        description: User registration data
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: player1
              minLength: 3
              maxLength: 50
            email:
              type: string
              format: email
              example: player1@example.com
            password:
              type: string
              format: password
              minLength: 6
              example: securepassword123
    responses:
      200:
        description: Registration successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            user:
              $ref: '#/definitions/User'
      400:
        description: Invalid input data
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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
    """Authenticate user and create session.
    ---
    tags:
      - Authentication
    summary: User login
    description: Authenticate a user and create a session cookie.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        description: Login credentials
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: player1
            password:
              type: string
              format: password
              example: securepassword123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            user:
              $ref: '#/definitions/User'
      400:
        description: Missing credentials
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Invalid credentials or inactive account
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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
    """Clear user session and logout.
    ---
    tags:
      - Authentication
    summary: User logout
    description: Clear the user's session cookie and log them out.
    produces:
      - application/json
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
    """
    logout_user()
    return jsonify({'success': True})


@auth_bp.route('/me', methods=['GET'])
def get_current_user_info():
    """Get current user information.
    ---
    tags:
      - Authentication
    summary: Get current user
    description: Retrieve information about the currently authenticated user.
    produces:
      - application/json
    security:
      - SessionAuth: []
    responses:
      200:
        description: User information retrieved successfully
        schema:
          type: object
          properties:
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: player1
                total_score:
                  type: integer
                  example: 500
                games_played:
                  type: integer
                  example: 10
                best_score:
                  type: integer
                  example: 100
                created_at:
                  type: string
                  format: date-time
                is_admin:
                  type: boolean
                  example: false
      401:
        description: Not authenticated
        schema:
          $ref: '#/definitions/Error'
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'total_score': user.total_score,
            'games_played': user.games_played,
            'best_score': user.best_score,
            'created_at': user.created_at.isoformat(),
            'is_admin': user.is_admin
        }
    })


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset link.
    ---
    tags:
      - Authentication
    summary: Request password reset
    description: Request a password reset link to be sent via email. For security, always returns success even if the user doesn't exist.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        description: Email or username for password reset
        schema:
          type: object
          required:
            - identifier
          properties:
            identifier:
              type: string
              example: player1@example.com
              description: User's email address or username
    responses:
      200:
        description: Password reset request processed (always returns success for security)
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: If the account exists, a reset link has been sent to your email.
      400:
        description: Missing identifier
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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
    """Reset password using token.
    ---
    tags:
      - Authentication
    summary: Reset password
    description: Reset a user's password using a valid reset token received via email.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        description: Reset token and new password
        schema:
          type: object
          required:
            - token
            - password
          properties:
            token:
              type: string
              example: abc123def456ghi789
              description: Password reset token from email
            password:
              type: string
              format: password
              minLength: 6
              example: newsecurepassword123
              description: New password (minimum 6 characters)
    responses:
      200:
        description: Password reset successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Password reset successfully!
      400:
        description: Invalid input or expired token
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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