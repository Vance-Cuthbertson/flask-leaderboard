
import json
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)
DATA_FILE = 'leaderboard.json'

def load_leaderboard():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

leaderboard = load_leaderboard()

@app.route('/')
def home():
    return 'Flask server is running!'

@app.route('/update', methods=['POST'])
def update_leaderboard():
    global leaderboard
    data = request.get_json()
    if data and "name" in data and "score" in data:
        existing = next((entry for entry in leaderboard if entry["name"] == data["name"]), None)
        if existing:
            existing["score"] = data["score"]
        else:
            leaderboard.append(data)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        save_leaderboard(leaderboard)
        return jsonify({"status": "success", "received": data})
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
