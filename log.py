import logging
import sys

logging.basicConfig(
    handlers=[logging.FileHandler(filename="main.log", encoding="utf-8")],
    format="%(asctime)s  %(name)s, %(levelname)s, %(message)s",
    datefmt="%F %A %T",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)
