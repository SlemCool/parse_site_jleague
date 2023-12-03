import os
import random
import time
from typing import List, Optional

import app_logger
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumbase import SB
from telebot import TeleBot

from data import create_data_file, read_file, write_file

logger = app_logger.get_logger(__name__)
create_data_file()
event_status = read_file()

# TEMP
# load_dotenv()
# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# TELEGRAM_CHAT_ID_DIMA = os.getenv("TELEGRAM_CHAT_ID_DIMA")
# USER_IDS = {
#     "Andre": TELEGRAM_CHAT_ID,
#     "Dima": TELEGRAM_CHAT_ID_DIMA,
# }
# END TEMP

LOCATOR = {
    "match_events": (By.CSS_SELECTOR, "[class='match']"),
    "match_info": (By.CSS_SELECTOR, "[class='dataTable liveTopTable']"),
    "match_url": (By.TAG_NAME, "a"),
    "match_referee": (By.TAG_NAME, "td"),
}
ENG_URL = "https://www.jleague.co/match/j1/"
REF_JP = "福島 孝一郎"
REF_ENG = "Koichiro FUKUSHIMA"


def random_interval() -> None:
    """Sleep random interval"""
    time.sleep(random.randint(2, 7))


def parse_and_check_referee(url: str) -> Optional[List[str]]:
    """Get links and check match

    Args:
        url (str): Japan site reference

    Returns:
        List[str]: List with data
    """
    try:
        with SB(
            uc=True,
            headless=True,
            page_load_strategy="eager",
            block_images=True,
        ) as driver:
            logger.warning(f"Проверяем сайт: {url}")
            driver.get(url)
            games = driver.find_elements(*LOCATOR["match_events"])
            logger.warning(f"Найдено: {len(games)} матчей")
            if not games:
                logger.warning("На главной странице не найдено игр")
                return None

            game_urls = []
            for game in games:
                game_url = check_url(game)
                if game_url:
                    game_urls.append(game_url)

            if not game_urls:
                logger.warning("Нет ссылок для проверки")
                return None

            for game_url_jp in game_urls:
                game_info = check_game(driver, game_url_jp)
                if game_info:
                    return game_info
        return None

    except Exception as error:
        logger.error(f"Ошибка: {error} в получении информации о событии: {url}")


def check_url(game: WebElement) -> Optional[str]:
    """
    Checks if the game URL is valid and if the event is in the 'live' status.

    Args:
        game (WebElement): The game element to check.

    Returns:
        str or None: The game URL if the event is in the 'live' status,
            None if the event has already been processed.
    """
    game_url = game.find_element(*LOCATOR["match_url"]).get_attribute("href")
    logger.warning(f"Проверяем ссылку на валидность: {game_url}")
    if game_url in event_status:
        logger.warning("Событие отработано.")
        return None
    if "preview" not in game_url.split("/"):
        logger.warning("!! Нужное событие в статусе 'live' !!")
        
        # TEMP
        # bot = TeleBot(TELEGRAM_TOKEN)
        # message = "\U000026A0 Внимание \U000026A0"
        # bot.send_message(USER_IDS["Andre"], message)
        # bot.send_message(USER_IDS["Dima"], message)
        # random_interval()
        # message = f"\U0001F50D Поменялся статус игры на 'live'\nНужно проверить страницу на наличии судьи\n{game_url}"
        # bot.send_message(USER_IDS["Andre"], message)
        # bot.send_message(USER_IDS["Dima"], message)
        # random_interval()
        # message = "\U000026A0 Внимание \U000026A0"
        # bot.send_message(USER_IDS["Andre"], message)
        # bot.send_message(USER_IDS["Dima"], message)
        # END TEMP
        
        return game_url
    logger.warning("Событие в статусе 'preview'")


def check_game(driver: WebDriver, game_url_jp: str) -> Optional[List[str]]:
    """
    This function checks if a given game URL
    is a match and if the referee is the expected referee.
    It then returns the list of event data.

    Args:
    driver (WebDriver): The Selenium WebDriver.
    game_url_jp (str): The URL of the game to check.

    Returns:
    list or None: A list of event data if the game is a match and the referee is correct

    """
    try:
        logger.warning(f"Проверяем матч: {game_url_jp}")
        data_match_info = []
        driver.get(game_url_jp)
        random_interval()
        if driver.is_element_present(*LOCATOR["match_info"]):
            info_block = driver.find_element(*LOCATOR["match_info"])
            col_ref = info_block.find_elements(*LOCATOR["match_referee"])[3]
            referee = col_ref.text.replace("\u3000", " ")
            logger.warning(f"Судья в матче: {referee}")
            if REF_JP == referee:
                write_file(game_url_jp)
                event_status.append(game_url_jp)
                data_match_info.append(REF_ENG)
                data_match_info.append(game_url_jp)
                raw_url_jp = game_url_jp.split("/")
                data_match_info.append(ENG_URL + raw_url_jp[5] + raw_url_jp[6])
                return data_match_info
        return None
    except Exception as error:
        logger.error(f"Ошибка: {error} в получении информации о событии: {game_url_jp}")
