import os
import logging
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7831214357:AAHNlb2lXwoLks9eN7JnQ1SRDEd6zOgXe-U"  # Твой токен
ADMIN_CHAT_ID = "572255263"  # Твой Telegram ID

# Убери проверку, если токен задан вручную
# if not TOKEN:
#     raise ValueError("Токен не задан в переменных окружения. Укажи переменную TOKEN.")

if not TOKEN:
    raise ValueError("Токен не задан в переменных окружения. Укажи переменную TOKEN.")

NAME, PHONE, ADDRESS, SERVICE = range(4)

SERVICES = [
    "Поверка счетчиков тепла",
    "Замена счетчиков воды",
    "Поверка счетчиков воды"
]

request_counter = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Здравствуйте! Я бот для приема заявок. Давайте начнем.\nКак вас зовут?"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Укажите ваш номер телефона (например, +79991234567):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Укажите адрес, где нужно выполнить работы:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['address'] = update.message.text
    reply_keyboard = [[service] for service in SERVICES]
    await update.message.reply_text(
        "Выберите вид работ:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SERVICE

async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global request_counter
    context.user_data['service'] = update.message.text
    user_data = context.user_data

    request_counter += 1
    request_id = f"Заявка-{request_counter}-{random.randint(100, 999)}"

    message_to_admin = (
        f"Новая заявка: {request_id}\n"
        f"Имя: {user_data['name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Адрес: {user_data['address']}\n"
        f"Услуга: {user_data['service']}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_admin)
    
    await update.message.reply_text(
        f"Спасибо за заявку! Ваш номер заявки: **{request_id}**. Мы свяжемся с вами в ближайшее время.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Заявка отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

def main():
    application = Application.builder().token
