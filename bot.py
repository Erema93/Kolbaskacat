import os
import logging
import random
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes, TypeHandler
)

# Загружаем переменные окружения из .env (если локально)
load_dotenv()

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TOKEN = os.getenv("8012532063:AAGNNZ7XkdLQU_-sMR2SG9tLb1ZICVLOSWo")
ADMIN_CHAT_ID = os.getenv("572255263")
RENDER_HOSTNAME = os.getenv("aquanorma.onrender.com")

# Проверяем, что переменные окружения заданы
if not TOKEN:
    raise ValueError("❌ Токен не задан! Укажите переменную окружения TOKEN.")
if not ADMIN_CHAT_ID:
    raise ValueError("❌ ADMIN_CHAT_ID не задан! Укажите переменную окружения ADMIN_CHAT_ID.")
if not RENDER_HOSTNAME:
    raise ValueError("❌ RENDER_EXTERNAL_HOSTNAME не задан! Укажите переменную окружения RENDER_EXTERNAL_HOSTNAME.")

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)  # Приведение к int
except ValueError:
    raise ValueError("❌ ADMIN_CHAT_ID должен быть числом!")

# Состояния в разговоре
NAME, PHONE, ADDRESS, SERVICE = range(4)

SERVICES = [
    "Поверка счетчиков тепла",
    "Замена счетчиков воды",
    "Поверка счетчиков воды"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога"""
    await update.message.reply_text(
        "Здравствуйте! Я бот для приема заявок. Давайте начнем.\nКак вас зовут?"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем имя пользователя"""
