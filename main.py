import telebot
import schedule
import time

TOKEN = "@Kolbaskacat_bot"
CHAT_ID = "572255263"

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
