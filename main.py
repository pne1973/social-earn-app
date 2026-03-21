import telebot
from supabase import create_client

# DADOS DE ACESSO
TOKEN = "SEU_TOKEN_BOTFATHER"
URL = "SUA_URL_SUPABASE"
KEY = "SUA_KEY_SUPABASE"
VERCEL_LINK = "https://seu-projeto.vercel.app"

bot = telebot.TeleBot(TOKEN)
supabase = create_client(URL, KEY)

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.from_user.id
    uname = message.from_user.first_name
    lang = message.from_user.language_code or 'en'

    # Criar utilizador se não existir
    supabase.table('profiles').upsert({
        'id': uid, 
        'username': uname, 
        'lang': lang
    }).execute()

    # Mensagens traduzidas
    txt = {
        'pt': f"Olá {uname}! Pronto para ganhar com a nossa rede?",
        'en': f"Hello {uname}! Ready to earn with our network?",
    }.get(lang[:2], "Hello!")

    btn_txt = "Abrir Rede Social" if lang[:2] == 'pt' else "Open Social App"

    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(VERCEL_LINK)
    markup.add(telebot.types.InlineKeyboardButton(btn_txt, web_app=web_app))

    bot.send_message(message.chat.id, txt, reply_markup=markup)

bot.polling()
