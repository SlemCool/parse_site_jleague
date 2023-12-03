import os
import random
import time

import app_logger
from dotenv import load_dotenv
from parse_4score import get_trends
from parse_jleague import parse_and_check_referee
from telebot import TeleBot

logger = app_logger.get_logger(__name__)
load_dotenv()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_CHAT_ID_DIMA = os.getenv("TELEGRAM_CHAT_ID_DIMA")
USER_IDS = {
    "Andre": TELEGRAM_CHAT_ID,
    "Dima": TELEGRAM_CHAT_ID_DIMA,
}
URL_JLEAGUE_LATEST = "https://www.jleague.jp/match/search/j1/latest/"
# URL_JLEAGUE_LATEST = "https://www.jleague.jp/match/section/j1/33/"  # Для отладки
URL_TREND = "https://4score.ru/referee/18910"


def rnd_sleep_interval() -> int:
    return random.randint(300, 600)


def check_tokens() -> bool:
    """Checks the presence of all tokens

    Returns:
        bool
    """
    return all((TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_DIMA))


def send_message(bot: TeleBot, message: str) -> None:
    """Sending a message to the user

    Args:
        bot (TeleBot): bot instance
        message (str): text message
        chat_id (str): user id
    """
    logger.info("Начало отправки сообщения в Telegram")
    try:
        for user_id in USER_IDS.values():
            bot.send_message(user_id, message, disable_web_page_preview=True)
            logger.info(f"Сообщение отправлено пользователю: '{user_id}'")
    except Exception as error:
        logger.error(
            f"Пользователю: '{user_id}' не получилось отправить сообщение: {error}"
        )


def collect_event_message(event: list) -> str:
    """Collects the final event message

    Args:
        event (list): event data

    Returns:
        str: message string
    """
    match_info = (
        f"\U0001F525 Рефери: {event[0]}"
        f"\nСсылка 🇯🇵: {event[1]}"
        f"\nСсылка 🇺🇸: {event[2]}"
    )
    message = f"\U000026A0 Внимание \U000026A0\n\n{match_info}\n\n"
    trend_info = get_trends(URL_TREND)
    if trend_info:
        message += f"\U0001F4C8 Тренды для рефери:\n{trend_info}"
    return message


def main():
    """The main logic of the work of the bot"""
    logger.info("Бот приступает к патрулированию")
    if not check_tokens():
        logger.critical("Отсутствует хотя бы одна переменная окружения")
        raise ValueError("Отсутствует хотя бы одна переменная окружения!")
    logger.info("Переменные прошли проверку")
    bot = TeleBot(TELEGRAM_TOKEN)
    message = "Бот \U0001F916 начинает поиск игры. \U0001F50D"
    bot.send_message(USER_IDS["Andre"], message)
    while True:
        try:
            event_data = parse_and_check_referee(URL_JLEAGUE_LATEST)
            if event_data:
                logger.warning("Обнаружен нужный матч!!!")
                message = collect_event_message(event_data)
                send_message(bot, message)
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            bot.send_message(USER_IDS["Andre"], message)
            logger.error(message)
        finally:
            retry_interval = rnd_sleep_interval()
            logger.info(f"Засыпаю на - {retry_interval} сек")
            time.sleep(retry_interval)


if __name__ == "__main__":
    main()

# python -m nuitka \
# --follow-imports \
# --include-package-data=selenium  \
# --standalone \
# --include-data-files=.env=.env  \
# --remove-output \
# --windows-icon-from-ico=assets\logo.png  \
# -o JLparser \
# app\main.py
