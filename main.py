import os
import json
import logging
from flask import Flask, request
from telegram import (
    Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# Logging setup
logging.basicConfig(level=logging.INFO)

# === Constants ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PROJECTS = ["monad", "molandak", "chog"]
PREFS_FILE = "user_prefs.json"

# === Initialize prefs file ===
if not os.path.exists(PREFS_FILE):
    with open(PREFS_FILE, "w") as f:
        json.dump({}, f)

def load_prefs():
    with open(PREFS_FILE, "r") as f:
        return json.load(f)

def save_prefs(data):
    with open(PREFS_FILE, "w") as f:
        json.dump(data, f)

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(p.capitalize(), callback_data=f"toggle:{p}")]
        for p in PROJECTS
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select which projects you'd like to subscribe to:", reply_markup=markup
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    prefs = load_prefs()
    prefs.setdefault(user_id, [])

    project = query.data.split(":")[1]
    if project in prefs[user_id]:
        prefs[user_id].remove(project)
        msg = f"❌ Unsubscribed from {project}"
    else:
        prefs[user_id].append(project)
        msg = f"✅ Subscribed to {project}"

    save_prefs(prefs)
    await query.edit_message_text(msg)

# === Flask + Telegram Webhook ===
flask_app = Flask(__name__)
bot = Bot(BOT_TOKEN)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await telegram_app.process_update(update)
    return "OK"

# === Custom project message trigger ===
@flask_app.route("/hook/<project>", methods=["POST"])
def notify_project(project):
    data = request.json
    content = data.get("content", "")
    prefs = load_prefs()

    for user_id, subs in prefs.items():
        if project in subs:
            try:
                bot.send_message(chat_id=int(user_id), text=f"[{project}] {content}")
            except Exception as e:
                logging.warning(f"Failed to send to {user_id}: {e}")

    return "Message sent", 200

# === Register handlers ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_buttons))

# === For gunicorn ===
app = flask_app
