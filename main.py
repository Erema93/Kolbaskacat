from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)
import os
import uuid
from dotenv import load_dotenv

app = FastAPI()

# Загрузка переменных окружения (исправлено)
load_dotenv()
TELEGRAM_TOKEN = os.getenv("8012532063:AAGNNZ7XkdLQU_-sMR2SG9tLb1ZICVLOSWo")  # Теперь ожидает название переменной
YOUR_TELEGRAM_ID = os.getenv("572255263")  # Аналогично для ID

# Структура для зберігання заявок
tickets = {}

# Инициализация бота (теперь один раз)
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Вітаю! Для подачі заявки введіть: \n"
        "1. Ім'я\n"
        "2. Адресу\n"
        "3. Номер телефону\n"
        "Почнемо з імені."
    )
    context.user_data["step"] = 1  # Початковий етап

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    current_step = context.user_data.get("step", 1)
    text = update.message.text.strip()

    if current_step == 1:  # Введення імені
        context.user_data["name"] = text
        context.user_data["step"] = 2
        await update.message.reply_text("Введіть адресу:")
    elif current_step == 2:  # Введення адреси
        context.user_data["address"] = text
        context.user_data["step"] = 3
        await update.message.reply_text("Введіть номер телефону:")
    elif current_step == 3:  # Введення номера телефону
        context.user_data["phone"] = text

        # Генерація номера заявки
        ticket_id = str(uuid.uuid4())[:8]
        tickets[ticket_id] = {
            "name": context.user_data["name"],
            "address": context.user_data["address"],
            "phone": context.user_data["phone"],
            "user_id": user.id
        }

        # Відправка клієнту номера заявки
        await update.message.reply_text(
            f"Дякуємо! Ваша заявка №{ticket_id} прийнята. Очікуйте зворотнього зв'язку."
        )

        # Відправка заявки вам (на ваш Telegram)
        await context.bot.send_message(
            chat_id=YOUR_TELEGRAM_ID,
            text=f"Нова заявка №{python{ticket_id}}:\n"
                 f"Ім'я: {context.user_data['name']}\n"
                 f"Адреса: {context.user_data['address']}\n"
                 f"Телефон: {context.user_data['phone']}"
        )
        context.user_data.clear()  # Очистка даних

async def error_handler(update: object, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Виникла помилка. Спробуйте ще раз."
    )

# Добавляем обработчики один раз при старте
async def initialize_telegram():
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    telegram_app.add_error_handler(error_handler)
    await telegram_app.initialize()

# Запускаем инициализацию при старте FastAPI
@app.on_event("startup")
async def startup():
    await initialize_telegram()

# Исправленный обработчик вебхука
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)  # Передаем экземпляр бота
    await telegram_app.process_update(update)
    return {"status": "ok"}
