import os
import time

from dotenv import load_dotenv
from telebot import TeleBot

from log import logger
from parse_4score import get_trends
from parse_jleague import check_links, get_links, get_page_as_response

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_CHAT_ID_DIMA = os.getenv("TELEGRAM_CHAT_ID_DIMA")
USER_IDS = {
    "Andre": TELEGRAM_CHAT_ID,
    # "Dima": TELEGRAM_CHAT_ID_DIMA,
}
URL_BET = "https://www.jleague.co"
URL_TREND = "https://4score.ru/referee/18910"
RETRY_PERIOD = 600


def check_tokens() -> bool:
    """Checks the presence of all tokens

    Returns:
        bool
    """
    return all((TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_DIMA))


def send_message(bot: TeleBot, message: str, chat_id: str) -> None:
    """Sending a message to the user

    Args:
        bot (TeleBot): bot instance
        message (str): text message
        chat_id (str): user id
    """
    logger.debug("Начало отправки сообщения в Telegram")
    try:
        bot.send_message(chat_id, message)
        logger.debug(f"Сообщение отправлено: {message}")
    except Exception as error:
        logger.error(f"Упс сообщение не получилось отправить: {error}")


def main():
    """The main logic of the work of the bot"""
    logger.info("Бот приступает к патрулированию")
    if not check_tokens():
        logger.critical("Отсутствует хотя бы одна переменная окружения")
        raise ValueError("Отсутствует хотя бы одна переменная окружения!")
    logger.debug("Переменные прошли проверку")
    bot = TeleBot(TELEGRAM_TOKEN)
    print(type(bot))
    message = "Бот \U0001F916 начинает поиск игры. \U0001F50D"
    for user in USER_IDS:
        send_message(bot, message, USER_IDS[user])
    logger.debug("Пробное сообщение отправлено")
    while True:
        try:
            logger.debug("Проверяем главный сайт")
            response = get_page_as_response(URL_BET)
            parse_events = get_links(response)
            logger.debug("Проверка прошла")
            if parse_events:
                logger.debug(f"Обнаружены линки на события: {parse_events}")
                for link in parse_events:
                    logger.debug(f"Проверяем линк: {link}")
                    event_check = check_links(get_page_as_response(URL_BET + link))
                    if event_check:
                        match_info = f"\U000026BD Команды: {event_check[0]}\n\U0001F525 Рефери: {event_check[1]}"
                        logger.debug(f"Обнаружено нужное событие: {match_info}")
                        trend_info = get_trends(get_page_as_response(URL_TREND))
                        message = f"\U000026A0 Внимание \U000026A0\n\n{match_info}\n\n\U0001F4C8 Тренды для рефери:\n{trend_info}"
                        for user in USER_IDS:
                            send_message(bot, message, USER_IDS[user])
            else:
                logger.debug("Встречи команд ещё не опубликованы.")
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            send_message(bot, message)
            logger.error(message)
        finally:
            logger.debug(f"Засыпаю на - {RETRY_PERIOD} сек")
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
