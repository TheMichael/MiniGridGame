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
    
    # Prediction and results
    prediction = db.Column(db.Integer, nullable=False)
    actual_steps = db.Column(db.Integer, nullable=False)
    succeeded = db.Column(db.Boolean, nullable=False)
    
    # Scoring
    score = db.Column(db.Integer, nullable=False)
    total_reward = db.Column(db.Float, nullable=False)
    
    # Media and logs
    gif_filename = db.Column(db.String(255), nullable=True)
    steps_log = db.Column(db.Text, nullable=True)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
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
            'total_reward': self.total_reward,
            'gif_url': f'/video/{self.gif_filename}' if self.gif_filename else None,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<GameResult {self.id}: {self.user.username} - {self.agent_type}>'