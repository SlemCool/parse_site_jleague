import os

from config import app_logger
from db.data import create_data_file, read_file, write_file
from dotenv import load_dotenv
from telebot import TeleBot, types

logger = app_logger.get_logger(__name__)
load_dotenv()
DATA_FILE_USERS = "data/users.txt"
create_data_file(DATA_FILE_USERS)
DATA_FILE_SUB_REQUEST = "data/sub_reqst.txt"
create_data_file(DATA_FILE_SUB_REQUEST)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_ID_ADMIN = os.getenv("TELEGRAM_CHAT_ID")

bot = TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message: types.Message) -> None:
    """/start command handler

    Args:
        message (types.Message): user's message object
    """
    user_id = message.chat.id
    user_full_name = message.from_user.full_name
    logger.info("Пользователь: %s - %s нажал СТАРТ!", user_id, user_full_name)
    bot.send_message(user_id, f"Привет {user_full_name} ✌️")


@bot.message_handler(commands=["help"])
def help_message(message: types.Message) -> None:
    """/help command handler

    Args:
        message (types.Message): user's message object
    """
    user_id = message.chat.id
    message = (
        "Этот бот ищет 🔍 необходимого судью в матчах Jleague 🇯🇵\n\n"
        "Доступные команды:\n/add_me - Подписаться на рассылку\n"
        "/remove_me - Отписаться от рассылки"
    )
    bot.send_message(user_id, message)


@bot.message_handler(commands=["add_me"])
def subscribe(message: types.Message) -> None:
    """Add user to the data file. For sending messages

    Args:
        message (types.Message): user's message object
    """
    user_id = str(message.chat.id)
    user_full_name = message.from_user.full_name
    message = "📣 Вы отправили заявку на рассылку, ожидайте..."
    subscribers = read_file(DATA_FILE_USERS)
    subscription_request = read_file(DATA_FILE_SUB_REQUEST)
    if user_id in subscribers:
        message = "Вы уже есть в списках 📜 на рассылку."
    elif user_id in subscription_request:
        message = "Ваша заявка на рассмотрении у администратора."
    else:
        write_file(user_id, DATA_FILE_SUB_REQUEST)
        bot.send_message(
            TELEGRAM_ID_ADMIN, f"Пользователь: {user_id}-{user_full_name} подал заявку"
        )
        logger.info(
            "Пользователь: %s-%s "
            "подал заявку на добавление в рассылку"
            , user_id, user_full_name
        )
    bot.send_message(user_id, message)


@bot.message_handler(commands=["2988329"])
def approved_user(message: types.Message) -> None:
    """Approve the user's application"""
    logger.info("Начинаем подписывать пользователей")
    subscribers = read_file(DATA_FILE_USERS)
    subscription_request = read_file(DATA_FILE_SUB_REQUEST)
    count_user = 0
    if subscription_request:
        for user_id in subscription_request:
            logger.info("Добавляем пользователя: %s в рассылку", user_id)
            if user_id not in subscribers:
                count_user += 1
                write_file(user_id, DATA_FILE_USERS)
                bot.send_message(user_id, "Заявка на добавление одобрена! 🪇")
    logger.info("Очищаем файл с заявками")
    subscription_request.clear()
    write_file(subscription_request, DATA_FILE_SUB_REQUEST, method="w")
    bot.send_message(
        TELEGRAM_ID_ADMIN, f"Успешно! Добавлено: {count_user} пользователь(ля, лей)"
    )


@bot.message_handler(commands=["remove_me"])
def unsubscribe(message: types.Message) -> None:
    """Remove user from the data file. For not sending messages

    Args:
        message (types.Message): user's message object
    """
    user_id = str(message.chat.id)
    user_full_name = message.from_user.full_name
    message = "Вы отказались от рассылки. 🥹"
    subscribers = read_file(DATA_FILE_USERS)
    if user_id in subscribers:
        logger.info("Пользователь: %s-%s удалился из рассылки", user_id, user_full_name)
        subscribers.remove(user_id)
        write_file(subscribers, DATA_FILE_USERS, method="w")
    else:
        message = "Вы ещё не подписались на рассылку. 🤷‍♂️"
    bot.send_message(user_id, message)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


def send_to_user(user_id, message: str) -> None:
    """Sending a message to the user

    Args:
        user_id (str): user id
        message (str): text message
    """
    logger.info("Начало отправки сообщения для пользователя '%s'", user_id)
    try:
        bot.send_message(user_id, message)
        logger.info("Сообщение отправлено пользователю: '%s'", user_id)
    except Exception as error:
        logger.error(
            "Пользователю: '%s' не получилось отправить сообщение: %s", user_id, error
        )


def send_to_all_users(message: str) -> None:
    """Sending a message to all users who subscribe

    Args:
        message (str): text message
    """
    logger.info("Начало массовой рассылки сообщения для пользователей")
    users = read_file(DATA_FILE_USERS)
    for user_id in users:
        try:
            bot.send_message(user_id, message, disable_web_page_preview=True)
            logger.info("Сообщение отправлено пользователю: '%s'", user_id)
        except Exception as error:
            logger.error(
                "Пользователю: '%s' не получилось отправить сообщение: %s", user_id, error
            )


def start_bot():
    bot.infinity_polling()
