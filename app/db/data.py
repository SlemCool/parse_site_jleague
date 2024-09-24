import os
from typing import Union

from config import app_logger

logger = app_logger.get_logger(__name__)
if not os.path.isdir("data"):
    os.mkdir("data")


def write_file(data: Union[list, str], file_name: str, method: str = "a") -> None:
    """Writes data to the file

    Args:
        data (Union[list, str]): data to write
        file_name: name of the file to read
        method (str): method to write
    """
    try:
        with open(file_name, method, encoding="utf-8") as file:
            if type(data) is str:
                file.write(data + "\n")
                logger.info("Записываем в файл: %s данные: %s", file_name, data)

            if type(data) is list:
                for el in data:
                    file.write(el + "\n")
                logger.info("Записываем в файл: %s", file_name)
    except Exception as error:
        logger.error("Ошибка записи: %s Файл: %s Данные: %s", error, file_name, data)


def read_file(file_name: str) -> list:
    """Read event data from file

    Args:
        file_name: name of the file to read
    Returns:
        list: list with url of complied events
    """
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            logger.info("Считываем файл: %s", file_name)
            return list(map(str.strip, file.readlines()))
    except Exception as error:
        logger.error("Ошибка чтения: %s Файл: %s", error, file_name)


def create_data_file(file_name: str) -> None:
    """Creates a new file in UTF-8 encoding
    If the file already exists, it will not be overwritten.

    Args:
        file_name: name of the file to create
    """
    try:
        with open(file_name, "x", encoding="utf-8") as _:
            logger.info("Создаем файл: %s", file_name)
            pass
    except FileExistsError:
        logger.info("Файл: %s уже создан. Пропускаем создание", file_name)
    except Exception as error:
        logger.error("Ошибка создания файла: %s", error)
