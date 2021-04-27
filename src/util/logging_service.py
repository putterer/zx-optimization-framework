import logging
import sys

from src.util import config


def logger(class_type: type):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(class_type.__name__)
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.getLevelName(config.get(section="logging", option="level", fallback="WARN")))
    return logger
