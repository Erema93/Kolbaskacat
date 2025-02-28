import os
import telebot
import schedule
import time
import threading
from flask import Flask

# Конфигурация
TOKEN = "7149701343:AAHj3tT3KFlN5YXUQdTxSbNkDcGPyt3vjjY"
CHAT_ID = "7149701343"  # Замените на реальный chat_id (числовой, например: -123456789)

# Инициализация бота
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, "Привет! 🐱 Я буду отправлять тебе сказки про котов-колбасок каждый день в 22:00!")
    except Exception as e:
        print(f"Ошибка при отправке приветственного сообщения: {e}")

# Функция отправки сказок
def send_tales():
    print("Отправляю сказки...")
    try:
        tale1 = "🐱 История 1: Приключения котов-колбасок..."
        tale2 = "🐱 История 2: Сладкий мир котов-колбасок..."
        bot.send_message(CHAT_ID, tale1)
        time.sleep(1)  # Небольшая задержка между сообщениями
        bot.send_message(CHAT_ID, tale2)
    except Exception as e:
        print(f"Ошибка при отправке сказок: {e}")

# Функция для запуска планировщика
def run_scheduler():
    # Запланировать отправку на 22:00 каждый день (вместо каждых 1 минут)
    schedule.every().day.at("01:30").do(send_tales)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Проверка каждую минуту
        except Exception as e:
            print(f"Ошибка в планировщике: {e}")
            time.sleep(60)  # Продолжаем цикл даже при ошибке

# Функция для запуска бота polling
def run_bot_polling():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка в polling: {e}")
        time.sleep(5)  # Перезапуск через 5 секунд при ошибке
        run_bot_polling()  # Рекурсивный перезапуск

# Главный маршрут Flask
@app.route('/')
def index():
    return "Бот работает!"

if __name__ == "__main__":
    # Получаем порт из окружения или по умолчанию 5000
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting app on port {port}")
    
    # Запускаем процессы в отдельных потоках
    bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    
    bot_thread.start()
    scheduler_thread.start()
    
    # Запускаем Flask
    app.run(host="0.0.0.0", port=port)





