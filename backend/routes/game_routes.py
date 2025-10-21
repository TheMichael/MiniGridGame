#!/usr/bin/env python3
"""
Game routes for AI Agent Galaxy.
Extracted from original app.py - handles game execution and validation.
"""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from database import db
from database.models import GameResult
from services.auth_service import get_current_user
from services.scoring_service import calculate_score, get_score_explanation
from ai import video_of_one_DDQN_episode, video_of_one_D3QN_episode, setup_environment

game_bp = Blueprint('game', __name__)

# Initialize environment once
env = setup_environment()


@game_bp.route('/run-validation', methods=['POST'])
def run_validation():
    """Run AI agent validation and return results."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Must be logged in to play'}), 401
    
    try:
        data = request.get_json()
        agent_type = data.get('agent_type')
        prediction = data.get('prediction')
        
        if agent_type not in ['ddqn', 'd3qn']:
            return jsonify({'error': 'Invalid agent type'}), 400
        
        if not prediction:
            return jsonify({'error': 'Prediction required'}), 400
        
        # Generate unique filename for GIF
        gif_filename = f"run_{uuid.uuid4().hex}.gif"
        gif_path = os.path.join(current_app.config['VIDEO_FOLDER'], gif_filename)
        
        # Run the appropriate agent
        if agent_type == 'ddqn':
            model_path = os.path.join(current_app.config['MODEL_FOLDER'], 'DDQN_policy_net.pth')
            result = video_of_one_DDQN_episode(env, model_path, gif_path)
        else:  # d3qn
            model_path = os.path.join(current_app.config['MODEL_FOLDER'], 'D3QN_policy_net.pth')
            result = video_of_one_D3QN_episode(env, model_path, gif_path)
        
        # Parse results - SIMPLIFIED
        if len(result) == 4:
            total_reward, num_steps, gif_file, steps_log = result
            gif_url = f'/video/{os.path.basename(gif_file)}' if gif_file else None
            gif_filename_final = os.path.basename(gif_file) if gif_file else None
        else:
            total_reward, num_steps, steps_log = result
            gif_url = None
            gif_filename_final = None

        # Calculate results
        ai_agent_succeeded = bool(num_steps < current_app.config['MAX_STEPS'])
        score = calculate_score(prediction, num_steps, ai_agent_succeeded)

        # Save game result - SIMPLIFIED FIELDS
        game_result = GameResult(
            user_id=user.id,
            agent_type=agent_type,
            prediction=int(prediction) if prediction != 'fail' else 0,
            actual_steps=int(num_steps),
            score=int(score),
            gif_filename=gif_filename_final
        )

        db.session.add(game_result)

        # Update user statistics - SIMPLIFIED
        user.total_score += int(score)
        user.games_played += 1

        # Track best score
        if int(score) > user.best_score:
            user.best_score = int(score)

        db.session.commit()

        return jsonify({
            'steps': int(num_steps),
            'succeeded': ai_agent_succeeded,
            'gif_url': gif_url,
            'agent_type': str(agent_type),
            'score': int(score),
            'prediction': str(prediction),
            'user_stats': {
                'total_score': user.total_score,
                'games_played': user.games_played,
                'best_score': user.best_score
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in validation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@game_bp.route('/cleanup-old-videos', methods=['POST'])
def cleanup_old_videos():
    """Clean up old video files to save space."""
    try:
        import glob
        mp4_files = glob.glob(os.path.join(current_app.config['VIDEO_FOLDER'], "*.mp4"))
        removed_count = 0
        
        for mp4_file in mp4_files:
            try:
                os.remove(mp4_file)
                removed_count += 1
            except Exception as e:
                current_app.logger.error(f"Could not remove {mp4_file}: {e}")
        
        return jsonify({
            'success': True,
            'removed_files': removed_count,
            'message': f'Cleaned up {removed_count} old MP4 files'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500