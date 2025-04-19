import requests

data = {
    "name": "Steve",
    "score": 100,
}

response = requests.post("https://flask-leaderboard-8uws.onrender.com/update", json=data)

print("Status Code:", response.status_code)
print("Response Text:", response.text)
