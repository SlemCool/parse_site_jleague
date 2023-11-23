import os

import app_logger

logger = app_logger.get_logger(__name__)
if not os.path.isdir("data"):
    os.mkdir("data")
DATA_FILE_NAME = "data/event_data.txt"


def write_file(data: str) -> None:
    """Writes data to the file

    Args:
        data (str): data to write
    """
    try:
        with open(DATA_FILE_NAME, "a", encoding="utf-8") as file:
            file.write(data + "\n")
            logger.info(
                f"Записываем в файл: {DATA_FILE_NAME} отработанную ссылку: {data}"
            )
    except Exception as error:
        logger.error(f"Ошибка записи: {error} Файл: {DATA_FILE_NAME} Данные: {data}")


def read_file() -> list:
    """Read event data from file

    Returns:
        list: list with url of complied events
    """
    try:
        with open(DATA_FILE_NAME, "r", encoding="utf-8") as file:
            logger.info(f"Считываем файл: {DATA_FILE_NAME} для передачи в переменную")
            return list(map(str.strip, file.readlines()))
    except Exception as error:
        logger.error(f"Ошибка чтения: {error} Файл: {DATA_FILE_NAME}")


def create_data_file() -> None:
    """Creates a new file named "event_data.txt" in UTF-8 encoding
    If the file already exists, it will not be overwritten."""
    try:
        with open(DATA_FILE_NAME, "x", encoding="utf-8") as _:
            logger.info(f"Создаем файл для отработанных ссылок: {DATA_FILE_NAME}")
            pass
    except FileExistsError:
        logger.info(f"Файл: {DATA_FILE_NAME} уже создан. Пропускаем создание")
    except Exception as error:
        logger.error(f"Ошибка создания файла: {error}")
