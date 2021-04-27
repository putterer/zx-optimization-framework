from src.util import logger


class Loggable:
    def __init__(self):
        self.log = logger(self.__class__)