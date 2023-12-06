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
                logger.info(f"Записываем в файл: {file_name} данные: {data}")

            if type(data) is list:
                for el in data:
                    file.write(el + "\n")
                logger.info(f"Записываем в файл: {file_name}")
    except Exception as error:
        logger.error(f"Ошибка записи: {error} Файл: {file_name} Данные: {data}")


def read_file(file_name: str) -> list:
    """Read event data from file

    Args:
        file_name: name of the file to read
    Returns:
        list: list with url of complied events
    """
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            logger.info(f"Считываем файл: {file_name}")
            return list(map(str.strip, file.readlines()))
    except Exception as error:
        logger.error(f"Ошибка чтения: {error} Файл: {file_name}")


def create_data_file(file_name: str) -> None:
    """Creates a new file in UTF-8 encoding
    If the file already exists, it will not be overwritten.

    Args:
        file_name: name of the file to create
    """
    try:
        with open(file_name, "x", encoding="utf-8") as _:
            logger.info(f"Создаем файл: {file_name}")
            pass
    except FileExistsError:
        logger.info(f"Файл: {file_name} уже создан. Пропускаем создание")
    except Exception as error:
        logger.error(f"Ошибка создания файла: {error}")
