#!/usr/bin/env python3
"""
AI Agent Galaxy - Main Application Entry Point
Refactored from monolithic structure to clean modular architecture.
"""
import os
from flask import Flask
from flask_cors import CORS

from config import Config
from database import init_db
from utils.logging_config import setup_logging


def create_app(config_class=Config):
    """Application factory pattern for creating Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup logging first
    setup_logging(app)
    
    # FIXED: Proper CORS configuration for session cookies
    CORS(app, 
         supports_credentials=True,
         origins=['http://localhost:5000', 'http://127.0.0.1:5000'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize database
    init_db(app)
    
    # Register routes
    from routes import register_routes
    register_routes(app)
    
    # Ensure required directories exist
    _ensure_directories(app)
    
    app.logger.info("AI Agent Galaxy application initialized successfully")
    return app


def _ensure_directories(app):
    """Ensure all required directories exist."""
    directories = [
        app.config['VIDEO_FOLDER'],
        app.config['MODEL_FOLDER'],
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        app.logger.debug(f"Directory ensured: {directory}")


def main():
    """Main entry point for the application."""
    app = create_app()
    
    # Print startup information (temporarily simplified)
    print("AI Agent Galaxy - Refactored Backend Starting...")
    print(f"Running on: http://{app.config['HOST']}:{app.config['PORT']}")
    print("All routes registered and ready!")
    
    try:
        app.run(
            debug=app.config['DEBUG'],
            host=app.config['HOST'],
            port=app.config['PORT']
        )
    except KeyboardInterrupt:
        app.logger.info("Server stopped by user")
    except Exception as e:
        app.logger.error(f"Server error: {e}")
        raise
    finally:
        app.logger.info("Thanks for playing AI Agent Galaxy!")


if __name__ == '__main__':
    main()