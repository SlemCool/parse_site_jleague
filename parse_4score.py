from typing import List

from requests_html import HTMLResponse


def get_trends(response: HTMLResponse) -> List[str]:
    try:
        teams = response.html.find("div.trend-blocks", first=True)
        trends = teams.text.split("\n")
        if trends:
            data = ["-" + trend for trend in trends]
            # for trend in trends:
            #     data.append("-" + trend)
            return "\n".join(data)
        return None
    except Exception as error:
        print(f"Ошибка получения трендов {error}")
