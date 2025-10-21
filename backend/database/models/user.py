#!/usr/bin/env python3
"""
User model for AI Agent Galaxy.
Extracted from original app.py - handles user authentication and statistics.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db


class User(db.Model):
    """User model with authentication and game statistics."""
    
    __tablename__ = 'user'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Game statistics - SIMPLIFIED
    total_score = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Integer, default=0)

    # User status
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    games = db.relationship('GameResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses."""
        return {
            'id': self.id,
            'username': self.username,
            'total_score': self.total_score,
            'games_played': self.games_played,
            'best_score': self.best_score,
            'is_admin': self.is_admin
        }
    
    def __repr__(self):
        return f'<User {self.username}>'