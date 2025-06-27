import os
import threading
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is missing! Set it in environment variables.")

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Subscribe 🔔", callback_data="subscribe")],
        [InlineKeyboardButton("Unsubscribe 🔕", callback_data="unsubscribe")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"You chose: {query.data}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_buttons))

# --- Announcement Broadcast ---
async def broadcast_announcement(message: str):
    chat_ids = [...]  # Replace with actual IDs
    for chat_id in chat_ids:
        try:
            await telegram_app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")

@app.route("/hook/<key>", methods=["POST"])
def webhook(key):
    if key != "your_custom_webhook_key":
        return "Unauthorized", 403
    data = request.json
    text = data.get("content")
    if text:
        telegram_app.create_task(broadcast_announcement(text))
    return "OK", 200

@app.route("/")
def home():
    return "✅ Bot is running", 200

# --- Start bot when Flask is ready ---
@app.before_first_request
def launch_telegram():
    threading.Thread(target=telegram_app.run_polling, daemon=True).start()
