#!/usr/bin/env python3
"""
Admin routes for AI Agent Galaxy.
Extracted from original app.py - handles admin panel functionality.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from database import db
from database.models import User, GameResult
from services.auth_service import get_current_user, admin_required

admin_bp = Blueprint('admin', __name__)


def require_admin():
    """Decorator function to require admin access."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    if not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    return None


@admin_bp.route('/stats', methods=['GET'])
def admin_stats():
    """Get admin dashboard statistics."""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_games = GameResult.query.count()
        total_score = db.session.query(db.func.sum(User.total_score)).scalar() or 0
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_games = GameResult.query.filter(GameResult.timestamp >= week_ago).count()
        recent_users = User.query.filter(User.created_at >= week_ago).count()
        
        ddqn_games = GameResult.query.filter_by(agent_type='ddqn').count()
        d3qn_games = GameResult.query.filter_by(agent_type='d3qn').count()
        
        top_players = User.query.order_by(User.total_score.desc()).limit(10).all()
        top_players_data = [{
            'id': user.id,
            'username': user.username,
            'total_score': user.total_score,
            'games_played': user.games_played,
            'best_score': user.best_score,
            'created_at': user.created_at.isoformat()
        } for user in top_players]
        
        return jsonify({
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'total_games': total_games,
                'total_score': total_score,
                'recent_games': recent_games,
                'recent_users': recent_users
            },
            'agent_stats': {
                'ddqn_games': ddqn_games,
                'd3qn_games': d3qn_games
            },
            'top_players': top_players_data
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch statistics'}), 500


@admin_bp.route('/users', methods=['GET'])
def admin_users():
    """Get paginated list of users."""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        if search:
            query = query.filter(
                (User.username.contains(search)) | 
                (User.email.contains(search))
            )
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in users.items:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'total_score': user.total_score,
                'games_played': user.games_played,
                'best_score': user.best_score,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def admin_update_user(user_id):
    """Update user properties (admin/active status)."""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        
        current_user = get_current_user()
        if user.id == current_user.id and 'is_active' in data and not data['is_active']:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        if 'is_admin' in data:
            if not data['is_admin'] and User.query.filter_by(is_admin=True).count() <= 1:
                return jsonify({'error': 'Cannot remove the last admin'}), 400
            user.is_admin = bool(data['is_admin'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.username} updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to update user'}), 500


@admin_bp.route('/games', methods=['GET'])
def admin_games():
    """Get paginated list of game results."""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        games = GameResult.query.order_by(GameResult.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        games_data = []
        for game in games.items:
            games_data.append({
                'id': game.id,
                'username': game.user.username,
                'agent_type': game.agent_type.upper(),
                'prediction': game.prediction,
                'actual_steps': game.actual_steps,
                'succeeded': game.succeeded,
                'score': game.score,
                'total_reward': game.total_reward,
                'timestamp': game.timestamp.isoformat(),
                'gif_url': f'/video/{game.gif_filename}' if game.gif_filename else None
            })
        
        return jsonify({
            'games': games_data,
            'pagination': {
                'page': games.page,
                'pages': games.pages,
                'per_page': games.per_page,
                'total': games.total,
                'has_next': games.has_next,
                'has_prev': games.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch games'}), 500