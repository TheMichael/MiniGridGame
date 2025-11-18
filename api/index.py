#!/usr/bin/env python3
"""
Vercel serverless entry point for Neural Navigator.
This file adapts the Flask app to work with Vercel's serverless functions.
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from app import create_app

# Create the Flask app instance
app = create_app()

# This is the handler that Vercel will call
# Vercel's Python runtime expects an 'app' object or a handler function
