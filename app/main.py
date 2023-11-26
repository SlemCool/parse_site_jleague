import os
import random
import time

import app_logger
from dotenv import load_dotenv
from parse_4score import get_trends
from parse_jleague import get_page_as_response, parse_and_check_referee
from telebot import TeleBot

logger = app_logger.get_logger(__name__)
load_dotenv()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_CHAT_ID_DIMA = os.getenv("TELEGRAM_CHAT_ID_DIMA")
USER_IDS = {
    "Andre": TELEGRAM_CHAT_ID,
    # "Dima": TELEGRAM_CHAT_ID_DIMA,
}
URL_JLEAGUE_LATEST = "https://www.jleague.jp/match/search/j1/latest/"
URL_TREND = "https://4score.ru/referee/18910"


def rnd_sleep_interval() -> int:
    return random.randint(300, 700)


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
            bot.send_message(user_id, message)
            logger.info(f"Сообщение отправлено пользователю: '{user_id}'\n'{message}'")
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
        f"\n\U0001F525 Рефери: {event[0]}"
        f"\nСсылка 🇯🇵: {event[1]}"
        f"\nСсылка 🇺🇸: {event[2]}"
    )
    logger.warning("Обнаружен нужный матч!!!")
    trend_info = get_trends(get_page_as_response(URL_TREND))
    return (
        "\U000026A0 Внимание \U000026A0"
        f"\n\n{match_info}\n\n"
        "\U0001F4C8 Тренды для рефери:"
        f"\n{trend_info}"
    )


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
            event_check = parse_and_check_referee(URL_JLEAGUE_LATEST)
            if event_check:
                message = collect_event_message(event_check)
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

# python -m nuitka --follow-imports --standalone --windows-icon-from-ico=assets\logo.png --remove-output app\main.py 
