import os
import sys
from flask import Flask, request, jsonify, send_file, send_from_directory, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import secrets
import smtplib
from email.mime.text import MIMEText  # Fixed: Changed from MimeText to MIMEText
from email.mime.multipart import MIMEMultipart  # Fixed: Changed from MimeMultipart to MIMEMultipart

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all the necessary libraries
import gymnasium as gym
import minigrid
from minigrid.wrappers import RGBImgObsWrapper, RGBImgPartialObsWrapper, ImgObsWrapper
import numpy as np
import torch
import torch.nn as nn
import random
import cv2
import imageio

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration - Paths configured for backend folder structure
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BACKEND_DIR, "minigrid_game.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db = SQLAlchemy(app)

# Folder paths relative to project root
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')
VIDEO_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'videos')
MODEL_FOLDER = os.path.join(PROJECT_ROOT, 'models')
FRONTEND_FOLDER = os.path.join(PROJECT_ROOT, 'frontend')

# Ensure directories exist
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# Constants
MAX_STEPS = 120
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ================================
# DATABASE MODELS
# ================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    good_predictions = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    games = db.relationship('GameResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def ai_success_rate(self):
        if self.games_played == 0:
            return 0
        return round((self.games_won / self.games_played) * 100, 1)
    
    @property
    def prediction_accuracy(self):
        if self.games_played == 0:
            return 0
        return round((self.good_predictions / self.games_played) * 100, 1)
    
    @property
    def average_score_per_game(self):
        if self.games_played == 0:
            return 0
        return round(self.total_score / self.games_played, 1)

class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_type = db.Column(db.String(10), nullable=False)
    prediction = db.Column(db.Integer, nullable=False)
    actual_steps = db.Column(db.Integer, nullable=False)
    succeeded = db.Column(db.Boolean, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_reward = db.Column(db.Float, nullable=False)
    gif_filename = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    steps_log = db.Column(db.Text, nullable=True)

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='reset_tokens')
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.used and not self.is_expired

# ================================
# HELPER FUNCTIONS
# ================================

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.is_active:
            return user
    return None

def admin_required():
    user = get_current_user()
    return user and user.is_admin

def send_password_reset_email(user, token):
    try:
        if not app.config['MAIL_USERNAME']:
            print(f"🔑 Password reset token for {user.username}: {token}")
            return True
            
        msg = MIMEMultipart()  # Fixed: Changed from MimeMultipart to MIMEMultipart
        msg['From'] = app.config['MAIL_USERNAME']
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
        
        msg.attach(MIMEText(body, 'plain'))  # Fixed: Changed from MimeText to MIMEText
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        print(f"🔑 Password reset token for {user.username}: {token}")
        return False

# Preprocessing functions
def preprocess_state(state):
    state = cv2.cvtColor(state, cv2.COLOR_RGB2GRAY)
    state = np.expand_dims(state, axis=0)
    return state.astype(np.float32)

# Neural Networks
class DoubleDQNNetwork(nn.Module):
    def __init__(self, input_shape, num_actions):
        super(DoubleDQNNetwork, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )
        conv_out_size = self.get_conv_out(input_shape)
        self.fc = nn.Sequential(
            nn.Linear(conv_out_size, 512),
            nn.ReLU(),
            nn.Linear(512, num_actions)
        )

    def get_conv_out(self, shape):
        o = self.conv(torch.zeros(1, *shape))
        return int(np.prod(o.size()))

    def forward(self, x):
        conv_out = self.conv(x)
        conv_out = conv_out.view(conv_out.size()[0], -1)
        return self.fc(conv_out)

