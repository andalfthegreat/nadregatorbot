import os
import asyncio
import psycopg2
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# --- Environment Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN or not DATABASE_URL:
    raise RuntimeError("❌ BOT_TOKEN or DATABASE_URL is missing in environment variables.")

# --- Telegram Bot Setup ---
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Flask Setup ---
app = Flask(__name__)

# --- PostgreSQL Helpers ---
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def get_projects():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM projects")
            return [row[0] for row in cur.fetchall()]

def get_user_subscriptions(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT project FROM subscriptions WHERE user_id = %s", (user_id,))
            return [row[0] for row in cur.fetchall()]

def subscribe(user_id, project):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO subscriptions (user_id, project) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, project))
            conn.commit()

def unsubscribe(user_id, project):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM subscriptions WHERE user_id = %s AND project = %s", (user_id, project))
            conn.commit()

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscriptions = get_user_subscriptions(user_id)
    all_projects = get_projects()

    keyboard = []
    for project in all_projects:
        if project in subscriptions:
            button = InlineKeyboardButton(f"✅ {project}", callback_data=f"unsub|{project}")
        else:
            button = InlineKeyboardButton(f"🔔 {project}", callback_data=f"sub|{project}")
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your subscriptions:", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action, project = query.data.split("|")

    if action == "sub":
        subscribe(user_id, project)
        await query.edit_message_text(f"✅ Subscribed to {project}")
    elif action == "unsub":
        unsubscribe(user_id, project)
        await query.edit_message_text(f"🔕 Unsubscribed from {project}")

    await start(update, context)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_button))

# --- Webhook for External Broadcast ---
@app.route("/hook/<key>", methods=["POST"])
def webhook(key):
    if key != "your_custom_webhook_key":
        return "Unauthorized", 403

    data = request.json
    text = data.get("content")
    if text:
        asyncio.run(broadcast(text))
    return "OK", 200

async def broadcast(message: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT user_id FROM subscriptions")
            chat_ids = [row[0] for row in cur.fetchall()]
    
    for chat_id in chat_ids:
        try:
            await telegram_app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}")

# --- Run Bot and Server ---
async def run_telegram_bot():
    await telegram_app.initialize()
    await telegram_app.start()
    print("✅ Telegram bot is running...")
    await telegram_app.run_polling()

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    from multiprocessing import Process

    flask_process = Process(target=run_flask)
    bot_process = Process(target=lambda: asyncio.run(run_telegram_bot()))

    flask_process.start()
    bot_process.start()
    flask_process.join()
    bot_process.join()
