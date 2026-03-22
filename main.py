import os
import asyncio
import threading
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from supabase import create_client, Client

# --- CONFIGURAÇÃO DE LOGS (Para aparecer no Render) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SERVIDOR WEB (Para o Render não dar erro de porta) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Social Earn Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÃO DAS VARIÁVEIS DO RENDER ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# URL OFICIAL (Sem a barra no fim para evitar erro 404)
WEBAPP_URL = "https://social-earn-app.vercel.app"

# Verificação de segurança nos Logs do Render
if not TOKEN:
    logger.error("❌ ERRO: Variável TELEGRAM_TOKEN não encontrada!")
else:
    logger.info(f"✅ Token detetado: {TOKEN[:5]}***")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ ERRO: Credenciais do Supabase em falta!")

# Inicialização
bot = Bot(token=TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    
    logger.info(f"Recibi /start de {username} ({user_id})")

    # Lógica de Registo no Supabase
    try:
        res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if not res.data:
            supabase.table("profiles").insert({
                "id": user_id, 
                "username": username, 
                "points": 50
            }).execute()
            msg_text = f"🚀 Bem-vindo ao Social Earn, {username}!\n\nGanhaste 50 XP de bónus!"
        else:
            msg_text = f"Olá {username}! Pronto para ganhar mais?"
    except Exception as e:
        logger.error(f"Erro no Supabase: {e}")
        msg_text = "Bem-vindo de volta!"

    # Botão que abre o Mini App
    kb = [[types.InlineKeyboardButton(
        text="🚀 Abrir Social Earn", 
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )]]
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer(msg_text, reply_markup=reply_markup)

async def main():
    logger.info("🤖 Bot a iniciar Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # 1. Inicia o Flask numa thread separada
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Inicia o Bot
    asyncio.run(main())
