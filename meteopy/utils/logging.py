from __future__ import annotations

import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str, log_level: int | str = logging.DEBUG) -> logging.Logger:
    log_file = LOG_DIR / f"{name}.log"  # Każdy moduł ma swój plik logów

    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Zapobiega duplikowaniu handlerów
        logger.setLevel(log_level)

        formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
