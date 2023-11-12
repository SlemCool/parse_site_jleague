from typing import List
from requests_html import HTMLResponse, HTMLSession

URL_SITE = "https://4score.ru/referee/18910/"


def get_page_as_response(url: str) -> HTMLResponse:
    try:
        session = HTMLSession()
        response = session.get(url)
        response.html.render(sleep=1, scrolldown=2)
        session.close()
        return response
    except Exception as e:
        print(f"Error rendering: {e}")


def check_links(response: HTMLResponse) -> List[str]:
    teams = response.html.find("div.trend-blocks", first=True)
    test = teams.text.split("\n")
    if test:
        return '\n'.join(test)
    return None


rs = get_page_as_response(URL_SITE)
print('Тренды для судьи Koichiro Fukushima:')
print(check_links(rs))
print('По данным сайта 4SCORE')
