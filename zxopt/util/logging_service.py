import logging
import sys

from zxopt.util.config_service import config
from zxopt.util.toolbox import is_interactive


def logger(class_type: type):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')

    logger = logging.getLogger(class_type.__name__)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if config["logging"]["log_to_file"] == "True":
        file_handler = logging.FileHandler(config["logging"]["log_file"])
        logger.addHandler(file_handler)

    if is_interactive():
        logger.setLevel(logging.getLevelName(config.get(section="logging", option="level_interactive", fallback="WARN")))
    else:
        logger.setLevel(logging.getLevelName(config.get(section="logging", option="level", fallback="WARN")))

    return logger
