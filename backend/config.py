#!/usr/bin/env python3
"""
Configuration management for AI Agent Galaxy.
Extracted from original app.py - centralizes all configuration settings.
"""
import os
from pathlib import Path
from datetime import timedelta


class Config:
    """Base configuration class with all application settings."""
    
    # Application paths
    BACKEND_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = BACKEND_DIR.parent
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database configuration
    DATABASE_PATH = BACKEND_DIR / "minigrid_game.db"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # File storage paths
    STATIC_FOLDER = PROJECT_ROOT / 'static'
    VIDEO_FOLDER = STATIC_FOLDER / 'videos'
    MODEL_FOLDER = PROJECT_ROOT / 'models'
    FRONTEND_FOLDER = PROJECT_ROOT / 'frontend'
    
    # Game settings
    MAX_STEPS = 120
    
    # Security settings - FIXED for session cookies
    SESSION_COOKIE_SECURE = False  # Set to True only in HTTPS production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None  # Allow localhost
    SESSION_COOKIE_PATH = '/'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_PERMANENT = True
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Never secure in development


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Always secure in production
    SESSION_COOKIE_SAMESITE = 'Strict'


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_map.get(config_name, DevelopmentConfig)