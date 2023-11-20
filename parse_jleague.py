from typing import List

from requests_html import HTMLResponse, HTMLSession

import app_logger
from data import create_data_file, read_file, write_file

logger = app_logger.get_logger(__name__)
create_data_file()
event_status = read_file()


def get_page_as_response(url: str) -> HTMLResponse:
    """Try to get a response from a given URL

    Args:
        url (str): site URL

    Returns:
        HTMLResponse: Response object with (JS). Returns rendered response
    """
    try:
        session = HTMLSession()
        response = session.get(url)
        response.html.render(sleep=1, scrolldown=2)
        session.close()
        return response
    except Exception as error:
        logger.error(f"Ошибка: {error} в получении или рендеринге для: {url}")


def get_links_from_main(response: HTMLResponse) -> List[str]:
    """Try to get links on main page

    Args:
        response (HTMLResponse): Response object

    Returns:
        List[str]: List with links
    """
    try:
        first_block = response.html.find("div.games-list", first=True)
        if first_block:
            events_links = list(first_block.links)
            if events_links:
                return events_links
        return None
    except Exception as error:
        logger.error(f"Ошибка в получении ссылок на события: {error}")


def get_links_from_fixtures(response: HTMLResponse) -> List[str]:
    """Try to get links on main page

    Args:
        response (HTMLResponse): Response object

    Returns:
        List[str]: List with links
    """
    try:
        events = response.html.find("a.match-link")
        if events:
            events_links = ["".join(event.links) for event in events]
            if events_links:
                logger.warning(f"Ссылки на игры: {events_links}")
                return events_links
        return None
    except Exception as error:
        logger.error(f"Ошибка в получении ссылок на события: {error}")


def check_links(
    response: HTMLResponse, referee: str = "Koichiro FUKUSHIMA"
) -> List[str]:
    """Finding the right referee

    Args:
        response (HTMLResponse): Response object
        referee: str: Name of the referee

    Returns:
        List[str]: List with match information
    """
    url = response.url
    if is_completed_event(url):
        return None
    try:
        match_info = []
        rs_match_info = response.html.find("div.match-extra-info-item")
        label, value = rs_match_info[3].text.split('\n')
        logger.warning(f"Проверяем линк: {url} Судья: {label} - {value}")
        if value.lower() == referee.lower():
            write_file(url)
            event_status.append(url)
            # Get teams name
            teams: list = response.html.find("div.match-details-header__info > h1")
            match_info.append(
                teams[0].text.strip().replace(",", '').replace("VS", "\U0001F19A")
            )
            # Referee name
            match_info.append(value)
            # Match url
            match_info.append(url)
            return match_info
        return None
    except Exception as error:
        logger.error(f"Ошибка: {error} в получении информации о событии: {url}")


def is_completed_event(url: str) -> bool:
    if event_status:
        return url in event_status
    return False
