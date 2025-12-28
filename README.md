# Neural Navigator

**Gamifying AI to make reinforcement learning accessible and engaging.**

A full-stack web application where users compete by predicting AI agent performance in navigation challenges. Players watch pre-trained deep learning agents solve complex mazes and earn points based on prediction accuracy.

**Live Demo:** [neural-navigator.onrender.com](https://neural-navigator.onrender.com) | **API Docs:** [Swagger](https://neural-navigator.onrender.com/api/docs)

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-green) ![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red)

---

## Why I Built This

Reinforcement learning is powerful but intimidating for non-technical users. I wanted to:
- **Make AI tangible**: Turn abstract ML concepts into an interactive experience
- **Solve the "black box" problem**: Let users observe and predict agent behavior in real-time
- **Build something production-ready**: Full authentication, admin tools, API documentation, and deployment

This project demonstrates end-to-end product development: from identifying a user need to shipping a scalable, secure web application.

---

## What It Does

Users compete in a prediction game powered by two pre-trained reinforcement learning agents:

1. **Choose an AI agent** (DDQN or D3QN)
2. **Predict performance** (number of steps to complete a 6-room maze, or predict failure)
3. **Watch the AI navigate** (visual GIF replay of the episode)
4. **Earn points** based on prediction accuracy (100 pts for perfect, 50 for close, 0 for way off)
5. **Compete on leaderboards** and track personal stats

---

## Key Features

**For Users:**
- Real-time AI agent visualization with GIF playback
- Persistent score tracking and leaderboards
- Secure authentication with password reset
- Responsive design (mobile-friendly)

**For Admins:**
- User management dashboard
- Game analytics and statistics
- Bulk operations (activate/deactivate users)

**For Developers:**
- Full REST API with Swagger documentation
- Modular architecture (routes, services, models)
- Docker support for easy deployment
- Comprehensive security (PBKDF2 hashing, CSRF protection, SQL injection prevention)

---

## Tech Stack

**Backend:**
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **PyTorch** - Running pre-trained neural networks
- **Gymnasium (MiniGrid)** - Reinforcement learning environment
- **SQLite** - Database (production uses PostgreSQL)

**Frontend:**
- **Vanilla JavaScript** - Modular, framework-free architecture
- **HTML5/CSS3** - Responsive design with custom components

**AI/ML:**
- **DDQN** (Double Deep Q-Network) - Fast, aggressive navigation
- **D3QN** (Dueling Double DQN) - Strategic, robust generalization
- Pre-trained on 10,000+ episodes using shaped reward functions

**DevOps:**
- **Docker** - Containerization
- **Render** - Cloud deployment
- **GitHub Actions** - CI/CD (optional)

---

## Quick Start

### Prerequisites
- Python 3.11+
- 2GB+ free disk space (for PyTorch)

### Installation

**Windows:**
```bash
git clone https://github.com/TheMichael/MiniGridGame.git
cd MiniGridGame
.\run.bat  # Auto-setup: venv, dependencies, and server
```

**Mac/Linux:**
```bash
git clone https://github.com/TheMichael/MiniGridGame.git
cd MiniGridGame
./run.sh  # Auto-setup: venv, dependencies, and server
```

