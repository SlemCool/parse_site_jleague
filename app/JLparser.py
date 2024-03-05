import os
import random
import time
from parser.parse_4score import get_trends
from parser.parse_jleague import parse_and_check_referee
from threading import Thread

from bot import main_bot
from config import app_logger
from dotenv import load_dotenv

logger = app_logger.get_logger(__name__)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_ID_ADMIN = os.getenv("TELEGRAM_CHAT_ID")
URL_JLEAGUE_LATEST = "https://www.jleague.jp/match/search/j1/latest/"
# URL_JLEAGUE_LATEST = "https://www.jleague.jp/match/section/j1/34/"  # Для отладки
URL_TREND = "https://4score.ru/referee/18910"


def rnd_sleep_interval() -> int:
    return random.randint(120, 360)


def check_tokens() -> bool:
    """Checks the presence of all tokens

    Returns:
        bool
    """
    return all((TELEGRAM_TOKEN, TELEGRAM_ID_ADMIN))


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
        message = "Отсутствует хотя бы одна переменная окружения"
        logger.critical(message)
        raise ValueError(message)
    logger.info("Переменные прошли проверку")
    message = "\U0001F916 'JLbot' начинает поиск игры. \U0001F50D"
    main_bot.send_to_user(TELEGRAM_ID_ADMIN, message)
    while True:
        try:
            event_data = parse_and_check_referee(URL_JLEAGUE_LATEST)
            if event_data:
                logger.warning(f"Обнаружен нужный матч: {event_data[1]}")
                message = collect_event_message(event_data)
                main_bot.send_to_all_users(message)
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            main_bot.send_to_user(TELEGRAM_ID_ADMIN, message)
            logger.error(message)
        finally:
            retry_interval = rnd_sleep_interval()
            logger.info(f"Засыпаю на - {retry_interval} сек")
            time.sleep(retry_interval)


if __name__ == "__main__":
    Thread(target=main).start()
    Thread(target=main_bot.start_bot).start()


# python -m nuitka --follow-imports --include-package-data=selenium  --standalone --include-data-files=.env=.env  --remove-output --windows-icon-from-ico=assets\logo.png  -o JLparser app\JLparser.py
