import logging

def get_ai_logger(name: str = "sentinel.ai"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

ai_logger = get_ai_logger()
