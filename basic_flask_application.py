from flask import Flask, request, jsonify, Response
import os
from openpyxl import Workbook, load_workbook

LEADERBOARD_XLSX = 'leaderboard.xlsx'
TEAMS_XLSX = 'teams.xlsx'
RESET_CODE = "RESET123"  # Change this to your secret code

app = Flask(__name__)

# --- Load Data ---
def load_leaderboard():
    leaderboard = {}
    if os.path.exists(LEADERBOARD_XLSX):
        wb = load_workbook(LEADERBOARD_XLSX)
        ws = wb.active
        for row in ws.iter_rows(min_row=2, values_only=True):
            name, score = row
            leaderboard[name] = score
    return leaderboard

def load_teams():
    teams = {}
    if os.path.exists(TEAMS_XLSX):
        wb = load_workbook(TEAMS_XLSX)
        ws = wb.active
        for row in ws.iter_rows(min_row=2, values_only=True):
            team, score, members = row
            teams[team] = {
                'score': score,
                'members': set(m.strip() for m in members.split(',')) if members else set()
            }
    return teams

# --- Save Data ---
def save_leaderboard():
    wb = Workbook()
    ws = wb.active
    ws.append(["Name", "Score"])
    for name, score in leaderboard.items():
        ws.append([name, score])
    wb.save(LEADERBOARD_XLSX)

def save_teams():
    wb = Workbook()
    ws = wb.active
    ws.append(["Team", "Score", "Members"])
    for team, data in teams.items():
        ws.append([team, data['score'], ",".join(data['members'])])
    wb.save(TEAMS_XLSX)

leaderboard = load_leaderboard()
teams = load_teams()

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

    leaderboard[name] = leaderboard.get(name, 0) + score

    if team not in teams:
        teams[team] = {'members': set(), 'score': 0}

    if len(teams[team]['members']) < 4 or name in teams[team]['members']:
        teams[team]['members'].add(name)
        teams[team]['score'] += score
        save_leaderboard()
        save_teams()
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
    return Response(html, mimetype='text/html')

@app.route('/reset', methods=['POST'])
def reset_leaderboard():
    if request.form.get("code") != RESET_CODE:
        return jsonify({"status": "error", "message": "Invalid reset code"}), 403

    leaderboard.clear()
    teams.clear()

    save_leaderboard()
    save_teams()

    return jsonify({"status": "success", "message": "Leaderboards have been reset."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
