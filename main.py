import os
import telebot
from telebot import types
from supabase import create_client

# Configurações das Variáveis de Ambiente
TOKEN = os.getenv('BOT_TOKEN')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
VERCEL_LINK = os.getenv('VERCEL_LINK')

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Utilizador"
    
    # Registar ou atualizar o utilizador no Supabase
    try:
        supabase.table("profiles").upsert({
            "id": user_id, 
            "username": username
        }).execute()
    except Exception as e:
        print(f"Erro Supabase: {e}")

    # Criar o botão para abrir o Mini App
    markup = types.InlineKeyboardMarkup()
    web_app = types.WebAppInfo(VERCEL_LINK)
    menu_button = types.InlineKeyboardButton("Abrir Rede Social 🚀", web_app=web_app)
    markup.add(menu_button)

    texto = f"Olá {username}! 👋\n\nBem-vindo à Social Earn. Ganhe pontos interagindo com a nossa comunidade!\n\nClique no botão abaixo para começar:"
    bot.send_message(message.chat.id, texto, reply_markup=markup)

# Iniciar o Bot
if __name__ == "__main__":
    print("Bot a correr...")
    bot.infinity_polling()