class DuelingQNetwork(nn.Module):
    def __init__(self, input_shape, action_size, seed):
        super(DuelingQNetwork, self).__init__()
        self.seed = torch.manual_seed(seed)
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )
        self.conv_output_size = self._get_conv_output_size(input_shape)
        self.fc_value = nn.Sequential(
            nn.Linear(self.conv_output_size, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )
        self.fc_advantage = nn.Sequential(
            nn.Linear(self.conv_output_size, 512),
            nn.ReLU(),
            nn.Linear(512, action_size)
        )

    def _get_conv_output_size(self, shape):
        o = self.conv_layers(torch.zeros(1, *shape))
        return int(np.prod(o.size()))

    def forward(self, state):
        x = self.conv_layers(state)
        x = x.view(x.size(0), -1)
        value = self.fc_value(x)
        advantage = self.fc_advantage(x)
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        return q_values

# Agent Classes
class DDQNAgent:
    def __init__(self, input_shape, num_actions):
        self.num_actions = num_actions
        self.device = device
        self.allowed_actions = [a for a in range(num_actions) if a not in [3, 4, 6]]
        self.allowed_mask = torch.zeros(num_actions, dtype=torch.bool, device=self.device)
        for a in self.allowed_actions:
            self.allowed_mask[a] = True
        self.policy_net = DoubleDQNNetwork(input_shape, num_actions).to(self.device)
        self.policy_net.eval()

    def select_action(self, state, current_eps):
        if random.random() < current_eps:
            return random.choice(self.allowed_actions)
        else:
            with torch.no_grad():
                state = state.to(self.device)
                q_values = self.policy_net(state)
                q_values[0, ~self.allowed_mask] = -float("inf")
                return int(q_values.max(1)[1].item())

class D3QNAgent:
    def __init__(self, input_shape, action_size, seed):
        self.state_size = input_shape
        self.action_size = action_size
        self.seed = random.seed(seed)
        self.valid_actions = [0, 1, 2, 5]
        self.qnetwork_local = DuelingQNetwork(input_shape, action_size, seed).to(device)

    def act(self, state, eps=0.):
        state = torch.from_numpy(state).float().unsqueeze(0).to(device)
        self.qnetwork_local.eval()
        with torch.no_grad():
            action_values = self.qnetwork_local(state)
            mask = torch.ones_like(action_values) * float('-inf')
            for a in self.valid_actions:
                if a < action_values.shape[1]:
                    mask[0, a] = 0
            masked_action_values = action_values + mask
        self.qnetwork_local.train()
        
        if random.random() > eps:
            return np.argmax(masked_action_values.cpu().data.numpy())
        else:
            return random.choice(self.valid_actions)

# Reward functions
def shape_reward(step_count, max_steps, done, truncated, states_list, current_state, actions_list):
    reward = -0.5
    if actions_list[-1] == 5 and not np.array_equal(states_list[-1], current_state):
        reward += 5
    if actions_list[-1] == 5 and np.array_equal(states_list[-1], current_state):
        reward -= 3
    if len(actions_list) >= 2 and actions_list[-1] == 5 and actions_list[-2] == 5:
        reward -= 3
    if np.array_equal(states_list[-1], current_state):
        reward -= 4
    if done:
        reward += 80 + 10*(1 - 0.9 * (step_count / max_steps))
    if truncated or step_count == max_steps:
        reward -= 10
    return reward

def compute_reward(step_count, max_steps, done, truncated, states_list, current_state, actions_list):
    reward = -0.5
    if actions_list[-1] == 5 and not np.array_equal(states_list[-1], current_state):
        reward += 8
    if actions_list[-1] == 5 and np.array_equal(states_list[-1], current_state):
        reward -= 3
    if len(actions_list) >= 2 and actions_list[-1] == 5 and actions_list[-2] == 5:
        reward -= 3
    if np.array_equal(states_list[-1], current_state):
        reward -= 4
    if done:
        reward += 25 + 10*(1 - 0.9 * (step_count / max_steps))
    if truncated or step_count == max_steps:
        reward -= 10
    return reward

# Video generation functions
def video_of_one_DDQN_episode(env, policy_network_path, gif_filename):
    obs, _ = env.reset()
    obs = preprocess_state(obs)
    input_shape = obs.shape
    num_actions = env.action_space.n
    policy_net = DoubleDQNNetwork(input_shape, num_actions)
    
    try:
        policy_net.load_state_dict(torch.load(policy_network_path, map_location=device))
    except FileNotFoundError:
        return 0, 120, []

    policy_net.to(device)
    policy_net.eval()
    agent = DDQNAgent(input_shape, num_actions)
    agent.policy_net = policy_net
    
    total_reward = 0
    frames = []
    steps_log = []
    obs, _ = env.reset()
    processed = preprocess_state(obs)
    state = torch.tensor(processed, dtype=torch.float32).unsqueeze(0)
    episode_states = []
    episode_actions = []

    for t in range(MAX_STEPS):
        action = agent.select_action(state, 0)
        episode_states.append(state)
        episode_actions.append(action)
        
        next_obs, _, done, truncated, _ = env.step(action)
        reward = shape_reward(t, MAX_STEPS, done, truncated, episode_states, next_obs, episode_actions)
        total_reward += reward
        
        step_info = {
            'step': int(t + 1),
            'action': int(action),
            'reward': float(reward),
            'done': bool(done),
            'truncated': bool(truncated),
            'result': 'Goal reached! 🎯' if done else ('Max steps reached' if truncated else 'Continuing...')
        }
        steps_log.append(step_info)
        
        processed_next = preprocess_state(next_obs)
        state = torch.tensor(processed_next, dtype=torch.float32).unsqueeze(0)

        try:
            frame = env.render()
            if frame.shape[-1] == 3:
                frames.append(frame)
        except Exception as e:
            print(f"Rendering error: {e}")
        
        if done or truncated:
            break

    try:
        imageio.mimsave(gif_filename, frames, duration=0.1, loop=0)
    except Exception as e:
        print(f"GIF save error: {e}")
        return float(total_reward), int(t + 1), None, steps_log
    
    return float(total_reward), int(t + 1), gif_filename, steps_log

def video_of_one_D3QN_episode(env, policy_network_path, gif_filename):
    trained_agent = D3QNAgent((1, 56, 56), env.action_space.n, seed=0)
    
    try:
        trained_agent.qnetwork_local.load_state_dict(torch.load(policy_network_path, map_location=device))
    except FileNotFoundError:
        return 0, 120, []
    
    trained_agent.qnetwork_local.eval()
    score = 0
    frames = []
    steps_log = []
    state, _ = env.reset()
    state = preprocess_state(state)
    episode_states = []
    episode_actions = []

    for t in range(MAX_STEPS):
        action = trained_agent.act(state, 0.0)
        episode_states.append(state)
        episode_actions.append(action)

        current_state, _, done, truncated, _ = env.step(action)
        current_state = preprocess_state(current_state)
        reward = compute_reward(t, MAX_STEPS, done, truncated, episode_states, current_state, episode_actions)
        
        step_info = {
            'step': int(t + 1),
            'action': int(action),
            'reward': float(reward),
            'done': bool(done),
            'truncated': bool(truncated),
            'result': 'Goal reached! 🎯' if done else ('Max steps reached' if truncated else 'Continuing...')
        }
        steps_log.append(step_info)

        state = current_state
        score += reward
        
        try:
            frame = env.render()
            if frame.shape[-1] == 3:
                frames.append(frame)
        except Exception as e:
            print(f"Rendering error: {e}")
        
        if done or truncated:
            break

    try:
        imageio.mimsave(gif_filename, frames, duration=0.1, loop=0)
    except Exception as e:
        print(f"GIF save error: {e}")
        return float(score), int(t + 1), None, steps_log

    return float(score), int(t + 1), gif_filename, steps_log

# Environment setup
def setup_environment():
    ENV_NAME = "MiniGrid-MultiRoom-N6-v0"
    env = gym.make(ENV_NAME, render_mode="rgb_array", highlight=False)
    env = RGBImgPartialObsWrapper(env)
    env = ImgObsWrapper(env)
    return env

env = setup_environment()

# Scoring function
def calculate_score(prediction, actual_steps, succeeded):
    if prediction == 'fail':
        return 3 if not succeeded else 0
    
    try:
        predicted_steps = int(prediction)
        difference = abs(predicted_steps - actual_steps)
        
        if difference == 0:
            base_score = 10
        elif difference <= 5:
            base_score = 8
        elif difference <= 10:
            base_score = 5
        else:
            base_score = 0
        
        # Risk-reward multiplier system
        if 35 <= predicted_steps <= 55:
            multiplier = 0.4
        elif 30 <= predicted_steps <= 65:
            multiplier = 0.7
        elif predicted_steps <= 29:
            multiplier = 0.1
        elif 66 <= predicted_steps <= 85:
            multiplier = 1.5
        elif predicted_steps >= 86:
            multiplier = 2.0
        else:
            multiplier = 1.0
        
        final_score = int(base_score * multiplier)
        return max(final_score, 1) if base_score > 0 else 0
        
    except ValueError:
        return 0

# ================================
# ROUTES
# ================================

@app.route('/')
def index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/admin')
def admin_dashboard():
    user = get_current_user()
    if not user or not user.is_admin:
        return "Access denied. Admin privileges required.", 403
    return send_from_directory(FRONTEND_FOLDER, 'admin.html')

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email_or_username = data.get('identifier', '').strip()
        
        if not email_or_username:
            return jsonify({'error': 'Email or username required'}), 400
        
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if not user:
            return jsonify({'success': True, 'message': 'If the account exists, a reset link has been sent.'})
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_token)
        db.session.commit()
        send_password_reset_email(user, token)
        
        return jsonify({
            'success': True,
            'message': 'If the account exists, a reset link has been sent to your email.'
        })
        
    except Exception as e:
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        
        if not token or not new_password or len(new_password) < 6:
            return jsonify({'error': 'Valid token and password (6+ chars) required'}), 400
        
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token or not reset_token.is_valid:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        user = reset_token.user
        user.password_hash = generate_password_hash(new_password)
        reset_token.used = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/reset-password')
