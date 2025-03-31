import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

# --- НАСТРОЙКИ ---
# Получаем токен и ID чата из переменных окружения
TELEGRAM_BOT_TOKEN = os.environ.get('8012532063:AAGNNZ7XkdLQU_-sMR2SG9tLb1ZICVLOSWo')
YOUR_PERSONAL_CHAT_ID = os.environ.get('572255263')
# --- КОНЕЦ НАСТРОЕК ---

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем состояния для ConversationHandler
CATEGORY, PHONE, ADDRESS = range(3) # Добавили состояние ADDRESS

# Категории услуг
CATEGORIES = {
    "heat_meter_verify": "Повірка лічильника опалення",
    "battery_replace": "Заміна батарейки",
    "water_meter_replace": "Заміна лічильника води",
    "water_meter_verify": "Повірка лічильника води",
}

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отправляет приветственное сообщение и предлагает выбрать категорию."""
    keyboard = [
        [InlineKeyboardButton(text, callback_data=key)] for key, text in CATEGORIES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Убираем любую предыдущую клавиатуру на всякий случай
    await update.message.reply_text(
        'Вітаю! Я допоможу вам оформити заявку. Будь ласка, оберіть послугу:',
        reply_markup=reply_markup
    )
    # Очищаем user_data на случай перезапуска диалога
    context.user_data.clear()
    return CATEGORY # Переходим в состояние выбора категории

# Функция обработки нажатия кнопки с категорией
async def category_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор категории и запрашивает номер телефона."""
    query = update.callback_query
    await query.answer()

    category_key = query.data
    category_text = CATEGORIES.get(category_key, "Невідома категорія")
    context.user_data['category'] = category_text # Сохраняем выбранную категорию

    await query.edit_message_text(text=f"Ви обрали: {category_text}")

    # Запрашиваем номер телефона
    phone_button = KeyboardButton(text="📱 Надіслати номер телефону", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[phone_button]], one_time_keyboard=True, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text='Тепер, будь ласка, надайте ваш номер телефону для зв\'язку, натиснувши кнопку нижче:',
        reply_markup=reply_markup
    )
    return PHONE # Переходим в состояние ожидания телефона

# Функция обработки получения контакта (телефона)
async def phone_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает получение контакта и запрашивает адрес."""
    contact = update.message.contact
    phone_number = contact.phone_number
    context.user_data['phone'] = phone_number # Сохраняем номер телефона

    # Убираем клавиатуру запроса телефона и просим ввести адрес
    await update.message.reply_text(
        'Дякую! Тепер, будь ласка, введіть вашу адресу (місто, вулиця, будинок, квартира):',
        reply_markup=ReplyKeyboardRemove() # Убирает кнопку "Надіслати номер"
    )
    return ADDRESS # Переходим в состояние ожидания адреса

# Функция обработки получения адреса
async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает получение адреса и отправляет заявку владельцу."""
    address = update.message.text
    context.user_data['address'] = address # Сохраняем адрес

    user = update.message.from_user
    user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"

    # Получаем сохраненные данные
    category = context.user_data.get('category', 'Не вказано')
    phone_number = context.user_data.get('phone', 'Не вказано')
    address_text = context.user_data.get('address', 'Не вказано')

    # Формируем текст заявки для отправки владельцу
    application_text = (
        f"🔔 Нова заявка! 🔔\n\n"
        f"👤 Від: {user_info}\n"
        f"📞 Телефон: +{phone_number}\n"
        f"🏠 Адреса: {address_text}\n" # Добавили адрес
        f"🔧 Послуга: {category}"
    )

    # Отправляем заявку на ЛИЧНЫЙ Chat ID владельца
    try:
        if not YOUR_PERSONAL_CHAT_ID:
             logger.error("YOUR_PERSONAL_CHAT_ID не встановлено!")
             raise ValueError("Chat ID власника не налаштовано.")

        await context.bot.send_message(
            chat_id=YOUR_PERSONAL_CHAT_ID,
            text=application_text
        )
        logger.info(f"Заявка від {user_info} по послузі '{category}' (Адреса: {address_text}) відправлена.")
        # Сообщаем пользователю, что заявка принята
        await update.message.reply_text(
            '✅ Дякуємо! Ваша заявка прийнята. Ми зв\'яжемося з вами найближчим часом.',
            reply_markup=ReplyKeyboardRemove() # Убираем любую клавиатуру
        )
    except Exception as e:
        logger.error(f"Помилка відправки заявки: {e}")
        await update.message.reply_text(
            '❌ Виникла помилка при відправці заявки. Спробуйте пізніше або зверніться до адміністратора.',
            reply_markup=ReplyKeyboardRemove()
        )

    # Очищаем user_data
    context.user_data.clear()
    return ConversationHandler.END # Завершаем диалог

# Функция для отмены диалога
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет текущий диалог."""
    await update.message.reply_text(
        'Дію скасовано.',
        reply_markup=ReplyKeyboardRemove() # Убираем клавиатуру
    )
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Запуск бота."""
    # Проверка наличия токена и ID перед запуском
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("Не знайдено TELEGRAM_BOT_TOKEN! Встановіть змінну оточення.")
        return
    if not YOUR_PERSONAL_CHAT_ID:
        logger.critical("Не знайдено YOUR_PERSONAL_CHAT_ID! Встановіть змінну оточення.")
        # Можно не останавливать бота, а просто логировать ошибку,
        # но заявки не будут отправляться. Решил остановить для ясности.
        return
    try:
        # Пробуем преобразовать ID в число для ранней проверки
        int(YOUR_PERSONAL_CHAT_ID)
    except ValueError:
        logger.critical(f"YOUR_PERSONAL_CHAT_ID ('{YOUR_PERSONAL_CHAT_ID}') не є дійсним числовим ID чату!")
        return


    # Создаем Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Создаем ConversationHandler с новыми состояниями и переходами
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CATEGORY: [CallbackQueryHandler(category_choice)],
            PHONE: [MessageHandler(filters.CONTACT, phone_received)],
             # Добавляем обработчик для текстового сообщения в состоянии ADDRESS
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Запускаем бота (в
