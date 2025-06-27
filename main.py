import os
import json
from flask import Flask, request
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import asyncio

# Securely load the bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = f"https://nadregatorbot.onrender.com/{BOT_TOKEN}"

# Your curated project list (later this will go into a DB)
projects = ["monad", "molandak", "chog"]

# File-based fallback for user prefs (to be replaced with DB)
PREF_FILE = "user_prefs.json"

def load_user_prefs():
    if os.path.exists(PREF_FILE):
        with open(PREF_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_prefs(prefs):
    with open(PREF_FILE, "w") as f:
        json.dump(prefs, f)

user_prefs = load_user_prefs()

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_prefs:
        user_prefs[user_id] = []
        save_user_prefs(user_prefs)
    await update.message.reply_text(
        "Welcome to Nadregator!\nUse /projects to manage your subscriptions."
    )

# /projects command
async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    keyboard = []

    for proj in projects:
        subscribed = proj in user_prefs.get(user_id, [])
        label = f"{'✅' if subscribed else '❌'} {proj}"
        callback_data = f"{'unsubscribe' if subscribed else 'subscribe'}:{proj}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your subscriptions:", reply_markup=reply_markup)

# Button press callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    action, project = query.data.split(":")

    if action == "subscribe":
        user_prefs.setdefault(user_id, []).append(project)
    elif action == "unsubscribe" and project in user_prefs.get(user_id, []):
        user_prefs[user_id].remove(project)

    save_user_prefs(user_prefs)
    await list_projects(update, context)

# Webhook endpoint for Discord → Telegram announcements
@app.route("/hook/<project>", methods=["POST"])
def handle_webhook(project):
    if project not in projects:
        return {"error": "Unknown project"}, 400

    data = request.json
    message = data.get("content", "New update")
    notify_subscribers(project, message)
    return {"ok": True}

# Send messages to subscribed users
def notify_subscribers(project, message):
    for user_id, subscriptions in user_prefs.items():
        if project in subscriptions:
            asyncio.run(send_telegram_message(user_id, f"[{project}] {message}"))

async def send_telegram_message(user_id, text):
    await telegram_app.bot.send_message(chat_id=user_id, text=text)

# Telegram command + callback handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("projects", list_projects))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

# Set the Telegram webhook on startup
async def set_webhook():
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    import threading

    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())

    threading.Thread(target=lambda: telegram_app.run_polling(), daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
