import os
import telebot
import schedule
import time
import threading
from flask import Flask

TOKEN = "7149701343:AAHj3tT3KFlN5YXUQdTxSbNkDcGPyt3vjjY"
CHAT_ID = "7149701343"  # Замените на правильный chat_id

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

# Запланировать отправку каждые 1 минуту (для теста)
schedule.every(1).minutes.do(send_tales)

# Запускаем бота в отдельном потоке
def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Главный маршрут Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает!"

if __name__ == "__main__":
    # Получаем порт из окружения или по умолчанию 5000
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting app on port {port}")  # Логируем, на каком порту запускается сервер
    
    # Запускаем приложение на всех интерфейсах (0.0.0.0) и на правильном порту
    threading.Thread(target=run_bot).start()  # Запускаем бота в фоновом режиме
    app.run(host="0.0.0.0", port=port)







