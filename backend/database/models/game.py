#!/usr/bin/env python3
"""
Game result model for AI Agent Galaxy.
Extracted from original app.py - stores individual game outcomes.
"""
from datetime import datetime
from .. import db


class GameResult(db.Model):
    """Game result model storing individual game outcomes."""
    
    __tablename__ = 'game_result'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Game configuration
    agent_type = db.Column(db.String(10), nullable=False)
    
    # Prediction and results - SIMPLIFIED
    prediction = db.Column(db.Integer, nullable=False)
    actual_steps = db.Column(db.Integer, nullable=False)

    # Scoring
    score = db.Column(db.Integer, nullable=False)

    # Media
    gif_filename = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def succeeded(self):
        """Calculate if agent succeeded based on steps (< 120 means success)."""
        return self.actual_steps < 120

    def to_dict(self):
        """Convert game result to dictionary for JSON responses."""
        return {
            'id': self.id,
            'username': self.user.username,
            'agent_type': self.agent_type.upper(),
            'prediction': self.prediction,
            'actual_steps': self.actual_steps,
            'succeeded': self.succeeded,
            'score': self.score,
            'gif_url': f'/video/{self.gif_filename}' if self.gif_filename else None,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<GameResult {self.id}: {self.user.username} - {self.agent_type}>'