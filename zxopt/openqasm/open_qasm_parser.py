from zxopt.data_structures.circuit import Circuit
from zxopt.util import Loggable


class OpenQasmParser(Loggable):
    def __init__(self):
        self.circuit: Circuit = Circuit()
        self.version: str = ""
        self.working_directory: str = "."  # the directory the file loaded is from for relative includes

