from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
USER_PREFS_FILE = 'user_prefs.json'

def load_prefs():
    try:
        with open(USER_PREFS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def send_to_telegram(project, message_text):
    prefs = load_prefs()
    for user_id, projects in prefs.items():
        if project in projects:
            url = f"https://api.telegram.org/bot{7970077331:AAEE-_YknFwcxhl3rdGgRbcOxR3iTXW7RDE}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": f"[{project}] {message_text}"
            }
            requests.post(url, json=payload)

@app.route("/")
def home():
    return "Nadregator webhook online!"

@app.route("/hook/<project>", methods=["POST"])
def handle_webhook(project):
    data = request.json
    if not data or "content" not in data:
        return {"error": "Invalid payload"}, 400

    message = data["content"]
    send_to_telegram(project, message)
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run()
