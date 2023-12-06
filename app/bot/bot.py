import os

import telebot
from config import app_logger
from dotenv import load_dotenv

logger = app_logger.get_logger(__name__)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message):
    logger.info("КТО ТО ПРИСЛАЛ СТАРТ!!!!")
    bot.send_message(message.chat.id, "Привет ✌️ ")


# def start_sync():
#     bot.infinity_polling()

bot.infinity_polling()
