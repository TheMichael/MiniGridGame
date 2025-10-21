import sqlite3
import json
from datetime import datetime

def view_database():
    """Simple script to view your MiniGrid game database"""
    
    # Connect to database
    conn = sqlite3.connect('minigrid_game.db')
    cursor = conn.cursor()
    
    print("AI AGENT GALAXY - DATABASE VIEWER")
    print("=" * 50)

    # Show all users
    print("\nREGISTERED USERS:")
    print("-" * 30)
    cursor.execute("""
        SELECT username, total_score, games_played, games_won, created_at
        FROM user 
        ORDER BY total_score DESC
    """)
    
    users = cursor.fetchall()
    if users:
        print(f"{'Username':<15} {'Score':<8} {'Games':<7} {'Wins':<6} {'Success%':<9} {'Joined':<12}")
        print("-" * 70)
        for user in users:
            username, score, games, wins, created = user
            success_rate = (wins/games*100) if games > 0 else 0
            created_date = created[:10] if created else "Unknown"
            print(f"{username:<15} {score:<8} {games:<7} {wins:<6} {success_rate:<9.1f} {created_date:<12}")
    else:
        print("No users registered yet.")
    
    # Show recent games
    print(f"\nRECENT GAMES (Last 10):")
    print("-" * 40)
    cursor.execute("""
        SELECT u.username, g.agent_type, g.prediction, g.actual_steps, 
               g.succeeded, g.score, g.timestamp
        FROM game_result g
        JOIN user u ON g.user_id = u.id
        ORDER BY g.timestamp DESC
        LIMIT 10
    """)
    
    games = cursor.fetchall()
    if games:
        print(f"{'Player':<12} {'Agent':<6} {'Pred':<6} {'Actual':<8} {'Won':<5} {'Score':<7} {'When':<12}")
        print("-" * 65)
        for game in games:
            username, agent, pred, actual, won, score, timestamp = game
            pred_str = "FAIL" if pred == 0 else str(pred)
            won_str = "YES" if won else "NO"
            time_str = timestamp[5:16] if timestamp else "Unknown"  # MM-DD HH:MM
            print(f"{username:<12} {agent.upper():<6} {pred_str:<6} {actual:<8} {won_str:<5} {score:<7} {time_str:<12}")
    else:
        print("No games played yet.")
    
    # Database statistics
    print(f"\nDATABASE STATISTICS:")
    print("-" * 25)
    
    cursor.execute("SELECT COUNT(*) FROM user")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM game_result")
    total_games = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM game_result WHERE succeeded = 1")
    successful_games = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total_score) FROM user")
    total_points = cursor.fetchone()[0] or 0
    
    success_rate = (successful_games/total_games*100) if total_games > 0 else 0
    
    print(f"Total Users: {total_users}")
    print(f"Total Games: {total_games}")
    print(f"Successful Games: {successful_games}")
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print(f"Total Points Earned: {total_points}")
    
    if total_games > 0:
        cursor.execute("SELECT agent_type, COUNT(*) FROM game_result GROUP BY agent_type")
        agent_stats = cursor.fetchall()
        print(f"\nAgent Usage:")
        for agent, count in agent_stats:
            print(f"  {agent.upper()}: {count} games ({count/total_games*100:.1f}%)")
    
    conn.close()
    print("\n" + "=" * 50)

def search_user(username):
    """Search for a specific user's data"""
    conn = sqlite3.connect('minigrid_game.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"User '{username}' not found.")
        return
    
    print(f"\nUSER PROFILE: {username}")
    print("-" * 30)
    print(f"Total Score: {user[5]}")
    print(f"Games Played: {user[6]}")
    print(f"Games Won: {user[7]}")
    print(f"Success Rate: {(user[7]/user[6]*100) if user[6] > 0 else 0:.1f}%")
    print(f"Joined: {user[4][:10] if user[4] else 'Unknown'}")
    
    # Show user's game history
    cursor.execute("""
        SELECT agent_type, prediction, actual_steps, succeeded, score, timestamp
        FROM game_result 
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user[0],))
    
    games = cursor.fetchall()
    print(f"\nGAME HISTORY ({len(games)} games):")
    print("-" * 70)
    
    if games:
        print(f"{'Agent':<6} {'Prediction':<12} {'Actual':<8} {'AI Result':<10} {'Pred Result':<12} {'Score':<7} {'Date':<12}")
        print("-" * 70)
        for game in games:
            agent, pred, actual, ai_succeeded, score, timestamp = game
            
            # Determine prediction accuracy
            if pred == 0:  # Predicted failure
                pred_str = "Will Fail"
                pred_correct = "Correct" if not ai_succeeded else "Wrong"
            else:
                pred_str = f"{pred} steps"
                difference = abs(int(pred) - actual)
                if difference == 0:
                    pred_correct = "Perfect"
                elif difference <= 5:
                    pred_correct = "Close"
                elif difference <= 10:
                    pred_correct = "Decent"
                else:
                    pred_correct = "Off"
            
            ai_result = "Completed" if ai_succeeded else "Failed"
            date_str = timestamp[5:16] if timestamp else "Unknown"
            
            print(f"{agent.upper():<6} {pred_str:<12} {actual:<8} {ai_result:<10} {pred_correct:<12} {score:<7} {date_str:<12}")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Search for specific user
        username = sys.argv[1]
        search_user(username)
    else:
        # Show overview
        view_database()
    
    print("\nUsage:")
    print("  python view_db.py           # Show all data")
    print("  python view_db.py alice     # Show Alice's profile")