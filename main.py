import os
import telebot
import schedule
import time
import threading
from flask import Flask, request
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "7149701343:AAHj3tT3KFlN5YXUQdTxSbNkDcGPyt3vjjY"
CHAT_ID = "7149701343"  # Замените на реальный chat_id (числовой)

# Инициализация бота и Flask
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, "Привет! 🐱 Я буду отправлять тебе сказки про котов-колбасок каждый день в 22:00!")
    except Exception as e:
        logger.error(f"Ошибка при отправке приветственного сообщения: {e}")

# Функция отправки сказок
def send_tales():
    logger.info("Отправляю сказки...")
    try:
        tale1 = "🐱 История 1: Приключения котов-колбасок..."
        tale2 = "🐱 История 2: Сладкий мир котов-колбасок..."
        bot.send_message(CHAT_ID, tale1)
        time.sleep(1)  # Задержка между сообщениями
        bot.send_message(CHAT_ID, tale2)
    except Exception as e:
        logger.error(f"Ошибка при отправке сказок: {e}")

# Функция для планировщика
def run_scheduler():
    schedule.every().day.at("22:00").do(send_tales)
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")
            time.sleep(60)

# Маршрут для вебхуков Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        if request.headers.get("content-type") == "application/json":
            json_string = request.get_data().decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return "", 200
        else:
            return "", 403
    except Exception as e:
        logger.error(f"Ошибка в вебхуке: {e}")
        return "", 500

# Главный маршрут для проверки статуса
@app.route("/")
def index():
    return "Бот работает!"

def set_webhook():
    # Установка вебхука
    port = int(os.environ.get("PORT", 10000))
    # Предполагаем, что Render предоставляет внешний URL в формате <service-name>.onrender.com
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    
    # Удаляем старый вебхук, если он есть
    bot.remove_webhook()
    time.sleep(1)  # Даем время на удаление
    
    # Устанавливаем новый вебхук
    bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting app on port {port}")

    # Устанавливаем вебхук
    set_webhook()

    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Запускаем Flask сервер
    app.run(host="0.0.0.0", port=port)



