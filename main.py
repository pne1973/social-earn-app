import os
import telebot
from supabase import create_client

# --- CONFIGURAÇÃO (Lê as chaves do painel Environment Variables) ---
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VERCEL_LINK = os.getenv("VERCEL_LINK")

# Inicialização do Bot e do Supabase
bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username or ""
    lang_code = message.from_user.language_code or 'pt'

    # 1. Registar ou Atualizar o utilizador no Supabase
    try:
        supabase.table('profiles').upsert({
            'id': user_id, 
            'username': username, 
            'lang': lang_code
        }).execute()
        print(f"Utilizador {user_id} registado com sucesso.")
    except Exception as e:
        print(f"Erro ao conectar ao Supabase: {e}")

    # 2. Definir Mensagens (Português vs Inglês)
    if lang_code.startswith('pt'):
        txt = f"Olá {first_name}! 👋\n\nBem-vindo à nossa rede social! Aqui ganhas pontos por interagir. 1000 pontos valem 0,75€ via PayPal.\n\nClica no botão abaixo para começar!"
        btn_txt = "Abrir Rede Social 🚀"
    else:
        txt = f"Hello {first_name}! 👋\n\nWelcome to our social network! Earn points by interacting. 1000 points = €0.75 via PayPal.\n\nClick the button below to start!"
        btn_txt = "Open Social App 🚀"

    # 3. Criar o Botão do Mini App
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(VERCEL_LINK)
    markup.add(telebot.types.InlineKeyboardButton(text=btn_txt, web_app=web_app))

    # 4. Enviar Resposta
    bot.send_message(message.chat.id, txt, reply_markup=markup)

# Iniciar o Bot
if __name__ == "__main__":
    print("O Bot @socialntworkbot está ONLINE!")
    bot.polling(none_stop=True)
