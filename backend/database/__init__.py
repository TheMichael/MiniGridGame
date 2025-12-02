#!/usr/bin/env python3
"""
Database initialization for AI Agent Galaxy.
Extracted from original app.py - handles SQLAlchemy setup.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """Initialize database with the Flask app."""
    db.init_app(app)
    
    # Import models to ensure they're registered
    from .models import User, GameResult, PasswordResetToken
    
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully!")

            # Note: First user to register will automatically become admin
            # See auth_routes.py register() function
            if User.query.count() == 0:
                app.logger.info("No users exist. First registered user will become admin.")

        except Exception as e:
            app.logger.error(f"Database initialization error: {e}")
            raise