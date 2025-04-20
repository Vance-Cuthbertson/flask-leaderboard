
import json
from flask import Flask, request, jsonify, render_template_string
import os
import requests

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
        name = data["name"]
        score = int(data["score"])  # Make sure score is an int

        # Flag to check if the user exists
        user_found = False

        for entry in leaderboard:
            if entry["name"].lower() == name.lower():  # Case-insensitive match
                entry["score"] += score  # Add to existing score
                user_found = True
                break

        if not user_found:
            leaderboard.append({"name": name, "score": score})

        # Sort leaderboard from highest to lowest score
        leaderboard.sort(key=lambda x: x["score"], reverse=True)

        save_leaderboard(leaderboard)
        return jsonify({"status": "success", "leaderboard": leaderboard})
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
        <form action="{{ url_for('fetch_esp32') }}" method="get">
            <button type="submit">Fetch Score from ESP32</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html, leaderboard=leaderboard)

@app.route('/fetch-esp32')
def fetch_esp32():
    esp32_ip = 'http://192.168.X.X/score'  # Replace with your ESP32 IP
    try:
        response = requests.get(esp32_ip)
        if response.status_code == 200:
            data = response.json()
            name = data['name']
            score = int(data['score'])

            # Update the leaderboard logic
            leaderboard = load_leaderboard()
            if name in leaderboard:
                leaderboard[name] += score
            else:
                leaderboard[name] = score
            save_leaderboard(leaderboard)
            return redirect(url_for('home'))
        else:
            return f"Error: ESP32 returned status {response.status_code}"
    except Exception as e:
        return f"Failed to reach ESP32: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
