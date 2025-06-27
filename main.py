import os
import threading
import asyncio
import psycopg2
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# --- Environment Setup ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")  # Example: postgres://user:pass@host:port/dbname

if not BOT_TOKEN or not DATABASE_URL:
    raise RuntimeError("❌ BOT_TOKEN or DATABASE_URL not set in environment variables.")

# --- DB Setup ---
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def ensure_tables_exist():
    with get_db_connection() as conn:
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
                    project_id INTEGER NOT NULL REFERENCES projects(id)
                );
            """)
        conn.commit()

ensure_tables_exist()

# --- Flask Setup ---
app = Flask(__name__)

# --- Telegram Bot Setup ---
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Helper Functions ---
def get_projects():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM projects ORDER BY name;")
            return cur.fetchall()

def get_user_subscriptions(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.name FROM subscriptions s
                JOIN projects p ON s.project_id = p.id
                WHERE s.user_id = %s;
            """, (user_id,))
            return [row[0] for row in cur.fetchall()]

def toggle_subscription(user_id, project_name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get project ID
            cur.execute("SELECT id FROM projects WHERE name = %s;", (project_name,))
            result = cur.fetchone()
            if not result:
                return
            project_id = result[0]

            # Check if already subscribed
            cur.execute("""
                SELECT id FROM subscriptions WHERE user_id = %s AND project_id = %s;
            """, (user_id, project_id))
            exists = cur.fetchone()

            if exists:
                cur.execute("DELETE FROM subscriptions WHERE id = %s;", (exists[0],))
                conn.commit()
                return False
            else:
                cur.execute("""
                    INSERT INTO subscriptions (user_id, project_id) VALUES (%s, %s);
                """, (user_id, project_id))
                conn.commit()
                return True

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscriptions = get_user_subscriptions(user_id)
    buttons = []

    for _, project_name in get_projects():
        is_subscribed = project_name in subscriptions
        label = f"✅ {project_name}" if is_subscribed else f"❌ {project_name}"
        buttons.append([InlineKeyboardButton(label, callback_data=project_name)])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Select projects to (un)subscribe:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    project_name = query.data

    subscribed = toggle_subscription(user_id, project_name)
    status = "Subscribed ✅" if subscribed else "Unsubscribed ❌"

    subscriptions = get_user_subscriptions(user_id)
    buttons = []
    for _, name in get_projects():
        label = f"✅ {name}" if name in subscriptions else f"❌ {name}"
        buttons.append([InlineKeyboardButton(label, callback_data=name)])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(f"{status}\n\nSelect projects:", reply_markup=reply_markup)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_buttons))

# --- Webhook for Announcements ---
@app.route("/hook/<key>", methods=["POST"])
def webhook(key):
    if key != "your_custom_webhook_key":
        return "Unauthorized", 403
    data = request.json
    text = data.get("content")
    if text:
        telegram_app.create_task(broadcast_announcement(text))
    return "OK", 200

async def broadcast_announcement(message: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT user_id FROM subscriptions;")
            chat_ids = [row[0] for row in cur.fetchall()]
    for chat_id in chat_ids:
        try:
            await telegram_app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}")

# --- Bot Runner ---
async def run_bot():
    await telegram_app.initialize()
    await telegram_app.start()
    print("✅ Bot is running...")
    await telegram_app.run_polling()

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

threading.Thread(target=start_bot).start()

# --- Flask Entry Point ---
@app.route("/")
def index():
    return "Bot is running", 200
