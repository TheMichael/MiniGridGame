import requests
import json
import random
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"
session = requests.Session()

# Realistic user data
USERS_DATA = [
    {"username": "alice_ai", "email": "alice@email.com", "password": "password123"},
    {"username": "bob_gamer", "email": "bob@email.com", "password": "password123"},
    {"username": "charlie_pro", "email": "charlie@email.com", "password": "password123"},
    {"username": "diana_strategic", "email": "diana@email.com", "password": "password123"},
    {"username": "erik_predictor", "email": "erik@email.com", "password": "password123"},
    {"username": "fiona_analytics", "email": "fiona@email.com", "password": "password123"},
    {"username": "george_neural", "email": "george@email.com", "password": "password123"},
    {"username": "hannah_ml", "email": "hannah@email.com", "password": "password123"},
    {"username": "ivan_deep", "email": "ivan@email.com", "password": "password123"},
    {"username": "julia_ai", "email": "julia@email.com", "password": "password123"}
]

# Different player personalities with prediction patterns
PLAYER_PERSONALITIES = {
    "conservative": {
        "description": "Predicts higher numbers (expects longer paths)",
        "step_range": (70, 120),
        "agent_preference": "ddqn"
    },
    "aggressive": {
        "description": "Predicts lower numbers (optimistic about efficiency)",
        "step_range": (20, 60),
        "agent_preference": "d3qn"
    },
    "analytical": {
        "description": "Well-researched predictions, balanced approach",
        "step_range": (40, 80),
        "agent_preference": None  # No preference
    },
    "random": {
        "description": "Completely random predictions",
        "step_range": (1, 120),
        "agent_preference": None
    },
    "optimistic": {
        "description": "Believes agent will succeed quickly, predicts middle range",
        "step_range": (45, 75),
        "agent_preference": "ddqn"
    }
}

