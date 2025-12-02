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
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-only-for-local-development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))

    # Base URL configuration (for email links, absolute URLs, etc.)
    # In production, set BASE_URL env var (e.g., https://your-app.onrender.com)
    BASE_URL = os.environ.get('BASE_URL', f'http://{HOST}:{PORT}')

    # CORS configuration - additional allowed origins (comma-separated)
    # In production, set ALLOWED_ORIGINS env var (e.g., https://your-app.onrender.com)
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '').split(',')

    # File storage paths
    # IMPORTANT: static/ folder is mounted as persistent disk in production
    STATIC_FOLDER = BACKEND_DIR / 'static'
    VIDEO_FOLDER = STATIC_FOLDER / 'videos'
    MODEL_FOLDER = PROJECT_ROOT / 'models'
    FRONTEND_FOLDER = PROJECT_ROOT / 'frontend'

    # Database configuration
    # CRITICAL: Database is stored in static/ folder so it persists with Render disk mount
    # This ensures user data survives deployments and server restarts
    DATABASE_PATH = STATIC_FOLDER / "minigrid_game.db"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
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

    def __init__(self):
        super().__init__()
        # Validate SECRET_KEY is set in production
        if not os.environ.get('SECRET_KEY'):
            raise ValueError(
                "SECRET_KEY environment variable must be set in production!\n"
                "Generate one with: python3 -c \"import secrets; print(secrets.token_hex(32))\""
            )
        # Warn if using default dev key
        if self.SECRET_KEY == 'dev-secret-key-only-for-local-development':
            raise ValueError(
                "Cannot use default SECRET_KEY in production!\n"
                "Set SECRET_KEY environment variable."
            )


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