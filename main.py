import os
import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# === Load environment variable ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Flask web app (to keep Render web service alive) ===
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Nadregator Bot is up and running!"

# === Telegram Bot Handler ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Nadregator bot is working.")

# === Bot startup coroutine ===
async def run_bot():
    print("🚀 Entered run_bot()")
    try:
        print("✅ Starting Telegram bot...")
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))

        await application.initialize()
        await application.start()
        print("✅ Bot polling started.")
        await application.updater.start_polling()
        await application.updater.idle()
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")

# === Main app entry point ===
if __name__ == "__main__":
    print("🔧 main.py is running")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(run_bot())
        print("📡 run_bot() was scheduled")
    except Exception as e:
        print(f"❌ Failed to schedule run_bot(): {e}")

    app.run(host="0.0.0.0", port=10000)