def reset_password_page():
    token = request.args.get('token', '')
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    valid_token = reset_token and reset_token.is_valid
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Reset Password - AI Agent Galaxy</title></head>
    <body>
        <h1>🔐 Reset Password</h1>
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

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email required'}), 400
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            last_login=datetime.utcnow()
        )
        
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'total_score': user.total_score,
                'games_played': user.games_played,
                'prediction_accuracy': user.prediction_accuracy,
                'is_admin': user.is_admin
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account has been deactivated'}), 401
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'total_score': user.total_score,
                'games_played': user.games_played,
                'prediction_accuracy': user.prediction_accuracy,
                'average_score': user.average_score_per_game,
                'is_admin': user.is_admin
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/me', methods=['GET'])
def get_current_user_info():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'total_score': user.total_score,
            'games_played': user.games_played,
            'games_won': user.games_won,
            'prediction_accuracy': user.prediction_accuracy,
            'ai_success_rate': user.ai_success_rate,
            'average_score': user.average_score_per_game,
            'created_at': user.created_at.isoformat(),
            'is_admin': user.is_admin
        }
    })

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
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
            'prediction_accuracy': user.prediction_accuracy,
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

@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
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
                'prediction_accuracy': user.prediction_accuracy,
                'ai_success_rate': user.ai_success_rate,
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

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def admin_update_user(user_id):
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
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

