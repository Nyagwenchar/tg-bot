import os
import asyncio
import nest_asyncio
from threading import Thread
from bot import run_bot
from admin import run_admin
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

def run_admin_thread():
    run_admin()

def main():
    print("Starting Crypto Store Bot and Admin Panel...")
    print("=" * 50)
    
    print("✅ Admin panel starting on http://0.0.0.0:5000")
    admin_thread = Thread(target=run_admin_thread, daemon=True)
    admin_thread.start()
    
    print("✅ Telegram bot starting...")
    print("=" * 50)
    asyncio.run(run_bot())

if __name__ == '__main__':
    main()
