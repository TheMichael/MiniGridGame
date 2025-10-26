# AI Agent Prediction Game

A full-stack web application where users compete by predicting AI agent performance in reinforcement learning navigation tasks. Watch pre-trained Deep Q-Learning agents solve MiniGrid mazes and earn points based on prediction accuracy.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎮 Overview

This project combines **reinforcement learning** with an interactive web game. Players predict how many steps AI agents (DDQN and D3QN) will take to navigate a complex multi-room maze environment, earning points based on accuracy.

### Key Features

- 🤖 **Two Pre-trained RL Agents**: DDQN (Double Deep Q-Network) and D3QN (Dueling Double Deep Q-Network)
- 🎯 **Prediction Challenge**: Guess the number of steps or predict failure
- 🎬 **Visual Replays**: Watch GIF recordings of each AI navigation attempt
- 👤 **User Authentication**: Secure session-based login with password reset
- 📊 **Persistent Statistics**: Track scores, games played, and personal bests
- 🏆 **Leaderboard System**: Compete with other players
- 🔐 **Admin Panel**: User management and game analytics

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip package manager
- 2GB+ free disk space (for PyTorch dependencies)

### Installation

#### Windows

```bash
git clone https://github.com/TheMichael/MiniGridGame.git
cd MiniGridGame
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
python app.py
```

#### Mac/Linux

```bash
git clone https://github.com/TheMichael/MiniGridGame.git
cd MiniGridGame
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python app.py
```

### Access the Application

1. Open your browser and navigate to **http://localhost:5000**
2. Register a new account (first user becomes admin automatically)
3. Select an AI agent and make your prediction
4. Watch the AI navigate and see your score!

### Optional: Sample Data

```bash
cd backend
python populate_db.py  # Creates demo users and game history
```

## 🎲 How to Play

1. **Choose an AI Agent**:
   - **DDQN**: Double Deep Q-Network (faster, more aggressive)
   - **D3QN**: Dueling architecture (more strategic, better generalization)

