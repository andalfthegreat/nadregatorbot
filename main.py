import os
import json
from flask import Flask, request
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Telegram Bot Token from Render environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Define list of projects
PROJECTS = ["monad", "molandak", "chog"]

# Store user subscriptions
USER_PREFS_FILE = "user_prefs.json"
if not os.path.exists(USER_PREFS_FILE):
    with open(USER_PREFS_FILE, "w") as f:
        json.dump({}, f)

# Telegram app
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

# Load user preferences
def load_user_prefs():
    with open(USER_PREFS_FILE, "r") as f:
        return json.load(f)

def save_user_prefs(prefs):
    with open(USER_PREFS_FILE, "w") as f:
        json.dump(prefs, f)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(project.capitalize(), callback_data=f"toggle:{project}")]
        for project in PROJECTS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select projects to subscribe/unsubscribe:", reply_markup=reply_markup)

# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if data.startswith("toggle:"):
        project = data.split(":")[1]
        prefs = load_user_prefs()
        prefs.setdefault(user_id, [])
        if project in prefs[user_id]:
            prefs[user_id].remove(project)
            status = f"❌ Unsubscribed from {project.capitalize()}"
        else:
            prefs[user_id].append(project)
            status = f"✅ Subscribed to {project.capitalize()}"
        save_user_prefs(prefs)
        await query.edit_message_text(text=status)

# Webhook broadcaster
app = Flask(__name__)

@app.before_request
def setup_webhook_once():
    if not hasattr(app, "initialized"):
        app.initialized = True
        # Set the Telegram webhook
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
        telegram_app.bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook set to {webhook_url}")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return "OK"

# Webhook for external posts (e.g., from curl/Discord)
@app.route("/hook/<project>", methods=["POST"])
def external_webhook(project):
    message = request.json.get("content")
    prefs = load_user_prefs()
    for user_id, subscribed in prefs.items():
        if project in subscribed:
            try:
                bot.send_message(chat_id=int(user_id), text=f"[{project}] {message}")
            except Exception as e:
                logging.error(f"Failed to send to {user_id}: {e}")
    return "OK"

# Register handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))

# Export app for gunicorn
if __name__ == "__main__":
    app.run()
