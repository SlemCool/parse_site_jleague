import os

from config import app_logger
from db.data import create_data_file, read_file, write_file
from dotenv import load_dotenv
from telebot import TeleBot, types

logger = app_logger.get_logger(__name__)
load_dotenv()
DATA_FILE_USERS = "data/users.txt"
create_data_file(DATA_FILE_USERS)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message: types.Message) -> None:
    """/start command handler

    Args:
        message (types.Message): user's message object
    """
    user_id = message.chat.id
    user_full_name = message.from_user.full_name
    logger.info(f"Пользователь: {user_id} - {user_full_name} нажал СТАРТ!")
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
    message = "📣 Вы добавлены в рассылку. 🪇"
    subscribers = read_file(DATA_FILE_USERS)
    if user_id in subscribers:
        message = "Вы уже есть в списках 📜 на рассылку."
    else:
        write_file(user_id, DATA_FILE_USERS)
        logger.info(f"Пользователь: {user_id}-{user_full_name} добавился в рассылку")
    bot.send_message(user_id, message)


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
        logger.info(f"Пользователь: {user_id}-{user_full_name} удалился из рассылки")
        subscribers.remove(user_id)
        write_file(subscribers, DATA_FILE_USERS, method="w")
    else:
        message = "Вы ещё не подписались на рассылку. 🤷‍♂️"
    bot.send_message(user_id, message)


def send_to_user(user_id, message: str) -> None:
    """Sending a message to the user

    Args:
        user_id (str): user id
        message (str): text message
    """
    logger.info(f"Начало отправки сообщения для пользователя '{user_id}'")
    try:
        bot.send_message(user_id, message)
        logger.info(f"Сообщение отправлено пользователю: '{user_id}'")
    except Exception as error:
        logger.error(
            f"Пользователю: '{user_id}' не получилось отправить сообщение: {error}"
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
            logger.info(f"Сообщение отправлено пользователю: '{user_id}'")
        except Exception as error:
            logger.error(
                f"Пользователю: '{user_id}' не получилось отправить сообщение: {error}"
            )


def start_bot():
    bot.infinity_polling()


# start_bot()
