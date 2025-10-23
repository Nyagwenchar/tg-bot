import os
import threading
from bot import run_bot
from admin import run_admin
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Starting Crypto Store Bot and Admin Panel...")
    print("=" * 50)
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("✅ Telegram bot started")
    
    print("✅ Admin panel starting on http://0.0.0.0:5000")
    print("=" * 50)
    run_admin()

if __name__ == '__main__':
    main()
