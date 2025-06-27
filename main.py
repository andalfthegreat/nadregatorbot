from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("7970077331:AAEE-_YknFwcxhl3rdGgRbcOxR3iTXW7RDE")
USER_PREFS_FILE = 'user_prefs.json'
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ✅ Only these projects can be subscribed to
ALLOWED_PROJECTS = ["monad", "molandak", "chog"]

def load_prefs():
    try:
        with open(USER_PREFS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_prefs(prefs):
    with open(USER_PREFS_FILE, 'w') as f:
        json.dump(prefs, f)

def send_to_telegram(project, message_text):
    prefs = load_prefs()
    for user_id, projects in prefs.items():
        if project in projects:
            url = f"{TELEGRAM_API}/sendMessage"
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
    if project not in ALLOWED_PROJECTS:
        return {"error": f"'{project}' is not a valid project"}, 403
    message = data["content"]
    send_to_telegram(project, message)
    return {"status": "ok"}, 200

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.json
    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    user_id = str(message["chat"]["id"])
    text = message.get("text", "").strip()
    prefs = load_prefs()

    if text.startswith("/subscribe"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            project = parts[1].lower()
            if project not in ALLOWED_PROJECTS:
                send_reply(user_id, f"❌ '{project}' is not a valid project.")
            else:
                prefs.setdefault(user_id, [])
                if project not in prefs[user_id]:
                    prefs[user_id].append(project)
                    save_prefs(prefs)
                    send_reply(user_id, f"✅ Subscribed to '{project}'")
                else:
                    send_reply(user_id, f"⚠️ Already subscribed to '{project}'")
        else:
            send_reply(user_id, "❗ Usage: /subscribe <project>")

    elif text.startswith("/unsubscribe"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            project = parts[1].lower()
            if project not in ALLOWED_PROJECTS:
                send_reply(user_id, f"❌ '{project}' is not a valid project.")
            elif user_id in prefs and project in prefs[user_id]:
                prefs[user_id].remove(project)
                save_prefs(prefs)
                send_reply(user_id, f"❌ Unsubscribed from '{project}'")
            else:
                send_reply(user_id, f"⚠️ Not subscribed to '{project}'")
        else:
            send_reply(user_id, "❗ Usage: /unsubscribe <project>")

    else:
        send_reply(user_id, "🤖 Use /subscribe <project> or /unsubscribe <project>")

    return {"ok": True}

def send_reply(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})
