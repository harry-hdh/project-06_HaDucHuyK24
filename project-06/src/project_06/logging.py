from .config import LOG_PATH
import os
from pathlib import Path
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

def check_and_create_file(file_path):
    if not os.path.exists(file_path):
        parent_dir = os.path.dirname(file_path)
        Path(parent_dir).mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            pass  # Just create the file