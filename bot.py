import logging
import os
import sys
import time

from dotenv import load_dotenv
from telebot import TeleBot

from giga import generate_horoscope
from parse_4score import get_trends
from parse_jleague import check_links, get_links, get_page_as_response

load_dotenv()


logging.basicConfig(
    handlers=[logging.FileHandler(filename="main.log", encoding="utf-8")],
    format="%(asctime)s  %(name)s, %(levelname)s, %(message)s",
    datefmt="%F %A %T",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)

GIGA_TOKEN = os.getenv("GIGA_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_CHAT_ID_DIMA = os.getenv("TELEGRAM_CHAT_ID_DIMA")
USER_IDS = {
    "Andre": TELEGRAM_CHAT_ID,
    # "Dima": TELEGRAM_CHAT_ID_DIMA,
}
URL_BET = "https://www.jleague.co/"
URL_TREND = "https://4score.ru/referee/18910/"
RETRY_PERIOD = 600


def check_tokens() -> bool:
    """Проверка предзаполненных переменных окружения."""
    return all((GIGA_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_DIMA))


def send_message(bot, message, chat_id):
    """Отправка сообщения пользователю бота."""
    logger.debug("Начало отправки сообщения в Telegram")
    try:
        bot.send_message(chat_id, message)
        logger.debug(f"Сообщение отправлено: {message}")
    except Exception as error:
        logger.error(f"Упс сообщение не получилось отправить: {error}")


def main():
    """Основная логика работы бота."""
    logger.info("Бот приступает к патрулированию")
    if not check_tokens():
        logger.critical("Отсутствует хотя бы одна переменная окружения")
        raise ValueError("Отсутствует хотя бы одна переменная окружения!")
    logger.debug("Переменные прошли проверку")
    bot = TeleBot(TELEGRAM_TOKEN)
    message = "Бот приступает к патрулированию.\n\n\t" + generate_horoscope(GIGA_TOKEN)
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
                logger.debug(f'Обнаружены линки на события: {parse_events}')
                for link in parse_events:
                    logger.debug(f'Проверяем линк: {link}')
                    event_check = check_links(get_page_as_response(URL_BET + link))
                    if event_check:
                        match_info = (
                            f"Команды: {event_check[0]}\nРефери: {event_check[1]}"
                        )
                        logger.debug(f'Обнаружено нужное событие: {match_info}')
                        trend_info = get_trends(get_page_as_response(URL_TREND))
                        message = f"Внимание!\n\n{match_info}\n\n{trend_info}"
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
