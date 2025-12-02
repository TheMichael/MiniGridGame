#!/usr/bin/env python3
"""
Static routes for AI Agent Galaxy.
Extracted from original app.py - handles frontend serving and static files.
"""
import os
from flask import Blueprint, send_from_directory, send_file, request, current_app
from services.auth_service import get_current_user
from database.models import PasswordResetToken

static_bp = Blueprint('static', __name__)


@static_bp.route('/')
def index():
    """Serve main frontend page."""
    return send_from_directory(current_app.config['FRONTEND_FOLDER'], 'index.html')


@static_bp.route('/favicon.ico')
def favicon():
    """Serve robot emoji favicon as SVG."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <text y="80" font-size="80">🤖</text>
    </svg>"""
    from flask import Response
    return Response(svg, mimetype='image/svg+xml')


@static_bp.route('/admin')
def admin_dashboard():
    """Serve admin dashboard page."""
    user = get_current_user()
    if not user or not user.is_admin:
        return "Access denied. Admin privileges required.", 403
    return send_from_directory(current_app.config['FRONTEND_FOLDER'], 'admin.html')


@static_bp.route('/reset-password')
def reset_password_page():
    """Serve password reset page with token validation."""
    token = request.args.get('token', '')
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    valid_token = reset_token and reset_token.is_valid
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Reset Password - Neural Navigator</title></head>
    <body>
        <h1>Reset Password</h1>
        {"<p>Invalid or expired token</p>" if not valid_token else
         f'<form><input type="password" placeholder="New password" id="pwd"><button onclick="resetPwd()">Reset</button></form>'}
        <script>
        function resetPwd() {{
            fetch('/api/reset-password', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{token: '{token}', password: document.getElementById('pwd').value}})
            }}).then(r => r.json()).then(d => alert(d.message || d.error));
        }}
        </script>
    </body>
    </html>
    """
    return html


@static_bp.route('/video/<filename>')
def serve_video(filename):
    """Serve video/GIF files."""
    video_path = os.path.join(current_app.config['VIDEO_FOLDER'], filename)
    if os.path.exists(video_path):
        if filename.endswith('.gif'):
            return send_file(video_path, mimetype='image/gif')
        elif filename.endswith('.mp4'):
            return send_file(video_path, mimetype='video/mp4')
        else:
            return "Unsupported file format", 400
    else:
        return "File not found", 404


@static_bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(current_app.config['STATIC_FOLDER'], filename)


# Error handlers
@static_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return "Page not found", 404


@static_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors."""
    return "Access forbidden", 403