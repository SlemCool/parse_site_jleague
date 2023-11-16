from log import logger

DATA_FILE_NAME = "event_data.txt"


def write_file(data: str) -> None:
    """Writes data to the file

    Args:
        data (str): data to write
    """
    try:
        with open(DATA_FILE_NAME, "a", encoding="utf-8") as file:
            file.write(data + "\n")
    except Exception as error:
        logger.debug(f"Ошибка записи: {error} Файл: {DATA_FILE_NAME} Данные: {data}")


def read_file() -> list:
    """Read event data from file

    Returns:
        list: list with url of complied events
    """
    try:
        with open(DATA_FILE_NAME, "r", encoding="utf-8") as file:
            return list(map(str.strip, file.readlines()))
    except Exception as error:
        logger.debug(f"Ошибка чтения: {error} Файл: {DATA_FILE_NAME}")


def create_data_file() -> None:
    """Creates a new file named "event_data.txt" in UTF-8 encoding
    If the file already exists, it will not be overwritten."""
    try:
        with open(DATA_FILE_NAME, "x", encoding="utf-8") as _:
            pass
    except FileExistsError:
        logger.debug("Файл уже создан. Пропускаем создание")
    except Exception as error:
        logger.debug(f"Создание файла: {error}")
