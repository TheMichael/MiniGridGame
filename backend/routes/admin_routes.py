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
    """Get admin dashboard statistics.
    ---
    tags:
      - Admin
    summary: Get dashboard statistics
    description: Retrieve comprehensive statistics for the admin dashboard including user counts, game counts, and top players.
    produces:
      - application/json
    security:
      - SessionAuth: []
    responses:
      200:
        description: Statistics retrieved successfully
        schema:
          type: object
          properties:
            overview:
              type: object
              properties:
                total_users:
                  type: integer
                  example: 100
                active_users:
                  type: integer
                  example: 95
                total_games:
                  type: integer
                  example: 1000
                total_score:
                  type: integer
                  example: 50000
                recent_games:
                  type: integer
                  example: 150
                  description: Games played in the last 7 days
                recent_users:
                  type: integer
                  example: 10
                  description: Users registered in the last 7 days
            agent_stats:
              type: object
              properties:
                ddqn_games:
                  type: integer
                  example: 600
                d3qn_games:
                  type: integer
                  example: 400
            top_players:
              type: array
              items:
                $ref: '#/definitions/User'
      401:
        description: Not authenticated
        schema:
          $ref: '#/definitions/Error'
      403:
        description: Admin access required
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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
    """Get paginated list of users.
    ---
    tags:
      - Admin
    summary: Get all users
    description: Retrieve a paginated list of all users with optional search filtering.
    produces:
      - application/json
    security:
      - SessionAuth: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number for pagination
      - name: per_page
        in: query
        type: integer
        default: 50
        description: Number of users per page
      - name: search
        in: query
        type: string
        description: Search query to filter users by username or email
    responses:
      200:
        description: Users retrieved successfully
        schema:
          type: object
          properties:
            users:
              type: array
              items:
                $ref: '#/definitions/User'
            pagination:
              type: object
              properties:
                page:
                  type: integer
                  example: 1
                pages:
                  type: integer
                  example: 5
                per_page:
                  type: integer
                  example: 50
                total:
                  type: integer
                  example: 245
                has_next:
                  type: boolean
                  example: true
                has_prev:
                  type: boolean
                  example: false
      401:
        description: Not authenticated
        schema:
          $ref: '#/definitions/Error'
      403:
        description: Admin access required
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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
    """Update user properties (admin/active status).
    ---
    tags:
      - Admin
    summary: Update user
    description: Update a user's admin status or active status. Cannot deactivate yourself or remove the last admin.
    consumes:
      - application/json
    produces:
      - application/json
    security:
      - SessionAuth: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user to update
      - name: body
        in: body
        required: true
        description: User properties to update
        schema:
          type: object
          properties:
            is_active:
              type: boolean
              example: true
              description: Whether the user account is active
            is_admin:
              type: boolean
              example: false
              description: Whether the user has admin privileges
    responses:
      200:
        description: User updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: User player1 updated successfully
      400:
        description: Invalid operation (e.g., deactivating yourself, removing last admin)
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Not authenticated
        schema:
          $ref: '#/definitions/Error'
      403:
        description: Admin access required
        schema:
          $ref: '#/definitions/Error'
      404:
        description: User not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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
    """Get paginated list of game results.
    ---
    tags:
      - Admin
    summary: Get all games
    description: Retrieve a paginated list of all game results across all users.
    produces:
      - application/json
    security:
      - SessionAuth: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number for pagination
      - name: per_page
        in: query
        type: integer
        default: 50
        description: Number of games per page
    responses:
      200:
        description: Games retrieved successfully
        schema:
          type: object
          properties:
            games:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  username:
                    type: string
                    example: player1
                  agent_type:
                    type: string
                    example: DDQN
                  prediction:
                    type: integer
                    example: 50
                  actual_steps:
                    type: integer
                    example: 48
                  succeeded:
                    type: boolean
                    example: true
                  score:
                    type: integer
                    example: 100
                  timestamp:
                    type: string
                    format: date-time
                  gif_url:
                    type: string
                    example: /video/run_abc123.gif
            pagination:
              type: object
              properties:
                page:
                  type: integer
                  example: 1
                pages:
                  type: integer
                  example: 20
                per_page:
                  type: integer
                  example: 50
                total:
                  type: integer
                  example: 1000
                has_next:
                  type: boolean
                  example: true
                has_prev:
                  type: boolean
                  example: false
      401:
        description: Not authenticated
        schema:
          $ref: '#/definitions/Error'
      403:
        description: Admin access required
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
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