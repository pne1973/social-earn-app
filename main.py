import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from supabase import create_client, Client
from urllib.parse import urlencode

app = Flask(__name__)

@app.route('/')
def home(): return "Social Network Bot Online!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# LÊ AS KEYS EXATAMENTE COMO ESTÃO NO ENVIRONMENT DO RENDER
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BASE_WEBAPP_URL = "https://social-earn-app.vercel.app"

bot = Bot(token=TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    
    # Regista o utilizador na tabela 'profiles'
    try:
        supabase.table("profiles").upsert({"id": user_id, "username": username, "points": 50}).execute()
    except Exception as e:
        print(f"Erro Supabase: {e}")

    # Envia as chaves via URL para o index.html ler
    params = {
        "url": SUPABASE_URL,
        "key": SUPABASE_KEY
    }
    final_url = f"{BASE_WEBAPP_URL}?{urlencode(params)}"

    kb = [[types.InlineKeyboardButton(text="🏠 Entrar na Rede Social", web_app=types.WebAppInfo(url=final_url))]]
    
    await message.answer(
        f"Bem-vindo à Social Network, {username}!\n\nGanhe XP publicando e interagindo com a comunidade.", 
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
    )

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("🤖 Bot a iniciar Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
