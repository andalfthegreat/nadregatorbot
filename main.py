import os
import json
import html
from flask import Flask, request
import requests

app = Flask(__name__)

# Replace this with your actual bot token
TELEGRAM_BOT_TOKEN = "7970077331:AAEE-_YknFwcxhl3rdGgRbcOxR3iTXW7RDE"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Define allowed projects
ALLOWED_PROJECTS = ["monad", "molandak", "chog"]

# Load or initialize user preferences
try:
    with open("user_prefs.json", "r") as f:
        user_prefs = json.load(f)
except FileNotFoundError:
    user_prefs = {}

# Save preferences to file
def save_prefs():
    with open("user_prefs.json", "w") as f:
        json.dump(user_prefs, f)

# Send a message to users subscribed to a project
def send_to_telegram(project, message):
    for user_id, prefs in user_prefs.items():
        if project in prefs.get("subscribed", []):
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": user_id,
                "text": message
            })

# Webhook for Telegram updates
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" not in data:
        return {"status": "no message"}, 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").lower()

    user_prefs.setdefault(str(chat_id), {"subscribed": []})
    prefs = user_prefs[str(chat_id)]

    if text == "/start":
        response = "👋 Welcome to Nadregator!\nUse /projects to manage your subscriptions."
    elif text == "/projects":
        response = "📋 Choose a project to subscribe/unsubscribe:\n"
        for project in ALLOWED_PROJECTS:
            sub = "✅" if project in prefs["subscribed"] else "❌"
            response += f"{sub} {project}\n"
        response += "\nUse /subscribe <project> or /unsubscribe <project>"
    elif text.startswith("/subscribe "):
        proj = text.split(" ", 1)[1]
        if proj in ALLOWED_PROJECTS and proj not in prefs["subscribed"]:
            prefs["subscribed"].append(proj)
            save_prefs()
            response = f"✅ Subscribed to '{proj}'"
        else:
            response = f"⚠️ Invalid or already subscribed"
    elif text.startswith("/unsubscribe "):
        proj = text.split(" ", 1)[1]
        if proj in prefs["subscribed"]:
            prefs["subscribed"].remove(proj)
            save_prefs()
            response = f"❌ Unsubscribed from '{proj}'"
        else:
            response = f"⚠️ Not subscribed or invalid project"
    else:
        response = "🤖 Unknown command. Use /projects to manage subscriptions."

    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": response
    })

    return {"status": "ok"}, 200

# Webhook from Discord or other source
@app.route("/hook/<project>", methods=["POST"])
def handle_webhook(project):
    data = request.json
    if not data or "content" not in data:
        return {"error": "Invalid payload"}, 400
    if project not in ALLOWED_PROJECTS:
        return {"error": f"'{project}' is not a valid project"}, 403

    # Keep all emoji and escape any HTML
    content = html.escape(data["content"])
    url = data.get("url", "")

    message = f"[{project}] {content}"
    if url:
        message += f"\n🔗 {url}"

    send_to_telegram(project, message)
    return {"status": "ok"}, 200

# Health check route (optional)
@app.route("/")
def home():
    return "Nadregator webhook online!"
