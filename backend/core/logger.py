import logging
import sys
from pathlib import Path

try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False


def setup_logger(name: str) -> logging.Logger:
    from core.config import settings
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    
    if logger.handlers:
        return logger
    
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    try:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        if HAS_JSON_LOGGER:
            json_format = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s'
            )
            file_handler.setFormatter(json_format)
        else:
            file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        pass
    
    return logger
