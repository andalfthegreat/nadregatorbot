import os
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is missing!")
if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL is missing!")

# --- Database ---
conn = psycopg2.connect(DATABASE_URL, sslmode="require", cursor_factory=RealDictCursor)
conn.autocommit = True

def init_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE
            );
        """)

# --- Flask ---
app = Flask(__name__)

# --- Telegram ---
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = []

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM projects ORDER BY name;")
        projects = cur.fetchall()

        for project in projects:
            cur.execute("""
                SELECT 1 FROM subscriptions
                WHERE user_id = %s AND project_id = %s;
            """, (user_id, project["id"]))
            subscribed = cur.fetchone() is not None

            btn_text = f"{'✅' if subscribed else '➕'} {project['name']}"
            action = f"{'unsub' if subscribed else 'sub'}:{project['id']}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=action)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose projects to subscribe/unsubscribe:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    action, project_id = query.data.split(":")
    project_id = int(project_id)

    with conn.cursor() as cur:
        if action == "sub":
            cur.execute("""
                INSERT INTO subscriptions (user_id, project_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (user_id, project_id))
        elif action == "unsub":
            cur.execute("""
                DELETE FROM subscriptions
                WHERE user_id = %s AND project_id = %s;
            """, (user_id, project_id))

    await start(update, context)  # Refresh buttons

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_buttons))

# --- Webhook endpoint for announcements ---
@app.route("/hook/<key>", methods=["POST"])
def webhook(key):
    if key != "your_custom_webhook_key":
        return "Unauthorized", 403
    data = request.json
    text = data.get("content")
    if text:
        telegram_app.create_task(broadcast_announcement(text))
    return "OK", 200

# --- Broadcast to all subscribed users ---
async def broadcast_announcement(message: str):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT user_id FROM subscriptions;
        """)
        user_ids = [row["user_id"] for row in cur.fetchall()]

    for user_id in user_ids:
        try:
            await telegram_app.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")

# --- Run bot and init ---
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

async def run_bot():
    await telegram_app.initialize()
    await telegram_app.start()
    print("✅ Bot is running...")
    await telegram_app.updater.start_polling()
    await telegram_app.updater.idle()

if __name__ == "__main__":
    init_db()
    import threading
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)

