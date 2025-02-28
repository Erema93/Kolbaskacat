import os
import telebot
import schedule
import time
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = "7938046164:AAF77xQmwN1a3Hph19M6e-B0FiWB9UUzcYw"
CHAT_ID = "7938046164"  

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! 🐱 Я буду отправлять тебе сказки про котов-колбасок каждый день в 22:00!")

def send_tales():
    tale1 = "🐱 История 1: Приключения котов-колбасок..."
    tale2 = "🐱 История 2: Сладкий мир котов-колбасок..."
    bot.send_message(CHAT_ID, tale1)
    bot.send_message(CHAT_ID, tale2)

schedule.every().day.at("22:00").do(send_tales)

def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_bot, daemon=True).start()  # daemon=True 

@app.route('/')
def index():
    return "Бот работает!"

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting app on port {port}")  # Логируем, на каком порту запускается сервер
    

    app.run(host="0.0.0.0", port=port)