**Manual Setup:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend && python app.py
```

Visit **http://localhost:5000** to play. First registered user becomes admin.

---

## How to Play

1. **Register/Login** - Create an account (first user = admin)
2. **Choose Agent** - DDQN (faster) or D3QN (smarter)
3. **Predict Steps** - Enter 1-120 or predict failure
4. **Watch AI Navigate** - See the GIF replay of the episode
5. **Earn Points**:
   - Perfect (0 steps off): **100 pts**
   - Close (1-10 off): **50 pts**
   - Far (11-20 off): **25 pts**
   - Correct failure: **50 pts**

---

## Project Structure

```
MiniGridGame/
├── backend/
│   ├── ai/                    # RL agents and environment
│   │   ├── agents/            # DDQN and D3QN implementations
│   │   ├── environment.py     # MiniGrid setup
│   │   └── game_runner.py     # Episode execution
│   ├── database/              # SQLAlchemy models
│   │   └── models/            # User, Game, Auth tables
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic (auth, scoring, game)
│   ├── utils/                 # Logging, validation, file management
│   ├── app.py                 # Application entry point
│   └── openapi.yaml           # Swagger API specification
├── frontend/
│   ├── assets/css/            # Modular stylesheets
│   ├── index.html             # Main game interface
│   └── admin.html             # Admin dashboard
├── models/                    # Pre-trained PyTorch weights
│   ├── DDQN_policy_net.pth
│   └── D3QN_policy_net.pth
└── README.md
```

---

## API Documentation

Access the **Swagger UI** at:
- **Local:** [http://localhost:5000/api/docs](http://localhost:5000/api/docs)
- **Production:** [https://neural-navigator.onrender.com/api/docs](https://neural-navigator.onrender.com/api/docs)

**Key Endpoints:**
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Authenticate user
- `POST /api/game/play` - Run AI agent and calculate score
- `GET /api/game/history` - Fetch user's game history
- `GET /api/game/leaderboard` - Global leaderboard
- `GET /api/admin/users` - Admin: list all users

---

## How the AI Works

The agents use **deep reinforcement learning** to navigate a 6-room MiniGrid maze:

**Training Phase** (pre-training, not in this repo):
- Agent plays 10,000+ episodes via trial and error
- Receives rewards for good moves (+5 for doors, -4 for walls)
- Neural network learns optimal navigation policy

**Inference Phase** (this project):
- Loads pre-trained weights from `models/` directory
- Agent uses learned policy to navigate new maze layouts
- No additional learning occurs during gameplay

**DDQN vs D3QN:**
- **DDQN**: Single Q-network, faster decisions, more aggressive
- **D3QN**: Dueling architecture (state value + action advantages), better generalization

Both use **Convolutional Neural Networks** to process visual maze input.

---

## Development Tools

**Database Management:**
```bash
python backend/view_db.py         # View database contents
python backend/populate_db.py     # Add sample data (10 users, 100 games)
python backend/quick_delete.py    # Reset database
```

**Virtual Environment:**
```bash
# Activate
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# Deactivate
deactivate
```

**Configuration:**
Edit `backend/config.py` for database, session, and environment settings.

---

## Security Features

- **Password Hashing**: PBKDF2-SHA256 via Werkzeug
- **Session Management**: Secure, HttpOnly cookies (24-hour expiration)
- **CSRF Protection**: SameSite cookie attribute
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **Password Reset**: Cryptographically secure tokens with expiration
- **Admin Authorization**: Role-based access control

---

## Deployment

**Docker:**
```bash
docker-compose up --build
```

**Production (Render):**
- Deploy via GitHub integration
- Set environment variables (DATABASE_URL, SECRET_KEY, etc.)
- Uses Gunicorn WSGI server

---

## What I Learned

**Product:**
- Balancing technical complexity with user experience
- Designing gamification mechanics that drive engagement
- Building admin tools for operational efficiency

**Technical:**
- Integrating pre-trained ML models into production web apps
- Architecting scalable Flask applications with clean separation of concerns
- Implementing secure authentication and session management
- Deploying containerized Python apps to cloud platforms

**Challenges Solved:**
- **GIF generation performance**: Optimized rendering to <2 seconds per episode
- **Agent consistency**: Ensured reproducible results via seeded environments
- **User engagement**: Designed scoring system to reward both accuracy and participation

---

## Future Enhancements

- [ ] Multi-agent tournaments (users pick agents to compete head-to-head)
- [ ] Custom maze builder for user-generated challenges
- [ ] Real-time multiplayer predictions
- [ ] Agent performance analytics dashboard
- [ ] Mobile app (React Native or Flutter)

---

## License

MIT License - see LICENSE file for details

---

## Contact

**Michael Ohayon**
Technical Product Manager | Digital Health
[LinkedIn](https://www.linkedin.com/in/michael-ohayon-511163272/) | [Email](mailto:Michmich6@gmail.com)

---

**⭐ If you find this project useful, consider starring the repo!**
