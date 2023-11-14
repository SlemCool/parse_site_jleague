from typing import List

from requests_html import HTMLResponse, HTMLSession

from log import logger


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
        logger.error(f"Ошибка в получении или рендеринге запроса: {error}")


def get_links(response: HTMLResponse) -> List[str]:
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


def check_links(response: HTMLResponse) -> List[str]:
    """Finding the right referee

    Args:
        response (HTMLResponse): Response object

    Returns:
        List[str]: List with match information
    """
    try:
        match_info = []
        teams = response.html.find("div.summary-teams", first=True)
        team_1, team_2, _ = teams.text.split("\n")
        match_info.append(team_1 + " \U0001F19A " + team_2)
        extra_block = response.html.find("div.match-extra-info-item")
        flag = False
        for info in extra_block:
            label, value = info.text.split("\n")
            if label == "Referee" and value == "Koichiro FUKUSHIMA":
                flag = True
                match_info.append(value)
        if flag:
            return match_info
        return None
    except Exception as error:
        logger.error(f"Ошибка в получении информации о событии: {error}")


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
            events_links = [list(event.links)[0] for event in events]
            print(events_links)
            print(len(events_links))
            if events_links:
                return events_links
        return None
    except Exception as error:
        logger.error(f"Ошибка в получении ссылок на события: {error}")
        

url = 'https://www.jleague.co/fixtures/stage/j1/2023/32/all/'
get_links_from_fixtures(get_page_as_response(url))