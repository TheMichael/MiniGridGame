# AI Agent Galaxy

A web-based game where you predict how many steps AI agents can take to complete MiniGrid challenges. Test your intuition against Deep Q-Learning and Double Deep Q-Learning agents!

## Quick Start

### Windows

```bash
git clone https://github.com/TheMichael/MiniGridGame.git
cd MiniGridGame
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
python app.py
```

### Mac/Linux

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

1. Open your browser and navigate to `http://localhost:5000`
2. Register a new account or login
3. (Optional) For demonstration purposes with sample data, run: `python populate_db.py`

## Features

- **Multiple AI Agents**: DDQN and D3QN reinforcement learning agents
- **Prediction Game**: Guess how many steps agents will take
- **Risk Zones**: Different difficulty levels with varying scoring multipliers
- **Visual Replays**: Watch AI agents navigate the grid in real-time
- **User Accounts**: Track your progress and compete with others
- **Scoring System**: Earn points based on prediction accuracy and risk level
- **Admin Panel**: Manage users and monitor game statistics

## Game Rules

### Prediction Zones

- **Safe Zone (51-80 steps)**: Low risk, standard scoring
- **Probable Zone (21-50 steps)**: Medium risk, slight bonus
- **Struggle Zone (81-100 steps)**: High risk, good bonus
- **Failure Zone (101-120 steps)**: Very high risk, excellent bonus
- **Impossible Zone (0-20 steps)**: Extreme risk, maximum bonus
- **Failure Prediction (0 steps)**: Predict the agent will fail completely

### Scoring

Points are awarded based on:
- **Accuracy**: How close your prediction was to the actual result
- **Risk Level**: Higher risk zones give bonus multipliers
- **Success Prediction**: Correctly predicting success vs failure

## Development

### Virtual Environment Commands

**Windows:**
```bash
venv\Scripts\activate     # Activate
deactivate               # Deactivate
```

**Mac/Linux:**
```bash
source venv/bin/activate  # Activate
deactivate               # Deactivate
```

### Database Management

```bash
cd backend
python view_db.py        # View database contents
python populate_db.py    # Populate with sample data
python quick_delete.py   # Reset database
```

**Happy Gaming!**