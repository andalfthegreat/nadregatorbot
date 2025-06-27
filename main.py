from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is missing! Make sure it's set in Render environment variables.")

# Load user subscriptions from JSON file
try:
    with open("user_prefs.json", "r") as f:
        user_prefs = json.load(f)
except FileNotFoundError:
    user_prefs = {}

projects = ["monad", "molandak"]

app = Flask(__name__)


# --- Telegram Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_prefs.setdefault(user_id, [])
    await update.message.reply_text("Welcome to Nadregator! Use /projects to manage your subscriptions.")


async def projects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_projects = set(user_prefs.get(user_id, []))

    keyboard = []
    for project in projects:
        if project in user_projects:
            label = f"✅ {project}"
        else:
            label = f"➕ {project}"
        keyboard.append([InlineKeyboardButton(label, callback_data=project)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a project to subscribe/unsubscribe:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    project = query.data

    if user_id not in user_prefs:
        user_prefs[user_id] = []

    if project in user_prefs[user_id]:
        user_prefs[user_id].remove(project)
        await query.edit_message_text(f"❌ Unsubscribed from {project}")
    else:
        user_prefs[user_id].append(project)
        await query.edit_message_text(f"✅ Subscribed to {project}")

    with open("user_prefs.json", "w") as f:
        json.dump(user_prefs, f)


# --- Discord Webhook Handler ---
@app.route("/hook/<project>", methods=["POST"])
def handle_webhook(project):
    if project not in projects:
        return {"error": "Unknown project"}, 400

    data = request.get_json()
    content = data.get("content", "")

    for user_id, prefs in user_prefs.items():
        if project in prefs:
            try:
                app.bot.send_message(chat_id=user_id, text=f"[{project}] {content}")
            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")

    return {"ok": True}


# --- Start Bot via Webhook ---
@app.before_first_request
def activate_bot():
    from telegram import Bot
    from telegram.ext import Application

    print("🔄 Initializing Telegram bot...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("projects", projects_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    app.bot = application.bot
    application.run_polling()  # NOTE: Replace with `run_webhook()` for production if needed


# --- Required for Render/Gunicorn ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

    threading.Thread(target=lambda: telegram_app.run_polling(), daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