@app.route('/api/admin/games', methods=['GET'])
def admin_games():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
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

@app.route('/api/run-validation', methods=['POST'])
def run_validation():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Must be logged in to play'}), 401
    
    try:
        data = request.get_json()
        agent_type = data.get('agent_type')
        prediction = data.get('prediction')
        
        gif_filename = f"run_{uuid.uuid4().hex}.gif"
        gif_path = os.path.join(VIDEO_FOLDER, gif_filename)
        
        if agent_type == 'ddqn':
            model_path = os.path.join(MODEL_FOLDER, 'DDQN_policy_net.pth')
            result = video_of_one_DDQN_episode(env, model_path, gif_path)
        elif agent_type == 'd3qn':
            model_path = os.path.join(MODEL_FOLDER, 'D3QN_policy_net.pth')
            result = video_of_one_D3QN_episode(env, model_path, gif_path)
        else:
            return jsonify({'error': 'Invalid agent type'}), 400
        
        if len(result) == 4:
            total_reward, num_steps, gif_file, steps_log = result
            gif_url = f'/video/{os.path.basename(gif_file)}' if gif_file else None
            gif_filename_final = os.path.basename(gif_file) if gif_file else None
        else:
            total_reward, num_steps, steps_log = result
            gif_url = None
            gif_filename_final = None
        
        ai_agent_succeeded = bool(num_steps < MAX_STEPS)
        score = calculate_score(prediction, num_steps, ai_agent_succeeded)
        is_good_prediction = score > 0
        
        game_result = GameResult(
            user_id=user.id,
            agent_type=agent_type,
            prediction=int(prediction),
            actual_steps=int(num_steps),
            succeeded=ai_agent_succeeded,
            score=int(score),
            total_reward=float(total_reward),
            gif_filename=gif_filename_final,
            steps_log=str(steps_log)
        )
        
        db.session.add(game_result)
        
        user.total_score += int(score)
        user.games_played += 1
        if ai_agent_succeeded:
            user.games_won += 1
        if is_good_prediction:
            user.good_predictions += 1
        
        db.session.commit()
        
        return jsonify({
            'steps': int(num_steps),
            'succeeded': ai_agent_succeeded,
            'total_reward': float(total_reward),
            'gif_url': gif_url,
            'agent_type': str(agent_type),
            'score': int(score),
            'prediction': str(prediction),
            'steps_log': steps_log,
            'user_stats': {
                'total_score': user.total_score,
                'games_played': user.games_played,
                'prediction_accuracy': user.prediction_accuracy,
                'ai_success_rate': user.ai_success_rate
            }
        })
        
    except Exception as e:
        print(f"Error in validation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/video/<filename>')
def serve_video(filename):
    video_path = os.path.join(VIDEO_FOLDER, filename)
    if os.path.exists(video_path):
        if filename.endswith('.gif'):
            return send_file(video_path, mimetype='image/gif')
        elif filename.endswith('.mp4'):
            return send_file(video_path, mimetype='video/mp4')
        else:
            return "Unsupported file format", 400
    else:
        return "File not found", 404

@app.route('/api/cleanup-old-videos', methods=['POST'])
def cleanup_old_videos():
    try:
        import glob
        mp4_files = glob.glob(os.path.join(VIDEO_FOLDER, "*.mp4"))
        removed_count = 0
        
        for mp4_file in mp4_files:
            try:
                os.remove(mp4_file)
                removed_count += 1
            except Exception as e:
                print(f"Could not remove {mp4_file}: {e}")
        
        return jsonify({
            'success': True,
            'removed_files': removed_count,
            'message': f'Cleaned up {removed_count} old MP4 files'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("📊 Database tables created successfully!")
            
            # Create default admin if no users exist
            if User.query.count() == 0:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    last_login=datetime.utcnow()
                )
                db.session.add(admin)
                db.session.commit()
                print("🔑 Default admin created! Username: admin, Password: admin123")
                print("⚠️  PLEASE CHANGE DEFAULT ADMIN PASSWORD IMMEDIATELY!")
            
            print(f"🔍 Backend directory: {BACKEND_DIR}")
            print(f"🔍 Project root: {PROJECT_ROOT}")
            print(f"🔍 Database location: {os.path.abspath(os.path.join(BACKEND_DIR, 'minigrid_game.db'))}")
            print(f"🔍 Static folder: {STATIC_FOLDER}")
            print(f"🔍 Video folder: {VIDEO_FOLDER}")
            print(f"🔍 Model folder: {MODEL_FOLDER}")
            print(f"🔍 Frontend folder: {FRONTEND_FOLDER}")
                            
        except Exception as e:
            print(f"❌ Database creation error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("🚀 Starting Enhanced MiniGrid Prediction Game Server...")
    print("="*60)
    print("📍 Make sure you have the trained model files:")
    print("   📁 models/DDQN_policy_net.pth")
    print("   📁 models/D3QN_policy_net.pth")
    print()
    print("🌐 ACCESS POINTS:")
    print("   🎮 Main Game: http://localhost:5000")
    print("   👑 Admin Panel: http://localhost:5000/admin")
    print("   🔐 Password Reset: http://localhost:5000/reset-password")
    print()
    print("📊 DATA STORAGE:")
    print(f"   📁 GIFs saved to: {VIDEO_FOLDER}")
    print(f"   💾 Database stored in: {os.path.join(BACKEND_DIR, 'minigrid_game.db')}")
    print()
    print("🔑 DEFAULT ADMIN ACCESS:")
    print("   👤 Username: admin")
    print("   🔒 Password: admin123")
    print("   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
    print()
    print("✨ FEATURES ENABLED:")
    print("   🔐 Password reset functionality")
    print("   👑 Complete admin panel")
    print("   🎯 Enhanced scoring system")
    print("   🎬 Real-time GIF generation")
    print("   📈 User analytics & statistics")
    print("   🛡️  Account security & management")
    
    # Email configuration check
    if not app.config['MAIL_USERNAME']:
        print()
        print("📧 EMAIL CONFIGURATION:")
        print("   ⚠️  Email not configured for password reset")
        print("   🔧 To enable email functionality:")
        print("      Set MAIL_USERNAME environment variable")
        print("      Set MAIL_PASSWORD environment variable")
        print("   💡 Reset tokens will be printed to console instead")
    else:
        print()
        print("📧 EMAIL CONFIGURATION:")
        print("   ✅ Email configured for password reset")
        print(f"   📮 SMTP Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    
    print("\n" + "="*60)
    print("🎮 Ready to play! Users must register/login to start!")
    print("="*60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Thanks for playing AI Agent Galaxy!")