import os
import re

from zxopt.data_structures.circuit import Circuit
from zxopt.util import Loggable

VAR_NAME = "[a-z][a-zA-Z0-9_]*"

class OpenQASMParser(Loggable):
    def __init__(self):
        super().__init__()
        self.circuit = Circuit()
        self.working_directory: str = "."  # the directory the file loaded is from for relative includes
        self.version: str = ""

        self.handlers = {
            self.__parse_version: ["OPENQASM (\\d+\\.\\d+)"],
            self.__parse_include: ["include \"([a-zA-Z0-9_\\-\\.]+)\""],
            self.__parse_register: [f"(qreg|creg) ({VAR_NAME})\\[(\d+)\\]"]
        }

    def load_file(self, filename: str) -> Circuit:
        self.working_directory = os.path.dirname(os.path.realpath(filename))
        with open(filename, "r") as file:
            return self.load(file.read())

    def load(self, input: str) -> Circuit:
        self.__parse_input(input)
        return self.circuit

    def __parse_input(self, input: str):
        statements = self.__get_statements(input)
        self.__parse_statements(statements)

    def __parse_statements(self, statements: list[str]):
        for statement in statements:
            self.__parse_statement(statement)

        return self.circuit

    def __parse_statement(self, statement: str):
        for handler, patterns in self.handlers.items():
            for pattern in patterns:
                match = re.fullmatch(pattern, statement)
                if match:
                    handler(match)
                    return

        raise RuntimeError("Could not parse statement: \"" + statement + "\"")

    def __parse_version(self, match: re.Match):
        if self.version != "":
            raise RuntimeError("Duplicate specification of version")
        self.version = match.group(1)
        self.log.debug(f"Detected OpenQASM version: {self.version}")

        if self.version != "2.0":
            raise NotImplementedError(f"Unsupported version: {self.version}, this parser only supports version 2.0")

    def __parse_include(self, match: re.Match):
        filename = os.path.join(self.working_directory, match.group(1))
        self.log.debug(f"Including: {filename}")

        with open(filename, "r") as file:
            self.__parse_input(file.read())

    def __parse_register(self, match: re.Match):
        reg_type = match.group(1)
        name = match.group(2)
        size = int(match.group(3))

        if type == "qreg":
            pass
        elif type == "creg":
            pass
        else:
            raise NotImplementedError(f"Unsupported register type {reg_type}")

    """
    Returns the statements contained in the input(separated by semicolons) as a list, removes empty statements, removes comments
    """
    def __get_statements(self, input: str) -> list[str]:
        input_no_comments = self.__eliminate_comments(input)

        statements = []
        last_semicolon = -1
        while True:
            next_semicolon = input_no_comments.find(";", last_semicolon + 1)
            if next_semicolon == -1:
                break
            statements.append(input_no_comments[last_semicolon + 1:next_semicolon:])
            last_semicolon = next_semicolon

        statements = [s.replace("\n", " ").strip() for s in statements]
        statements = list(filter(lambda s: s != "", statements))
        return statements

    """
    Eliminates all line and block comments from the input
    """
    def __eliminate_comments(self, input: str) -> str:
        # block comments
        while True:
            comment_start = input.find("/*")
            if comment_start == -1:
                break
            comment_end = input.find("*/", comment_start)
            if comment_end == -1:
                raise RuntimeError("failed to parse qasm due to non-ending comment")
            input = input[0:comment_start:] + input[comment_end + 2::]

        # line comments
        lines = [line.strip() for line in input.split("\n")]
        lines = list(map(lambda line: line.split("//")[0], lines))
        lines = list(filter(lambda line: line != "", lines))
        return "\n".join(lines)


if __name__ == "__main__":
    parser = OpenQASMParser()
    circuit = parser.load_file("circuits/bell_swap.qasm")