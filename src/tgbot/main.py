import telebot
from telebot import types
import os

token = os.getenv("API_TOKEN")

bot = telebot.TeleBot(token)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "Привет! Я — телеграм-бот, который поможет тебе обработать "
        "видео шахматной партии: добавлю озвучку и субтитры на выбранном тобой языке!\n\n"
        "Выбери стиль обработки видео:"
    )

    # Создаём инлайн-кнопки
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎓 Обучающий стиль", callback_data="style_educational")
    btn2 = types.InlineKeyboardButton("😂 Развлекательный стиль", callback_data="style_funny")
    markup.add(btn1, btn2)

    # Отправляем сообщение с кнопками
    bot.send_message(message.chat.id, text, reply_markup=markup)

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "style_educational":
        bot.send_message(call.message.chat.id, "Выбран обучающий стиль. Отлично!")
        # здесь можно продолжить сценарий — предложить выбрать язык, тип озвучки и т.д.
    elif call.data == "style_funny":
        bot.send_message(call.message.chat.id, "Выбран развлекательный стиль. Готовим мемы!")
        # аналогично — можно продолжить опрос

# Обработчик всех других сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Пожалуйста, выбери стиль обработки через /start.")

bot.infinity_polling() #! DONT_TOUCH_PLS