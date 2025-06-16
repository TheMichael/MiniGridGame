#!/usr/bin/env python3
"""
Email service for AI Agent Galaxy.
Extracted from original app.py - handles password reset emails.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_password_reset_email(user, token):
    """Send password reset email to user."""
    try:
        if not current_app.config['MAIL_USERNAME']:
            print(f"🔑 Password reset token for {user.username}: {token}")
            return True
            
        msg = MIMEMultipart()
        msg['From'] = current_app.config['MAIL_USERNAME']
        msg['To'] = user.email
        msg['Subject'] = "🌌 AI Agent Galaxy - Password Reset"
        
        reset_link = f"http://localhost:5000/reset-password?token={token}"
        body = f"""
        Greetings, Galaxy Commander {user.username}! 🚀
        
        You requested a password reset for your AI Agent Galaxy account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 24 hours for security.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.starttls()
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        print(f"🔑 Password reset token for {user.username}: {token}")
        return False