import json
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

DATA_FILE = 'leaderboard.json'

# Load leaderboard from file
def load_leaderboard():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save leaderboard to file
def save_leaderboard(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Initialize leaderboard
leaderboard = load_leaderboard()

@app.route('/')
def home():
    return 'Flask server is running!'

@app.route('/update', methods=['POST'])
def update_leaderboard():
    global leaderboard
    data = request.get_json()

    if data and "name" in data and "score" in data:
        name = data["name"]
        score = data["score"]


        # Check if name exists and update score
        found = False
        for entry in leaderboard:
            if entry["name"] == name:
                entry["score"] = score  # or: max(entry["score"], score)
                found = True
                break

        # If not found, append as new
        if not found:
            leaderboard.append(data)

        # Sort the leaderboard by score (descending)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        # Save updated leaderboard        
        save_leaderboard(leaderboard)

        return jsonify({"status": "success", "updated": data})
    
    else:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/leaderboard')
def show_leaderboard():
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Leaderboard</title></head>
    <body>
        <h1>Leaderboard</h1>
        <table border="1" cellpadding="10">
            <tr><th>Rank</th><th>Name</th><th>Score</th></tr>
            {% for entry in leaderboard %}
                <tr><td>{{ loop.index }}</td><td>{{ entry.name }}</td><td>{{ entry.score }}</td></tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''
    return render_template_string(html, leaderboard=leaderboard)

@app.route('/reset', methods=['POST'])
def reset_leaderboard():
    global leaderboard
    leaderboard = []
    save_leaderboard(leaderboard)
    return jsonify({"status": "success", "message": "Leaderboard has been reset."})

# This block prevents SystemExit errors when running in IDEs
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

