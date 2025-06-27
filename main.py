import os
import json
from flask import Flask, request
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "7970077331:AAEE-_YknFwcxhl3rdGgRbcOxR3iTXW7RDE"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

ALLOWED_PROJECTS = ["monad", "molandak", "chog"]

try:
    with open("user_prefs.json", "r") as f:
        user_prefs = json.load(f)
except FileNotFoundError:
    user_prefs = {}

def save_prefs():
    with open("user_prefs.json", "w") as f:
        json.dump(user_prefs, f)

def send_to_telegram(project, message):
    for user_id, prefs in user_prefs.items():
        if project in prefs.get("subscribed", []):
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": user_id,
                "text": message
            })

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").lower()
        user_prefs.setdefault(str(chat_id), {"subscribed": []})
        prefs = user_prefs[str(chat_id)]

        if text == "/start":
            response = "👋 Welcome to Nadregator! Use /projects to manage subscriptions."
            requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": response})

        elif text == "/projects":
            keyboard = []
            for project in ALLOWED_PROJECTS:
                keyboard.append([
                    {"text": f"Subscribe {project.capitalize()}", "callback_data": f"subscribe:{project}"},
                    {"text": f"Unsubscribe {project.capitalize()}", "callback_data": f"unsubscribe:{project}"}
                ])
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "📋 Choose a project to subscribe/unsubscribe:",
                "reply_markup": {"inline_keyboard": keyboard}
            })

    elif "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["from"]["id"]
        action, project = query["data"].split(":")
        prefs = user_prefs.setdefault(str(chat_id), {"subscribed": []})

        if action == "subscribe" and project not in prefs["subscribed"]:
            prefs["subscribed"].append(project)
            text = f"✅ Subscribed to {project}"
        elif action == "unsubscribe" and project in prefs["subscribed"]:
            prefs["subscribed"].remove(project)
            text = f"❌ Unsubscribed from {project}"
        else:
            text = "⚠️ Nothing changed."

        save_prefs()

        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })

    return {"status": "ok"}, 200

@app.route("/hook/<project>", methods=["POST"])
def handle_webhook(project):
    data = request.json
    if not data or "content" not in data:
        return {"error": "Invalid payload"}, 400
    if project not in ALLOWED_PROJECTS:
        return {"error": f"'{project}' is not a valid project"}, 403

    content = data["content"]
    url = data.get("url", "")
    message = f"[{project}] {content}"
    if url:
        message += f"\n🔗 {url}"

    send_to_telegram(project, message)
    return {"status": "ok"}, 200

@app.route("/")
def home():
    return "Nadregator webhook online!"
