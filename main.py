import os
import telebot
import schedule
import time
from flask import Flask

TOKEN = os.getenv("TOKEN")  # 7938046164:AAF77xQmwN1a3Hph19M6e-B0FiWB9UUzcYw
CHAT_ID = os.getenv("CHAT_ID")  # 7938046164

bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! 🐱 Я бот, который будет отправлять тебе сказки про котов-колбасок каждую ночь в 22:00! 🎉")

# Функция отправки сказок
def send_tales():
    bot.send_message(CHAT_ID, "📖 Вот твои сказки на сегодня!")
    bot.send_message(CHAT_ID, "🐱 Сказка 1: Печенье-великан...")
    bot.send_message(CHAT_ID, "🐱 Сказка 2: Конфетный лабиринт...")

# Запускаем задачу по расписанию
schedule.every().day.at("22:00").do(send_tales)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

import threading
threading.Thread(target=run_scheduler).start()

# Создаём Flask-сервер (чтобы Render не ругался)
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render выдаёт порт
    app.run(host="0.0.0.0", port=port)
    bot.polling(none_stop=True)



