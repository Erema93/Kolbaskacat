import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not load_dotenv(dotenv_path):
    logger.error("Не удалось загрузить файл .env. Убедитесь, что файл существует.")

# Получаем переменные окружения
TOKEN = os.getenv("8012532063:AAGNNZ7XkdLQU_-sMR2SG9tLb1ZICVLOSWo")
ADMIN_CHAT_ID = os.getenv("572255263")
RENDER_HOSTNAME = os.getenv("aquanorma.onrender.com")

# Отладочные сообщения для проверки значений переменных окружения
logger.info(f"TOKEN: {TOKEN}")
logger.info(f"ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
logger.info(f"RENDER_HOSTNAME: {RENDER_HOSTNAME}")

# Проверяем, что переменные окружения заданы
if not TOKEN:
    logger.error("❌ Токен не задан! Укажите переменную окружения TOKEN.")
    raise ValueError("❌ Токен не задан! Укажите переменную окружения TOKEN.")
if not ADMIN_CHAT_ID:
    logger.error("❌ ADMIN_CHAT_ID не задан! Укажите переменную окружения ADMIN_CHAT_ID.")
    raise ValueError("❌ ADMIN_CHAT_ID не задан! Укажите переменную окружения ADMIN_CHAT_ID.")
if not RENDER_HOSTNAME:
    logger.error("❌ RENDER_EXTERNAL_HOSTNAME не задан! Укажите переменную окружения RENDER_EXTERNAL_HOSTNAME.")
    raise ValueError("❌ RENDER_EXTERNAL_HOSTNAME не задан! Укажите переменную окружения RENDER_EXTERNAL_HOSTNAME.")

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)  # Приведение к int
except ValueError:
    logger.error("❌ ADMIN_CHAT_ID должен быть числом!")
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
    user = update.message.from_user
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Приятно познакомиться, {context.user_data['name']}! Укажите, пожалуйста, ваш номер телефона."
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем телефон пользователя"""
    context.user_data["phone"] = update.message.text
    await update.message.reply_text(
        "Спасибо! Теперь укажите ваш адрес."
    )
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем адрес пользователя"""
    context.user_data["address"] = update.message.text
    await update.message.reply_text(
        "Отлично! Теперь выберите услугу из списка ниже.",
        reply_markup=ReplyKeyboardMarkup([SERVICES], one_time_keyboard=True)
    )
    return SERVICE

async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем выбранную услугу"""
    context.user_data["service"] = update.message.text
    await update.message.reply_text(
        "Спасибо за предоставленную информацию! Ваша заявка принята.",
        reply_markup=ReplyKeyboardRemove()
    )

    # Отправка уведомления админу
    admin_message = (
        f"Новая заявка от {context.user_data['name']}:\n"
        f"Телефон: {context.user_data['phone']}\n"
        f"Адрес: {context.user_data['address']}\n"
        f"Услуга: {context.user_data['service']}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    return ConversationHandler.END

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)]
        },
        fallbacks=[CommandHandler("cancel", lambda update, context: ConversationHandler.END)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
