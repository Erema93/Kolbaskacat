import telebot
import schedule
import time

TOKEN = "7938046164:AAHKw2wmUyBuziXuy0lPlkYXQQgH4D3wmzA"
CHAT_ID = "7938046164"

bot = telebot.TeleBot(TOKEN)

def send_tales():
    tale1 = "🐱 История 1: Приключения котов-колбасок..."
    tale2 = "🐱 История 2: Сладкий мир котов-колбасок..."
    bot.send_message(CHAT_ID, tale1)
    bot.send_message(CHAT_ID, tale2)

schedule.every().day.at("22:00").do(send_tales)

while True:
    schedule.run_pending()
    time.sleep(60)

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render выдаёт порт
    app.run(host="0.0.0.0", port=port)
