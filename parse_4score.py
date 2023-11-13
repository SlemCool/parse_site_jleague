from typing import List
from requests_html import HTMLResponse


def get_trends(response: HTMLResponse) -> List[str]:
    try:
        teams = response.html.find("div.trend-blocks", first=True)
        test = teams.text.split("\n")
        if test:
            return "\n".join(test)
        return None
    except Exception as error:
        print(f"Ошибка получения трендов {error}")