2. **Make Your Prediction**:
   - Enter the number of steps you think the agent will take (1-120)
   - OR predict the agent will fail (doesn't reach goal in 120 steps)

3. **Watch the Agent Play**:
   - The AI navigates a 6-room MiniGrid maze
   - You'll see a GIF recording of the entire episode

4. **Earn Points Based on Accuracy**:
   - **Perfect** (0 steps off): **100 points** 🏆
   - **Close** (1-10 steps off): **50 points** ✅
   - **Far** (11-20 steps off): **25 points** 📉
   - **Way Off** (21+ steps off): **0 points** ❌
   - **Correct Failure Prediction**: **50 points** 🎯

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **PyTorch** - Running pre-trained neural networks
- **OpenAI Gymnasium** - MiniGrid environment
- **SQLite** - Database (easily replaceable with PostgreSQL)

**Frontend:**
- **Vanilla JavaScript** - No frameworks, modular architecture
- **HTML5/CSS3** - Responsive design
- **Fetch API** - RESTful communication with backend

**AI/ML:**
- **DDQN** - Double Deep Q-Network with CNN architecture
- **D3QN** - Dueling Double Deep Q-Network with value/advantage streams
- **MiniGrid-MultiRoom-N6-v0** - 6-room navigation environment
- **Pre-trained models** - Trained using shaped reward functions

### Project Structure

```
MiniGridGame/
├── backend/
│   ├── ai/                    # AI agents and environment
│   │   ├── agents/
│   │   │   ├── ddqn_agent.py
│   │   │   └── d3qn_agent.py
│   │   ├── environment.py    # MiniGrid setup
│   │   └── game_runner.py    # Episode execution
│   ├── database/             # SQLAlchemy models
│   │   └── models/
│   │       ├── user.py       # User authentication
│   │       ├── game.py       # Game results
│   │       └── auth.py       # Password reset tokens
│   ├── routes/               # API endpoints
│   │   ├── auth_routes.py    # Login, register, logout
│   │   ├── game_routes.py    # Game execution
│   │   └── admin_routes.py   # Admin panel
│   ├── services/             # Business logic
│   │   ├── auth_service.py   # Session management
│   │   ├── scoring_service.py # Score calculation
│   │   └── game_service.py   # Game coordination
│   ├── utils/                # Utilities
│   ├── app.py               # Application entry point
│   ├── config.py            # Configuration management
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── assets/
│   │   ├── css/             # Modular stylesheets
│   │   └── js/              # Modular JavaScript
│   ├── index.html           # Main game interface
│   ├── admin.html           # Admin dashboard
│   └── reset-password.html  # Password reset page
├── models/
│   ├── DDQN_policy_net.pth  # Pre-trained DDQN weights
│   └── D3QN_policy_net.pth  # Pre-trained D3QN weights
└── README.md
```

## 🧠 How the AI Works

### Reinforcement Learning Basics

The agents learned to navigate through **trial and error**:

1. **Training Phase** (not in this repo):
   - Agent plays 10,000+ practice episodes
   - Receives rewards for good moves (+5 for opening doors)
   - Receives penalties for bad moves (-4 for hitting walls)
   - Neural network learns optimal navigation strategy

2. **Inference Phase** (what this project does):
   - Loads pre-trained neural network weights
   - Agent uses learned policy to navigate new mazes
   - No further learning occurs during gameplay

### DDQN vs D3QN

**DDQN (Double Deep Q-Network):**
- Single neural network predicts Q-values for each action
- Reduces overestimation bias compared to standard DQN
- Faster decision-making

**D3QN (Dueling Double Deep Q-Network):**
- Splits into two streams: state value + action advantages
- Better at distinguishing when actions matter
- More stable in complex environments

Both use **Convolutional Neural Networks** to process visual input from the maze.

## 🛠️ Development

### Database Management Tools

```bash
# View current database contents
python backend/view_db.py

# Populate with sample data (10 users, 100 games)
python backend/populate_db.py

# Reset database (delete all data)
python backend/quick_delete.py
```

### Virtual Environment

**Activate:**
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Deactivate:**
```bash
deactivate
```

### Configuration

Edit `backend/config.py` for:
- Database settings
- Session configuration
- File storage paths
- Environment-specific settings (dev/production)

## 📊 Database Schema

### User Table
- `id`, `username`, `email`, `password_hash`
- `total_score`, `games_played`, `best_score`
- `is_admin`, `is_active`
- `created_at`, `last_login`

### GameResult Table
- `user_id` (foreign key)
- `agent_type` (ddqn or d3qn)
- `prediction`, `actual_steps`, `score`
- `gif_filename`, `timestamp`

### PasswordResetToken Table
- `user_id`, `token`, `created_at`, `expires_at`, `used`

## 🔐 Security Features

- **Password Hashing**: PBKDF2-SHA256 via Werkzeug
- **Session Management**: Secure, HttpOnly cookies with 24-hour expiration
- **CSRF Protection**: SameSite cookie attribute
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **Password Reset**: Cryptographically secure tokens with expiration

## 🚧 Known Limitations

- **SQLite**: Not ideal for high concurrency (easily upgradeable to PostgreSQL)
- **Synchronous AI Execution**: Game runs block the server (could add task queue)
- **Local Storage Only**: Videos stored on server (could use cloud storage)
- **No Real-time Features**: No WebSocket support for live multiplayer

## 🎯 Future Improvements

- [ ] Migrate to PostgreSQL for production
- [ ] Add Celery task queue for async AI execution
- [ ] Implement WebSocket for real-time multiplayer predictions
- [ ] Add analytics dashboard with charts
- [ ] Create API documentation with Swagger
- [ ] Add unit tests and integration tests
- [ ] Deploy to cloud platform (AWS, GCP, or Azure)
- [ ] Implement caching with Redis

## 📝 License

MIT License - feel free to use this project for learning or portfolio purposes.

## 🙏 Acknowledgments

- **OpenAI Gymnasium** - MiniGrid environment
- **PyTorch** - Deep learning framework
- **Flask** - Web framework
- Pre-trained models developed during university reinforcement learning coursework

---

**Built with ❤️ as a portfolio project demonstrating full-stack development and ML integration**
