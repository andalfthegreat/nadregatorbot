import os
import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# === Load environment variable ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Flask app ===
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Nadregator Bot is up and running!"

# === Telegram command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Nadregator bot is working.")

# === Bot startup ===
async def run_bot():
    print("🚀 Entered run_bot()")
    try:
        app_builder = ApplicationBuilder().token(BOT_TOKEN)
        application = app_builder.build()
        application.add_handler(CommandHandler("start", start))
        print("✅ Bot polling starting...")
        await application.run_polling()
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")

# === Launch bot in separate thread ===
def launch_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

if __name__ == "__main__":
    print("🔧 main.py is running")

    # Run bot in parallel to Flask
    import threading
    threading.Thread(target=launch_async_loop).start()
    print("📡 run_bot() thread started")

    app.run(host="0.0.0.0", port=10000)

