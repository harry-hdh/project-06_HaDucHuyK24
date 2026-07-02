from .config import LOG_PATH
from .untils import check_and_create_file
import logging
import sys

  # Ensure log directory exists

def setup_logging():
    check_and_create_file(LOG_PATH)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger(__name__)
    return logger