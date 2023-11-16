from log import logger

DATA_FILE = "event_data.txt"


def write_file(data: str) -> None:
    try:
        with open(DATA_FILE, "a", encoding="utf-8") as file:
            file.write(data + "\n")
    except Exception as error:
        logger.debug(f"Ошибка записи: {error} Файл: {DATA_FILE} Данные: {data}")


def read_file() -> list:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return list(map(str.strip, file.readlines()))
    except Exception as error:
        logger.debug(f"Ошибка чтения: {error} Файл: {DATA_FILE}")


def create_data_file():
    try:
        file = open(DATA_FILE, "x", encoding="utf-8")
        file.close()
    except Exception as error:
        logger.debug(f"Создание файла: {error}")
