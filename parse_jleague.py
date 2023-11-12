from typing import List

from requests_html import HTMLResponse, HTMLSession

URL_SITE = "https://www.jleague.co/"


def get_page_as_response(url: str) -> HTMLResponse:
    try:
        session = HTMLSession()
        response = session.get(url)
        response.html.render(sleep=1, scrolldown=2)
        session.close()
        return response
    except Exception as e:
        print(f"Error rendering: {e}")


def get_links(response: HTMLResponse) -> List[str]:
    first_block = response.html.find("div.games-list", first=True)
    if first_block:
        events_links = list(first_block.links)
        if events_links:
            return events_links
    return None


def check_links(response: HTMLResponse) -> List[str]:
    match_info = []
    teams = response.html.find("div.summary-teams", first=True)
    team_1, team_2, _ = teams.text.split("\n")
    match_info.append(team_1 + " VS " + team_2)
    extra_block = response.html.find("div.match-extra-info-item")
    flag = False
    for info in extra_block:
        label, value = info.text.split("\n")
        if label.startswith("Temperature"):
            match_info.append(value)
        if label == "Referee" and value == "Koichiro FUKUSHIMA":
            flag = True
            match_info.append(value)
    if flag:
        return match_info
    return None


rs = get_page_as_response(URL_SITE)
game_links = get_links(rs)
# rs = get_page_as_response("https://www.jleague.co/match/j1/2023092308/")
print(get_links(rs))
