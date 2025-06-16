#!/usr/bin/env python3
"""
Authentication model for AI Agent Galaxy.
Extracted from original app.py - handles password reset tokens.
"""
from datetime import datetime, timedelta
from .. import db


class PasswordResetToken(db.Model):
    """Password reset token model for secure password recovery."""
    
    __tablename__ = 'password_reset_token'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    
    # Token lifecycle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='reset_tokens')
    
    def __init__(self, **kwargs):
        super(PasswordResetToken, self).__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    @property
    def is_expired(self):
        """Check if token has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        return not self.used and not self.is_expired
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token[:8]}...>'