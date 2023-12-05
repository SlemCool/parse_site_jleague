import asyncio
import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


bot = AsyncTeleBot(TELEGRAM_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    await bot.reply_to(
        message,
        """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""",
    )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


async def start_async():
    await bot.polling()
# asyncio.run(bot.polling())
