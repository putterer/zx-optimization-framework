import os
import re

from antlr4 import InputStream
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.tree.Tree import ParseTreeWalker

from antlr.OpenQASMLexer import OpenQASMLexer
from antlr.OpenQASMListener import OpenQASMListener
from antlr.OpenQASMParser import OpenQASMParser
from zxopt.data_structures.circuit import Circuit
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister
from zxopt.util import Loggable

INCLUDE_PATTERN = r"include\s+\"([a-zA-Z0-9_\\-\\.]+)\"\s*;"

class OpenQasmParser(Loggable, OpenQASMListener):
    def __init__(self):
        super().__init__()
        self.circuit: Circuit = Circuit()
        self.version: str = ""
        self.working_directory: str = "."  # the directory the file loaded is from for relative includes
        self.includes = []
        self.registers = {}

    def load_file(self, filename: str) -> Circuit:
        self.working_directory = os.path.dirname(os.path.realpath(filename))
        self.includes.append(os.path.realpath(filename))
        with open(filename, "r") as file:
            return self.load(file.read())

    def load(self, input: str) -> Circuit:
        self.__parse_input(input)
        return self.circuit

    def __parse_input(self, input: str):
        self.log.debug("Parsing qasm")
        program = self.__resolve_includes(input)

        lexer = OpenQASMLexer(InputStream(program))
        stream = CommonTokenStream(lexer)
        parser = OpenQASMParser(stream)
        tree = parser.mainprogram()
        walker = ParseTreeWalker()
        walker.walk(self, tree)

        self.log.info("Parsed OpenQASM successfully")



    def enterVersion(self, ctx: OpenQASMParser.VersionContext):
        self.version = str(ctx.REAL())
        self.log.debug(f"Detected OpenQASM version: {self.version}")
        if self.version != "2.0":
            raise NotImplementedError(f"Unsupported version: {self.version}, this parser only supports version 2.0")

    def enterQreg_decl(self, ctx:OpenQASMParser.Qreg_declContext):
        register_name = ctx.ID().getText()
        bit_count = int(ctx.NNINTEGER().getText())

        register = QuantumRegister(bit_count)
        self.registers[register_name] = register

        self.circuit.add_register(register)
        self.log.debug(f"Added {register_name} register with {bit_count} qubits")

    def enterCreg_decl(self, ctx:OpenQASMParser.Qreg_declContext):
        register_name = ctx.ID().getText()
        bit_count = int(ctx.NNINTEGER().getText())

        register = QuantumRegister(bit_count)
        self.registers[register_name] = register

        self.circuit.add_register(register)
        self.log.debug(f"Added {register_name} register with {bit_count} qubits")

    """
    Iteratively resolves all includes specified in the file and inserts them into the program
    """
    def __resolve_includes(self, program: str) -> str:
        while True:
            program = self.__eliminate_comments(program)  # include might be commented
            match = re.search(INCLUDE_PATTERN, program)
            if match:
                filename = os.path.join(self.working_directory, match.group(1))
                if os.path.realpath(filename) in self.includes:
                    raise RuntimeError(f"File {os.path.realpath(filename)} was already included, might be a circular dependency")
                self.includes.append(os.path.realpath(filename))

                self.log.debug(f"Including: {filename}")
                with open(filename, "r") as file:
                    program = program.replace(match.group(0), "\n" + file.read() + "\n", 1)
            else:
                return program

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
    parser = OpenQasmParser()
    circuit = parser.load_file("circuits/bell_swap.qasm")