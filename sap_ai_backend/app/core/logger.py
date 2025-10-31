import logging, os
from logging.handlers import RotatingFileHandler

def get_logger(name: str) -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | [%(name)s] | %(message)s")

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        file = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=3)
        file.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(file)
    return logger