from typing import List

from requests_html import HTMLResponse

import app_logger

logger = app_logger.get_logger(__name__)


def get_trends(response: HTMLResponse) -> List[str]:
    """get trends from a response site 4score

    Args:
        response (HTMLResponse): response site

    Returns:
        List[str]: list of trends
    """
    try:
        teams = response.html.find("div.trend-blocks", first=True)
        trends = teams.text.split("\n")
        if trends:
            data = ["-" + trend for trend in trends]
            logger.info("Тренды для судьи получены")
            return "\n".join(data)
        return None
    except Exception as error:
        logger.error(f"Ошибка получения трендов {error}")