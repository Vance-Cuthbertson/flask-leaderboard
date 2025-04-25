import json
from flask import Flask, request, jsonify
import os

DATA_FILE = 'leaderboard.json'
TEAM_FILE = 'teams.json'

# Load individual leaderboard
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        leaderboard = json.load(f)
else:
    leaderboard = {}

# Load team leaderboard
if os.path.exists(TEAM_FILE):
    with open(TEAM_FILE, 'r') as f:
        raw_teams = json.load(f)
        teams = {
            team: {
                'members': set(data['members']),
                'score': data['score']
            } for team, data in raw_teams.items()
        }
else:
    teams = {}

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(leaderboard)

@app.route('/update', methods=['POST'])
def update_leaderboard():
    data = request.get_json()

    try:
        name = data.get('name', '').strip()
        score = int(data.get('score', 0))
        team = data.get('team', '').strip()
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid input format"}), 400

    # --- Individual Leaderboard ---
    leaderboard[name] = leaderboard.get(name, 0) + score

    # --- Team leaderboard ---
    if team not in teams:
        teams[team] = {'members': set(), 'score': 0}

    if len(teams[team]['members']) < 4 or name in teams[team]['members']:
        teams[team]['members'].add(name)
        teams[team]['score'] += score

        # Save updated individual leaderboard
        with open(DATA_FILE, 'w') as f:
            json.dump(leaderboard, f)

        # Save updated team leaderboard
        with open(TEAM_FILE, 'w') as f:
            json.dump({
                team: {
                    'members': list(data['members']),
                    'score': data['score']
                } for team, data in teams.items()
            }, f)
    
        # Debugging: print the current state of the leaderboard
        print("Current individual leaderboard:", leaderboard)
        print("Current teams leaderboard:", teams)

        return jsonify({"status": "success", "message": "Score submitted!"})
    else:
        return jsonify({"status": "error", "message": "Team already has 4 members"}), 403

@app.route('/leaderboard')
def show_leaderboards():
    sorted_individuals = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    sorted_teams = sorted(teams.items(), key=lambda x: x[1]['score'], reverse=True)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leaderboards</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f0f0f0; }
            h1 { text-align: center; }
            .container { display: flex; justify-content: space-around; gap: 40px; flex-wrap: wrap; }
            table {
                background: white; border-collapse: collapse; width: 100%; max-width: 400px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            th, td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
            th { background-color: #4CAF50; color: white; }
        </style>
    </head>
    <body>
        <h1>Game Leaderboards</h1>
        <div class="container">
            <div>
                <h2>Individual Leaderboard</h2>
                <table>
                    <tr><th>Player</th><th>Score</th></tr>
    """

    for name, score in sorted_individuals:
        html += f"<tr><td>{name}</td><td>{score}</td></tr>"

    html += """
                </table>
            </div>
            <div>
                <h2>Team Leaderboard</h2>
                <table>
                    <tr><th>Team</th><th>Score</th></tr>
    """

    for team, data in sorted_teams:
        html += f"<tr><td>{team}</td><td>{data['score']}</td></tr>"

    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    from flask import Response
    return Response(html, mimetype='text/html')

RESET_CODE = "RESET123"  # Change this to your secret code

@app.route('/reset', methods=['POST'])
def reset_leaderboard():
    if request.form.get("code") != RESET_CODE:
        return jsonify({"status": "error", "message": "Invalid reset code"}), 403

    leaderboard.clear()
    teams.clear()

    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

    with open(TEAM_FILE, 'w') as f:
        json.dump({}, f)

    return jsonify({"status": "success", "message": "Leaderboards have been reset."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
