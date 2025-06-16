#!/usr/bin/env python3
"""
Routes module for AI Agent Galaxy.
Registers all route blueprints with the Flask app.
"""
from .auth_routes import auth_bp
from .game_routes import game_bp
from .admin_routes import admin_bp
from .static_routes import static_bp


def register_routes(app):
    """Register all route blueprints with the Flask app."""
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(game_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(static_bp)
    
    app.logger.info("🛣️  All routes registered successfully")