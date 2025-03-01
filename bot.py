python

import logging
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Этапы диалога
NAME, PHONE, ADDRESS, SERVICE = range(4)

# Список услуг
SERVICES = [
    "Поверка счетчиков тепла",
    "Замена счетчиков воды",
    "Поверка счетчиков воды"
]

# Токен бота (замени на свой, полученный от @BotFather)
TOKEN = "7831214357:AAHNlb2lXwoLks9eN7JnQ1SRDEd6zOgXe-U"

# ID чата, куда будут отправляться заявки (замени на свой Telegram ID)
ADMIN_CHAT_ID = "572255263"  # Например, "123456789"

# Счетчик заявок (для простоты храним в памяти, для продакшна лучше использовать базу данных)
request_counter = 0

# Стартовая команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Здравствуйте! Я бот для приема заявок. Давайте начнем.\n"
        "Как вас зовут?"
    )
    return NAME

# Получение имени
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Укажите ваш номер телефона (например, +380970000001):")
    return PHONE

# Получение номера телефона
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Укажите адрес, где нужно выполнить работы:")
    return ADDRESS

# Получение адреса
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['address'] = update.message.text
    reply_keyboard = [[service] for service in SERVICES]
    await update.message.reply_text(
        "Выберите вид работ:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SERVICE

# Получение услуги и завершение заявки
async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global request_counter
    context.user_data['service'] = update.message.text
    user_data = context.user_data

    # Генерируем номер заявки
    request_counter += 1
    request_id = f"Заявка-{request_counter}-{random.randint(100, 999)}"  # Пример: Заявка-1-456

    # Формируем сообщение для администратора
    message_to_admin = (
        f"Новая заявка: {request_id}\n"
        f"Имя: {user_data['name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Адрес: {user_data['address']}\n"
        f"Услуга: {user_data['service']}"
    )

    # Отправляем заявку администратору
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_admin)
    
    # Подтверждение клиенту с номером заявки
    await update.message.reply_text(
        f"Спасибо за заявку! Ваш номер заявки: **{request_id}**. Мы свяжемся с вами в ближайшее время.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Заявка отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Обработка ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Настраиваем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_error_handler(error)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
