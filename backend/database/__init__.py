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

            # Create default admin if no users exist
            if User.query.count() == 0:
                create_default_admin()
                app.logger.info("Default admin created!")
                app.logger.warning("PLEASE CHANGE DEFAULT ADMIN PASSWORD IMMEDIATELY!")

        except Exception as e:
            app.logger.error(f"Database initialization error: {e}")
            raise


def create_default_admin():
    """Create default admin user if none exists."""
    from .models import User
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        last_login=datetime.utcnow()
    )
    db.session.add(admin)
    db.session.commit()