import json
from flask import Flask, request, jsonify//, render_template_string
import os

DATA_FILE = 'scores.json'

# Load existing scores from JSON file or create a new one
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        scores = json.load(f)
else:
    scores = {}

leaderboard = load_leaderboard()

@app.route('/')
def home():
    return jsonify(scores)

@app.route('/update', methods=['POST'])
def update_score():
    data = request.get_json()
    name = data.get('name')
    score = data.get('score', 0)

    if name:
        if name in scores:
            scores[name] += score
        else:
            scores[name] = score

        with open(DATA_FILE, 'w') as f:
            json.dump(scores, f)

        return jsonify({'message': f"Added {score} points to {name}. New total: {scores[name]}"}), 200
    else:
        return jsonify({'error': 'No name provided'}), 400


@app.route('/leaderboard')
def show_leaderboard():
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    html = """
    <html>
    <head>
        <title>Leaderboard</title>
        <style>
            body { font-family: Arial; background: #f9f9f9; padding: 40px; }
            h1 { text-align: center; color: #333; }
            table { margin: 0 auto; border-collapse: collapse; width: 50%; }
            th, td { border: 1px solid #ccc; padding: 10px; text-align: center; }
            th { background-color: #eee; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Leaderboard</h1>
        <table>
            <tr><th>Player</th><th>Score</th></tr>
    """

    for name, score in sorted_scores.items():
        html += f"<tr><td>{name}</td><td>{score}</td></tr>"

    html += "</table></body></html>"
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
