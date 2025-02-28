import os
import telebot
import schedule
import time
import threading

TOKEN = "7938046164:AAF77xQmwN1a3Hph19M6e-B0FiWB9UUzcYw"
CHAT_ID = "ВАШ_ПРАВИЛЬНЫЙ_CHAT_ID"  # Замените на правильный chat_id

bot = telebot.TeleBot(TOKEN)

# Ответ на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! 🐱 Я буду отправлять тебе сказки про котов-колбасок каждый день в 22:00!")

# Функция для отправки сказок
def send_tales():
    print("Отправляю сказки...")  # Логируем вызов функции
    try:
        tale1 = "🐱 История 1: Приключения котов-колбасок..."
        tale2 = "🐱 История 2: Сладкий мир котов-колбасок..."
        bot.send_message(CHAT_ID, tale1)
        bot.send_message(CHAT_ID, tale2)
    except Exception as e:
        print(f"Ошибка при отправке сказок: {e}")

# Запланировать отправку в 22:00 каждый день
schedule.every().day.at("22:00").do(send_tales)

# Запускаем бота
def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_bot).start()

# Главный маршрут Flask
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает!"

if __name__ == "__main__":
    # Получаем порт из окружения или по умолчанию 5000
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting app on port {port}")  # Логируем, на каком порту запускается сервер
    
    # Запускаем приложение на всех интерфейсах (0.0.0.0) и на правильном порту
    app.run(host="0.0.0.0", port=port)







