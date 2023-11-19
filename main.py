import os
import time
from datetime import datetime

from dotenv import load_dotenv
from telebot import TeleBot

from log import logger
from parse_4score import get_trends
from parse_jleague import check_links, get_links_from_fixtures, get_page_as_response

load_dotenv()
current_year = datetime.now().year


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_CHAT_ID_DIMA = os.getenv("TELEGRAM_CHAT_ID_DIMA")
USER_IDS = {
    "Andre": TELEGRAM_CHAT_ID,
    "Dima": TELEGRAM_CHAT_ID_DIMA,
}
URL_BET = "https://www.jleague.co"
URL_BET_FIXTURE = f"https://www.jleague.co/fixtures/j1/{current_year}/latest/"
URL_TREND = "https://4score.ru/referee/18910"
RETRY_PERIOD = 600


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
    logger.debug("Начало отправки сообщения в Telegram")
    try:
        for user_id in USER_IDS.values():
            bot.send_message(user_id, message)
            logger.debug(f"Сообщение отправлено: '{message}' пользователю: '{user_id}'")
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
        f"\U000026BD Команды: {event[0]}"
        f"\n\U0001F525 Рефери: {event[1]}"
        f"Ссылка: {event[2]}"
    )
    logger.debug(f"Обнаружено событие: {match_info}")
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
    logger.debug("Переменные прошли проверку")
    bot = TeleBot(TELEGRAM_TOKEN)
    message = "Бот \U0001F916 начинает поиск игры. \U0001F50D"
    send_message(bot, message)
    while True:
        try:
            logger.debug(f"Проверяем страницу с играми {URL_BET_FIXTURE}")
            response = get_page_as_response(URL_BET_FIXTURE)
            parse_events = get_links_from_fixtures(response)
            logger.debug(f"Вот что нашли: {parse_events}")
            if parse_events:
                for link in parse_events:
                    logger.debug(f"Проверяем линк: {link}")
                    event_check = check_links(get_page_as_response(URL_BET + link))
                    if event_check:
                        message = collect_event_message(event_check)
                        send_message(bot, message)
            else:
                logger.debug("Встречи команд ещё не опубликованы.")
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            bot.send_message(USER_IDS["Andre"], message)
            logger.error(message)
        finally:
            logger.debug(f"Засыпаю на - {RETRY_PERIOD} сек")
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
