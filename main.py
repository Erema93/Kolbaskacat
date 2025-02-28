import telebot
import schedule
import time
const port = process.env.PORT || 4000

TOKEN = "7938046164:AAHKw2wmUyBuziXuy0lPlkYXQQgH4D3wmzA"
CHAT_ID = "7938046164"

bot = telebot.TeleBot(TOKEN)

def send_tales():
    tale1 = "🐱 История 1: Приключения котов-колбасок..."
    tale2 = "🐱 История 2: Сладкий мир котов-колбасок..."
    bot.send_message(CHAT_ID, tale1)
    bot.send_message(CHAT_ID, tale2)

schedule.every().day.at("22:00").do(send_tales)

while True:
    schedule.run_pending()
    time.sleep(60)
