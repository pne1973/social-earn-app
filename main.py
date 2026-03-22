import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from supabase import create_client, Client

# --- SERVIDOR WEB (Para manter o Render ativo) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Social Earn Bot is Online!"

def run_flask():
    # O Render atribui uma porta automaticamente na variável PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÃO USANDO AS TUAS VARIÁVEIS DO RENDER ---
# Aqui usamos exatamente 'TELEGRAM_TOKEN' como pediste
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# URL do teu Mini App (Vercel ou GitHub Pages)
WEBAPP_URL = "https://socialntworkbot-mini-app.vercel.app" 

bot = Bot(token=TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    
    # Captura o ID de quem convidou (parâmetro start=...)
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None

    try:
        # Verifica se o utilizador já existe
        res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if not res.data:
            # NOVO UTILIZADOR: Criar conta com bónus inicial
            bonus_welcome = 50
            data = {
                "id": user_id,
                "username": username,
                "points": bonus_welcome,
                "referred_by": referrer_id
            }
            supabase.table("profiles").insert(data).execute()
            
            msg_text = f"🚀 Bem-vindo ao Social Earn, {username}!\n\nRecebeste {bonus_welcome} XP de bónus inicial."
            
            # Bónus para quem convidou
            if referrer_id and referrer_id.isdigit():
                try:
                    ref_id = int(referrer_id)
                    ref_res = supabase.table("profiles").select("points").eq("id", ref_id).execute()
                    if ref_res.data:
                        novos_pts = ref_res.data[0]['points'] + 100
                        supabase.table("profiles").update({"points": novos_pts}).eq("id", ref_id).execute()
                        await bot.send_message(ref_id, "🎊 Alguém entrou com o teu link! Ganhaste +100 XP.")
                except:
                    pass
        else:
            msg_text = f"Olá {username}! Vamos ganhar mais pontos hoje?"

    except Exception as e:
        print(f"Erro: {e}")
        msg_text = "Bem-vindo ao Social Earn!"

    # Botão para abrir o Mini App
    kb = [[types.InlineKeyboardButton(text="🚀 Abrir Social Earn", web_app=types.WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer(msg_text, reply_markup=reply_markup)

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Inicia o Flask para o Render detetar a porta aberta
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Inicia o Bot do Telegram
    asyncio.run(run_bot())
