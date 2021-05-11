import os

from zxopt.data_structures.circuit import Circuit
from zxopt.util import Loggable


class OpenQasmParser(Loggable):
    def __init__(self):
        self.circuit: Circuit = Circuit()
        self.version: str = ""
        self.working_directory: str = "."  # the directory the file loaded is from for relative includes

    def load_file(self, filename: str) -> Circuit:
        self.working_directory = os.path.dirname(os.path.realpath(filename))
        with open(filename, "r") as file:
            return self.load(file.read())

    def load(self, input: str) -> Circuit:
        self.__parse_input(input)
        return self.circuit

    def __parse_input(self, input: str):
        pass

if __name__ == "__main__":
    parser = OpenQasmParser()
    circuit = parser.load_file("circuits/bell_swap.qasm")