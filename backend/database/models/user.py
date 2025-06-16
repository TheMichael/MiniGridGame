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
    
    # Game statistics
    total_score = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    good_predictions = db.Column(db.Integer, default=0)
    
    # User status
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    games = db.relationship('GameResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def ai_success_rate(self):
        """Calculate AI agent success rate for this user's games."""
        if self.games_played == 0:
            return 0
        return round((self.games_won / self.games_played) * 100, 1)
    
    @property
    def prediction_accuracy(self):
        """Calculate prediction accuracy percentage."""
        if self.games_played == 0:
            return 0
        return round((self.good_predictions / self.games_played) * 100, 1)
    
    @property
    def average_score_per_game(self):
        """Calculate average score per game."""
        if self.games_played == 0:
            return 0
        return round(self.total_score / self.games_played, 1)
    
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
            'prediction_accuracy': self.prediction_accuracy,
            'ai_success_rate': self.ai_success_rate,
            'average_score': self.average_score_per_game,
            'is_admin': self.is_admin
        }
    
    def __repr__(self):
        return f'<User {self.username}>'