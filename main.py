import os, asyncio, threading, requests, time
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from supabase import create_client, Client
from urllib.parse import urlencode

app = Flask(__name__)
@app.route('/')
def home(): return "SERVER LIVE"

def keep_alive():
    # Tenta usar o URL real do Render para o servidor não dormir
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')}"
    while True:
        try: requests.get(url); print("Ping OK")
        except: print("Ping Fail")
        time.sleep(600)

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
bot = Bot(token=TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    supabase.table("profiles").upsert({"id": user_id, "username": username, "points": 50}).execute()
    
    params = urlencode({"url": SUPABASE_URL, "key": SUPABASE_KEY})
    url = f"https://social-earn-app.vercel.app?{params}"
    
    kb = [[types.InlineKeyboardButton(text="📱 Abrir Social Network", web_app=types.WebAppInfo(url=url))]]
    await message.answer(f"Olá {username}! Bem-vindo.", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

async def main():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
