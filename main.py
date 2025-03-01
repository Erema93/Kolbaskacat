import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = '7149701343:AAHj3tT3KFlN5YXUQdTxSbNkDcGPyt3vjjY'  # Замените на ваш токен

# Инициализация базы данных SQLite
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user TEXT, 
                  category TEXT, 
                  amount REAL, 
                  date TEXT)''')
    conn.commit()
    conn.close()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для учета расходов семьи. Используй команды:\n"
        "/add <категория> <сумма> - добавить расход\n"
        "/list - показать все расходы\n"
        "/delete <id> - удалить запись по ID"
    )

# Добавление расхода: /add <категория> <сумма>
async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Используй: /add <категория> <сумма>")
        return
    
    try:
        category, amount = args[0], float(args[1])
        user = update.message.from_user.username or update.message.from_user.first_name
        date = update.message.date.strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (user, category, amount, date) VALUES (?, ?, ?, ?)",
                  (user, category, amount, date))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"Добавлен расход: {category} - {amount} руб. от {user}")
    except ValueError:
        await update.message.reply_text("Сумма должна быть числом!")

# Просмотр всех расходов: /list
async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT id, user, category, amount, date FROM expenses")
    rows = c.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Расходов пока нет.")
        return

    response = "Список расходов:\n"
    for row in rows:
        response += f"ID: {row[0]} | {row[1]} | {row[2]} | {row[3]} руб. | {row[4]}\n"
    await update.message.reply_text(response)

# Удаление расхода: /delete <id>
async def delete_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Используй: /delete <id>")
        return

    try:
        expense_id = int(args[0])
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if c.rowcount > 0:
            await update.message.reply_text(f"Расход с ID {expense_id} удален.")
        else:
            await update.message.reply_text(f"Расход с ID {expense_id} не найден.")
        conn.commit()
        conn.close()
    except ValueError:
        await update.message.reply_text("ID должен быть числом!")

# Обработка неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда. Используй /start для помощи.")

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Произошла ошибка:", exc_info=context.error)
    if update:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже или свяжитесь с администратором.")

def main():
    # Инициализация базы данных
    init_db()

    # Создание приложения Telegram
    application = Application.builder().token(TOKEN).build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_expense))
    application.add_handler(CommandHandler("list", list_expenses))
    application.add_handler(CommandHandler("delete", delete_expense))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Добавление обработчика ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()

