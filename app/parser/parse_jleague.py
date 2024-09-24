import random
import re
import time
from typing import List, Optional

from config import app_logger
from db.data import create_data_file, read_file, write_file
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumbase import SB

logger = app_logger.get_logger(__name__)
DATA_FILE_URL = "data/event_data.txt"
create_data_file(DATA_FILE_URL)

LOCATOR = {
    "match_events": (By.CSS_SELECTOR, "[class='match']"),
    "match_info": (By.CSS_SELECTOR, "[class='dataTable liveTopTable']"),
    "match_url": (By.TAG_NAME, "a"),
    "match_referee": (By.TAG_NAME, "td"),
}
ENG_URL = "https://www.jleague.co/match/j1/"
REF_JP_NAME = "福島 孝一郎"
REF_ENG_NAME = "Koichiro FUKUSHIMA"
REGEX_REF = r"\w+\s\w+"


def random_interval() -> None:
    """Sleep random interval"""
    time.sleep(random.randint(2, 6))


def parse_and_check_referee(url: str) -> Optional[List[str]]:
    """Get all links and check match

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
            logger.info("Проверяем сайт: %s", url)
            driver.get(url)
            games = driver.find_elements(*LOCATOR["match_events"])
            logger.info("Найдено: %s матчей", len(games))
            if not games:
                logger.info("На странице не найдено игр")
                return None

            games_urls = []
            checked_games_url = read_file(DATA_FILE_URL)
            for game in games:
                game_url = check_url(game, checked_games_url)
                if game_url:
                    games_urls.append(game_url)

            if not games_urls:
                logger.info("Нет ссылок для проверки")
                return None

            for game_url_jp in games_urls:
                game_info = check_game(driver, game_url_jp)
                if game_info:
                    return game_info
        return None

    except Exception as error:
        logger.error("Ошибка: %s в получении информации о событии: %s", error, url)


def check_url(game: WebElement, checked_games_url: list) -> Optional[str]:
    """
    Checks if the game URL is valid and if the event is in the 'live' status.

    Args:
        game (WebElement): The game element to check.
        checked_games_url (list): Checked games url.

    Returns:
        str or None: The game URL if the event is in the 'live' status,
            None if the event has already been processed.
    """
    game_url = game.find_element(*LOCATOR["match_url"]).get_attribute("href")
    logger.info("Проверяем ссылку на валидность: %s", game_url)
    if game_url in checked_games_url:
        logger.info("Событие отработано.")
        return None
    if "preview" not in game_url.split("/"):
        logger.info("Можно проверять событие в статусе 'live'")
        return game_url
    logger.info("Пропускаем событие ещё в статусе 'preview'")


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
        logger.info("Проверяем матч: %s", game_url_jp)
        data_match_info = []
        driver.get(game_url_jp)
        random_interval()
        if driver.is_element_present(*LOCATOR["match_info"]):
            info_block = driver.find_element(*LOCATOR["match_info"])
            col_ref = info_block.find_elements(*LOCATOR["match_referee"])[3]
            referee = col_ref.text.replace("\u3000", " ")
            logger.info("Судья в матче: %s", referee)
            if REF_JP_NAME == referee:
                write_file(game_url_jp, DATA_FILE_URL)
                data_match_info.append(REF_ENG_NAME)
                data_match_info.append(game_url_jp)
                split_url_jp = game_url_jp.split("/")
                data_match_info.append(ENG_URL + split_url_jp[5] + split_url_jp[6])
                return data_match_info
            if re.match(REGEX_REF, referee):
                write_file(game_url_jp, DATA_FILE_URL)
        return None
    except Exception as error:
        logger.error("Ошибка: %s в получении информации о событии: %s", error, game_url_jp)
