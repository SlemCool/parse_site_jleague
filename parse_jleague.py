from typing import List

from requests_html import HTMLResponse, HTMLSession

from log import logger

event_status = {'https://www.jleague.co/match/j1/2023082607/': 'Completed', 'https://www.jleague.co/match/j1/2023090315/': 'Completed'}


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
        teams = response.html.find("div.summary-teams", first=True)
        team_1, team_2, _ = teams.text.split("\n")
        match_info.append(team_1 + " \U0001F19A " + team_2)
        extra_block = response.html.find("div.match-extra-info-item")
        for info in extra_block:
            label, value = info.text.split("\n")
            if label == "Referee" and value.lower() == referee.lower():
                event_status[url] = "Completed"
                match_info.append(value)
                match_info.append(url)
                return match_info
        return None
    except Exception as error:
        logger.error(f"Ошибка: {error} в получении информации о событии: {url}")


def is_completed_event(url: str) -> bool:
    return bool(event_status.get(url))


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
                return events_links
        return None
    except Exception as error:
        logger.error(f"Ошибка в получении ссылок на события: {error}")


URL_BET = "https://www.jleague.co"
for i in range(25, 33):
    url = f"https://www.jleague.co/fixtures/stage/j1/2023/{i}/"
    links = get_links_from_fixtures(get_page_as_response(url))
    for link in links:
        event_check = check_links(get_page_as_response(URL_BET + link))
        if event_check:
            print(event_check)
