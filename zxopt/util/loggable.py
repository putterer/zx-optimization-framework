from zxopt.util.logging_service import logger

"""
Represents a class that contains a logger for easy access
"""
class Loggable:
    def __init__(self):
        self.log = logger(self.__class__)