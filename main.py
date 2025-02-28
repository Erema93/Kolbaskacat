import os
import telebot
import schedule
import time
import threading
from flask import Flask, request
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "7149701343:AAHj3tT3KFlN5YXUQdTxSbNkDcGPyt3vjjY"
# Замените на реальный chat_id (числовой, например, 123456789 или -100123456789 для групп)
CHAT_ID = "7149701343"  # Пока None, нужно указать после получения реального ID

# Инициализация бота и Flask
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Список случайных сказок
TALES = [
    "🐱 Однажды кот-колбаска отправился в колбасный лес и нашел волшебную сосиску...",
    "🐱 В далекой колбасной стране кот-колбаска подружился с сырным драконом...",
    "🐱 Кот-колбаска решил устроить пир для всех своих мясных друзей...",
    "🐱 В темной колбасной пещере кот-колбаска нашел сокровище из ветчины...",
    "🐱 Кот-колбаска изобрел машину, которая превращает хлеб в колбасу..."
]

# Функция для создания кнопки
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Сказка", callback_data="tell_tale"))
    return markup

# Обработчик команды /start с кнопкой
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        # Сохраняем chat_id для использования в ежедневных сказках, если он еще не задан
        global CHAT_ID
        if CHAT_ID is None:
            CHAT_ID = message.chat.id
            logger.info(f"Установлен CHAT_ID: {CHAT_ID}")
        
        bot.send_message(
            message.chat.id,
            "Привет! 🐱 Я буду отправлять тебе случайные сказки про котов-колбасок каждый день в 22:00! "
            "А еще можешь нажать кнопку ниже, чтобы услышать сказку прямо сейчас!",
            reply_markup=gen_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке приветственного сообщения: {e}")

# Обработчик нажатия кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "tell_tale":
        try:
            # Выбираем случайную сказку из списка
            tale = random.choice(TALES)
            bot.send_message(call.message.chat.id, tale)
            # Предлагаем кнопку снова
            bot.send_message(call.message.chat.id, "Хочешь еще одну?", reply_markup=gen_markup())
        except Exception as e:
            logger.error(f"Ошибка при отправке сказки по кнопке: {e}")

# Функция отправки ежедневных случайных сказок
def send_tales():
    logger.info("Отправляю ежедневные сказки...")
    if CHAT_ID is None:
        logger.error("CHAT_ID не установлен! Сказки не отправлены.")
        return
    try:
        # Выбираем две случайные сказки
        tale1 = random.choice(TALES)
        tale2 = random.choice(TALES)
        bot.send_message(CHAT_ID, tale1)
        time.sleep(1)  # Задержка между сообщениями
        bot.send_message(CHAT_ID, tale2)
    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневных сказок: {e}")

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

# Установка вебхука
def set_webhook():
    port = int(os.environ.get("PORT", 10000))
    # Предполагаем, что Render или другой сервис предоставляет внешний URL
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'your-service.onrender.com')}/{TOKEN}"
    
    try:
        bot.remove_webhook()
        time.sleep(1)  # Даем время на удаление
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook установлен: {webhook_url}")
    except Exception as e:
        logger.error(f"Ошибка при установке вебхука: {e}")

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

    # Для локального теста закомментируйте set_webhook() и раскомментируйте ниже:
    # bot.remove_webhook()
    # bot.polling(none_stop=True)



