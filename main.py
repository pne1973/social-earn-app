import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from supabase import create_client, Client

# CONFIGURAÇÕES
TOKEN = "TEU_TOKEN_DO_BOT"
SUPABASE_URL = "https://fickstyevektwbgimapy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # A mesma chave do index.html
WEBAPP_URL = "https://teu-site-vercel.app" # URL do teu Mini App

bot = Bot(token=TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    # Verifica se veio de um convite (o parâmetro vem após o /start)
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None

    # Tenta buscar o perfil no Supabase
    res = supabase.table("profiles").select("*").eq("id", user_id).execute()
    
    if not res.data:
        # NOVO UTILIZADOR: Criar conta e dar bónus de boas-vindas
        bonus_inicial = 50 # Exemplo: 50 pontos por entrar
        data = {
            "id": user_id,
            "username": username,
            "points": bonus_inicial,
            "referred_by": referrer_id
        }
        supabase.table("profiles").insert(data).execute()
        
        texto_boas_vindas = f"👋 Bem-vindo ao Social Earn!\n\nRecebeste {bonus_inicial} XP de bónus de boas-vindas."
        
        # Se foi convidado, avisar o amigo (opcional)
        if referrer_id:
            try:
                # Dar bónus ao amigo que convidou (ex: +100 pontos)
                res_ref = supabase.table("profiles").select("points").eq("id", referrer_id).execute()
                if res_ref.data:
                    novos_pontos = res_ref.data[0]['points'] + 100
                    supabase.table("profiles").update({"points": novos_pontos}).eq("id", referrer_id).execute()
                    await bot.send_message(referrer_id, f"🎊 Alguém entrou com o teu link! Ganhaste +100 XP.")
            except:
                pass
    else:
        texto_boas_vindas = "Bem-vindo de volta à tua rede social favorita!"

    # Botão para abrir o Mini App
    kb = [
        [types.InlineKeyboardButton(text="🚀 Abrir Social Earn", web_app=types.WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer(texto_boas_vindas, reply_markup=reply_markup)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
