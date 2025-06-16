#!/usr/bin/env python3
"""
Logging configuration for AI Agent Galaxy.
Sets up application-wide logging with proper formatting.
"""
import logging
import sys
from pathlib import Path


def setup_logging(app):
    """Setup logging configuration for the application."""
    
    # Get log level from config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Setup file handler (optional)
    if not app.debug:
        log_file = Path(app.config['BACKEND_DIR']) / 'app.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    
    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    
    # Configure other loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    app.logger.info("📝 Logging configuration completed")