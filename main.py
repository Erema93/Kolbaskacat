import telebot
import schedule
import time

TOKEN = "7938046164:AAF77xQmwN1a3Hph19M6e-B0FiWB9UUzcYw"
CHAT_ID = "7938046164"

bot = telebot.TeleBot(TOKEN)

# Ответ на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! 🐱 Я буду отправлять тебе сказки про котов-колбасок каждый день в 22:00!")

# Функция для отправки сказок
def send_tales():
    tale1 = "🐱 История 1: Приключения котов-колбасок..."
    tale2 = "🐱 История 2: Сладкий мир котов-колбасок..."
    bot.send_message(CHAT_ID, tale1)
    bot.send_message(CHAT_ID, tale2)

# Запланировать отправку в 22:00 каждый день
schedule.every().day.at("22:00").do(send_tales)

# Запускаем бота
def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(60)

import threading
threading.Thread(target=run_bot).start()
bot.polling(none_stop=True)



