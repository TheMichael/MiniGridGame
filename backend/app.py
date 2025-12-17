#!/usr/bin/env python3
"""
AI Agent Galaxy - Main Application Entry Point
Refactored from monolithic structure to clean modular architecture.
"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from config import Config
from database import init_db
from utils.logging_config import setup_logging


def create_app(config_class=Config):
    """Application factory pattern for creating Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup logging first
    setup_logging(app)

    # CORS configuration for session cookies
    # Default origins for local development
    allowed_origins = ['http://localhost:5000', 'http://127.0.0.1:5000']

    # Add production origins from config (set via ALLOWED_ORIGINS env var)
    # Filter out empty strings
    additional_origins = [origin.strip() for origin in app.config['ALLOWED_ORIGINS'] if origin.strip()]
    allowed_origins.extend(additional_origins)

    app.logger.info(f"CORS allowed origins: {allowed_origins}")

    CORS(app,
         supports_credentials=True,
         origins=allowed_origins,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize database
    init_db(app)

    # Configure Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/openapi.yaml'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Neural Navigator API",
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 3,
            'displayRequestDuration': True,
            'filter': True,
            'tryItOutEnabled': True
        }
    )

    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Serve OpenAPI spec
    @app.route('/api/openapi.yaml')
    def openapi_spec():
        """Serve the OpenAPI specification file."""
        return send_from_directory(
            os.path.dirname(os.path.abspath(__file__)),
            'openapi.yaml',
            mimetype='text/yaml'
        )

    app.logger.info("Swagger API documentation initialized at /api/docs")

    # Register routes
    from routes import register_routes
    register_routes(app)
    
    # Ensure required directories exist
    _ensure_directories(app)
    
    app.logger.info("Neural Navigator application initialized successfully")
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
    print("Neural Navigator - Backend Starting...")
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
        app.logger.info("Thanks for playing Neural Navigator!")


if __name__ == '__main__':
    main()