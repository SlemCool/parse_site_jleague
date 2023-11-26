import random
import time
from typing import List

import app_logger
import app_logger
from requests_html import HTMLResponse, HTMLSession
from selenium.webdriver.common.by import By
from seleniumbase import SB

from data import create_data_file, read_file, write_file

logger = app_logger.get_logger(__name__)
create_data_file()
event_status = read_file()


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
    time.sleep(random.randint(1, 7))


def is_completed_event(url: str) -> bool:
    if event_status:
        return url in event_status
    return False


def parse_and_check_referee(url: str) -> List[str]:
    try:
        with SB(
            uc=True,
            headless=True,
            page_load_strategy="eager",
            block_images=True,
        ) as driver:
            logger.info(
                f"Версия хрома: {driver.get_chrome_version()} "
                f"версия драйвера: {driver.get_chromedriver_version()}"
            )
            data_match_info = []
            logger.warning(f"Проверяем сайт: {url}")
            driver.get(url)
            games = driver.find_elements(*LOCATOR["match_events"])
            logger.warning(f"Найдено: {len(games)} матчей")
            if not games:
                return None
            for game in games:
                game_url_jp = game.find_element(*LOCATOR["match_url"]).get_attribute(
                    "href"
                )
                logger.warning(f"Проверяем матч: {game_url_jp}")
                if is_completed_event(game_url_jp):
                    logger.warning(f"Уже отработанное событие: {game_url_jp}")
                    continue
                random_interval()
                game.click()
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
                random_interval()
                driver.go_back()
            return None
    except Exception as error:
        logger.error(f"Ошибка: {error} в получении информации о событии: {url}")


def get_page_as_response(url: str) -> HTMLResponse:
    """Try to get a response from a given URL

    Args:
        url (str): site URL

    Returns:
        HTMLResponse: Response object with (JS). Returns rendered response
    """
    try:
        # proxy = {'http' : 'http://50.168.210.226:80', 'https': 'https://50.168.210.226:80'}
        # session = HTMLSession(browser_args=["--proxy-server=50.168.210.226:80"])
        session = HTMLSession()
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Referer": "https://www.jleague.co/fixtures/j1/2023/latest/",
        }
        response = session.get(url, headers=headers, timeout=5)
        response.html.render(sleep=5, scrolldown=2)
        # response.close()
        session.close()
        # time.sleep(2)
        return response
    except Exception as error:
        logger.error(f"Ошибка: {error} в получении или рендеринге для: {url}")


# OLD CODE

# def get_links_from_main(response: HTMLResponse) -> List[str]:
#     """Try to get links on main page

#     Args:
#         response (HTMLResponse): Response object

#     Returns:
#         List[str]: List with links
#     """
#     try:
#         first_block = response.html.find("div.games-list", first=True)
#         if first_block:
#             events_links = list(first_block.links)
#             if events_links:
#                 return events_links
#         return None
#     except Exception as error:
#         logger.error(f"Ошибка в получении ссылок на события: {error}")


# def get_links_from_fixtures(response: HTMLResponse) -> List[str]:
#     """Try to get links on main page

#     Args:
#         response (HTMLResponse): Response object

#     Returns:
#         List[str]: List with links
#     """
#     try:
#         events = response.html.find("a.match-link")
#         if events:
#             events_links = ["".join(event.links) for event in events]
#             if events_links:
#                 logger.warning(f"Ссылки на игры: {events_links}")
#                 return events_links
#         return None
#     except Exception as error:
#         logger.error(f"Ошибка в получении ссылок на события: {error}")


# def check_links(
#     response: HTMLResponse, referee: str = "Koichiro FUKUSHIMA"
# ) -> List[str]:
#     """Finding the right referee

#     Args:
#         response (HTMLResponse): Response object
#         referee: str: Name of the referee

#     Returns:
#         List[str]: List with match information
#     """
#     url = response.url
#     if is_completed_event(url):
#         return None
#     try:
#         match_info = []
#         rs_match_info = response.html.find("div.match-extra-info-item")
#         label, value = rs_match_info[3].text.split("\n")
#         logger.warning(f"Проверяем линк: {url} Судья: {label} - {value}")
#         if value.lower() == referee.lower():
#             write_file(url)
#             event_status.append(url)
#             # Get teams name
#             teams: list = response.html.find("div.match-details-header__info > h1")
#             match_info.append(
#                 teams[0].text.strip().replace(",", "").replace("VS", "\U0001F19A")
#             )
#             # Referee name
#             match_info.append(value)
#             # Match url
#             match_info.append(url)
#             return match_info
#         return None
#     except Exception as error:
#         logger.error(f"Ошибка: {error} в получении информации о событии: {url}")
