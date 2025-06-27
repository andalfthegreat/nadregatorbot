import os
import asyncio
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is missing! Set it in environment variables.")

# --- Flask app ---
app = Flask(__name__)

# --- Telegram bot setup ---
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Telegram handlers ---
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
    action = query.data
    await query.edit_message_text(text=f"You chose: {action}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_buttons))

# --- Endpoint for external announcements ---
@app.route("/hook/<key>", methods=["POST"])
def webhook(key):
    if key != "your_custom_webhook_key":
        return "Unauthorized", 403
    data = request.json
    text = data.get("content")
    if text:
        telegram_app.create_task(broadcast_announcement(text))
    return "OK", 200

# --- Broadcast to all chat_ids (replace with your logic) ---
async def broadcast_announcement(message: str):
    chat_ids = [...]  # Replace with real chat IDs from your DB
    for chat_id in chat_ids:
        try:
            await telegram_app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}")

# --- Run the bot in the main async loop ---
async def main():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    await telegram_app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())

