import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# --- CONFIGURAÇÃO PARA MANTER O BOT VIVO NO RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "O Bot está online e o servidor Flask está a responder!"

def run():
    # O Render injeta automaticamente a variável de ambiente PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------------------------------

# Configurações do Bot (Lidas do Environment do Render)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
# Link correto: https://social-earn-app-joaopinheiro1973.vercel.app
VERCEL_LINK = os.environ.get("VERCEL_LINK") 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username or "Utilizador"
    
    texto = (
        f"Olá {username}! 👋\n\n"
        "Bem-vindo à **Social Earn**. Ganha pontos e dinheiro real!\n\n"
        "💰 **1000 pontos = 0.75€**\n\n"
        "Clica no botão abaixo para abrir a tua carteira:"
    )

    markup = types.InlineKeyboardMarkup()
    # Cria o botão de Mini App
    web_app = types.WebAppInfo(VERCEL_LINK)
    botao = types.InlineKeyboardButton("Abrir Rede Social 🚀", web_app=web_app)
    markup.add(botao)

    bot.send_message(message.chat.id, texto, reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    # Inicia o servidor Flask em segundo plano antes do polling
    keep_alive()
    print("Servidor Flask e Bot iniciados...")
    bot.polling(non_stop=True)
