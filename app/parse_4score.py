from typing import Optional

import app_logger
from selenium.webdriver.common.by import By
from seleniumbase import SB

logger = app_logger.get_logger(__name__)


def get_trends(url: str) -> Optional[str]:
    """get trends from a response site 4score

    Args:
        response (HTMLResponse): response site

    Returns:
        List[str]: list of trends
    """
    try:
        with SB(
            uc=True,
            headless=True,
            page_load_strategy="eager",
            block_images=True,
        ) as driver:
            driver.get(url)
            trends = driver.find_element(By.CSS_SELECTOR, "[class='trend-blocks']")
            trends = trends.text.split("\n")
            if trends:
                data = ["-" + trend for trend in trends]
                logger.info("Тренды для судьи получены")
                return "\n".join(data)
        return None
    except Exception as error:
        logger.error(f"Ошибка получения трендов {error}")
