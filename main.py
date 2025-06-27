import os
import threading
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is missing!")

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

@app.before_first_request
def launch_bot():
    threading.Thread(target=telegram_app.run_polling, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Subscribe 🔔", callback_data="subscribe")],
        [InlineKeyboardButton("Unsubscribe 🔕", callback_data="unsubscribe")]
    ]
    await update.message.reply_text("Welcome!", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"You chose: {query.data}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))