def register_user(username, email, password):
    """Register a new user"""
    try:
        response = session.post(f"{BASE_URL}/api/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"Registered user: {username}")
                return True
            else:
                print(f"Registration failed for {username}: {data.get('error')}")
                return False
        else:
            print(f"Registration error for {username}: {response.status_code}")
            return False

    except Exception as e:
        print(f"Registration exception for {username}: {e}")
        return False

def login_user(username, password):
    """Login as a user"""
    try:
        response = session.post(f"{BASE_URL}/api/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"Logged in as: {username}")
                return True

        print(f"Login failed for {username}")
        return False

    except Exception as e:
        print(f"Login exception for {username}: {e}")
        return False

def generate_prediction(personality):
    """Generate a prediction based on personality"""
    # Generate prediction within personality's range (1-120)
    # No longer supporting failure predictions (0)
    return random.randint(*personality["step_range"])

def choose_agent(personality):
    """Choose agent based on personality"""
    if personality["agent_preference"]:
        return personality["agent_preference"]
    else:
        return random.choice(["ddqn", "d3qn"])

def play_game(agent_type, prediction):
    """Play a single game"""
    try:
        response = session.post(f"{BASE_URL}/api/run-validation", json={
            "agent_type": agent_type,
            "prediction": str(prediction)
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"Game played: {agent_type.upper()} agent, predicted {prediction} steps, "
                  f"actual {data['steps']} steps, scored {data['score']} points")
            return data
        else:
            print(f"Game failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"Game exception: {e}")
        return None

def logout():
    """Logout current user"""
    try:
        session.post(f"{BASE_URL}/api/logout")
        print("Logged out")
    except:
        pass

def simulate_user_session(user_data, num_games):
    """Simulate a complete user session"""
    username = user_data["username"]
    
    # Assign personality
    personality_name = random.choice(list(PLAYER_PERSONALITIES.keys()))
    personality = PLAYER_PERSONALITIES[personality_name]
    
    print(f"\nSimulating {username} ({personality_name}): {personality['description']}")
    
    # Register user
    if not register_user(user_data["username"], user_data["email"], user_data["password"]):
        return
    
    # Login
    if not login_user(user_data["username"], user_data["password"]):
        return
    
    # Play games
    games_played = 0
    total_score = 0
    
    for game_num in range(num_games):
        # Generate prediction based on personality
        prediction = generate_prediction(personality)
        agent = choose_agent(personality)
        
        # Play the game
        result = play_game(agent, prediction)
        
        if result:
            games_played += 1
            total_score += result['score']
            
            # Small delay to be nice to the server
            time.sleep(0.5)
        
        # Random break between games (simulate thinking time)
        if random.random() < 0.3:  # 30% chance of longer break
            time.sleep(random.uniform(1, 3))
    
    print(f"{username} finished: {games_played} games, {total_score} total points")
    
    # Logout
    logout()
    time.sleep(1)  # Brief pause between users

def populate_database(num_users=None, games_per_user_range=(3, 12)):
    """Main function to populate the database"""
    
    print("NEURAL NAVIGATOR - DATABASE POPULATION SCRIPT")
    print("=" * 60)
    print(f"Target: {num_users or len(USERS_DATA)} users, {games_per_user_range[0]}-{games_per_user_range[1]} games each")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print("Server is running and accessible")
    except:
        print("Error: Server not running! Start your Flask app first.")
        print("   Run: python app.py")
        return
    
    # Use specified number of users or all available
    users_to_create = USERS_DATA[:num_users] if num_users else USERS_DATA
    
    total_users = len(users_to_create)
    total_games_estimate = sum(random.randint(*games_per_user_range) for _ in users_to_create)

    print(f"\nPlan: {total_users} users, ~{total_games_estimate} games total")
    print("Estimated time: ~{:.1f} minutes".format(total_games_estimate * 0.5 / 60))

    input("\nPress Enter to start population (or Ctrl+C to cancel)...")
    
    start_time = time.time()
    
    for i, user_data in enumerate(users_to_create, 1):
        print(f"\n{'='*20} User {i}/{total_users} {'='*20}")
        
        # Random number of games for this user
        num_games = random.randint(*games_per_user_range)
        
        # Simulate the user
        simulate_user_session(user_data, num_games)
        
        # Progress update
        elapsed = time.time() - start_time
        avg_time_per_user = elapsed / i
        remaining_users = total_users - i
        eta_seconds = remaining_users * avg_time_per_user
        
        print(f"Progress: {i}/{total_users} users complete. ETA: {eta_seconds/60:.1f} minutes")

    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("DATABASE POPULATION COMPLETE!")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Users created: {total_users}")
    print("Run 'python view_db.py' to see the results!")
    print("=" * 60)

def create_demo_data():
    """Create a smaller demo dataset"""
    demo_users = USERS_DATA[:5]  # First 5 users

    print("Creating demo data with 5 users...")
    populate_database(num_users=5, games_per_user_range=(2, 6))

if __name__ == "__main__":
    import sys

    print("Database Population Options:")
    print("1. Demo (5 users, 2-6 games each) - ~2 minutes")
    print("2. Small (7 users, 3-8 games each) - ~4 minutes") 
    print("3. Full (10 users, 3-12 games each) - ~8 minutes")
    print("4. Custom")
    
    choice = input("\nChoose option (1-4): ").strip()
    
    if choice == "1":
        populate_database(num_users=5, games_per_user_range=(2, 6))
    elif choice == "2":
        populate_database(num_users=7, games_per_user_range=(3, 8))
    elif choice == "3":
        populate_database(num_users=10, games_per_user_range=(3, 12))
    elif choice == "4":
        try:
            num_users = int(input("Number of users (1-10): "))
            min_games = int(input("Minimum games per user: "))
            max_games = int(input("Maximum games per user: "))
            populate_database(num_users=num_users, games_per_user_range=(min_games, max_games))
        except ValueError:
            print("Invalid input. Please enter numbers.")
    else:
        print("Invalid choice. Run the script again.")