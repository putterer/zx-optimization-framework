import math
import os
import re

from antlr4 import InputStream
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.tree.Tree import ParseTreeWalker

from antlr.OpenQASMLexer import OpenQASMLexer
from antlr.OpenQASMListener import OpenQASMListener
from antlr.OpenQASMParser import OpenQASMParser
from zxopt.data_structures.circuit import Circuit, MeasurementComponent, GateComponent, UnitaryGate, PauliXGate
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister, QuantumBit
from zxopt.data_structures.circuit.register.register import RegisterBit
from zxopt.util import Loggable

INCLUDE_PATTERN = r"include\s+\"([a-zA-Z0-9_\\-\\.]+)\"\s*;"
TRACE = False

class OpenQasmParser(Loggable, OpenQASMListener):
    def __init__(self):
        super().__init__()
        self.circuit: Circuit = Circuit()
        self.version: str = ""
        self.working_directory: str = "."  # the directory the file loaded is from for relative includes
        self.includes = []
        self.registers = {}
        self.gate_declarations = {}

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

    # TODO: how to parse sub gates?
    # function that generates it?
    # sub circuit where the bits get swapped?
    # just save text and parse later again? (maybe with same handler)

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


    def enterMeasure(self, ctx:OpenQASMParser.MeasureContext):
        if not isinstance(ctx.parentCtx.parentCtx, OpenQASMParser.StatementqopContext):
            raise NotImplementedError("Only statement QOPs are supported, no conditionals!")

        source_registers = self.__get_registers_bits(ctx.argument(0))
        target_registers = self.__get_registers_bits(ctx.argument(1))

        if len(source_registers) != len(target_registers):
            raise RuntimeError(f"Source and target register sizes for measurement must match! ({ctx.argument(0).getText()} -> {ctx.argument(1).getText()})")

        for i in range(len(source_registers)):
            self.circuit.add_component(MeasurementComponent(source_registers[i], target_registers[i]))
        self.log.debug(f"Added {len(source_registers)} measurements ({ctx.argument(0).getText()} -> {ctx.argument(1).getText()})")

    def enterReset_op(self, ctx:OpenQASMParser.Reset_opContext):
        if not isinstance(ctx.parentCtx.parentCtx, OpenQASMParser.StatementqopContext):
            raise NotImplementedError("Only statement QOPs are supported, no conditionals!")

        registers = self.__get_registers_bits(ctx.argument())
        raise NotImplementedError("Reset functionality not implemented")

    def enterBarrier(self, ctx:OpenQASMParser.BarrierContext):
        if not isinstance(ctx.parentCtx, OpenQASMParser.StatementContext):
            return # we are running through a gate definition, ignore

        self.log.warning("Ignoring barrier, not yet supported")

    """
    A single unitary operation, not located within a gate statement
    """
    def enterUop(self, ctx:OpenQASMParser.UopContext):
        if not isinstance(ctx.parentCtx, OpenQASMParser.QopContext):
            return # we are running through a gate definition, ignore
        if not isinstance(ctx.parentCtx.parentCtx, OpenQASMParser.StatementqopContext):
            raise NotImplementedError("Only statement QOPs are supported, no conditionals! Can be fixed easily.")

        self.apply_uop(ctx, {}, {})

    def apply_uop(self, ctx:OpenQASMParser.UopContext, bound_qubit_names: dict[str, QuantumBit], bound_names: dict[str, float]):
        gate_name = ctx.children[0].getText() # 'U', 'CX' or ID for custom gate
        params = params = ctx.explist().exp() if ctx.explist() else []
        qarg_contexts = []
        if ctx.argument():
            qarg_contexts += ctx.argument()
        if ctx.anylist():
            qarg_contexts += ctx.anylist().argument()

        qargs = []
        for ctx in qarg_contexts:
            if ctx.getText() in bound_qubit_names:
                qargs.append(bound_qubit_names[ctx.getText()])
            else:
                qargs.append(self.__get_registers_bit(ctx))

        self.apply_gate(gate_name, params, qargs, bound_names)


    def enterGatestmt(self, ctx:OpenQASMParser.GatestmtContext):
        gatedecl: OpenQASMParser.GatedeclContext = ctx.gatedecl()

        name = gatedecl.ID().getText()
        params = [node.getText() for node in gatedecl.gateparams().idlist().ID()] if gatedecl.gateparams() is not None else []
        qargs = [node.getText() for node in gatedecl.gateqargs().idlist().ID()]

        gate_declaration = GateDeclaration(name, params, qargs, ctx.goplist())
        self.gate_declarations[name] = gate_declaration

        if TRACE:
            self.log.debug(f"Defined gate \"{name}\" with params {params} and args {qargs}")

    """
    Applies the gate with the given name, recursively if necessary
    name:
        the name of the gate
    params: list[OpenQASMParser.ExpContext]
        the list of parameters (as contexts, not evaluated)
    qargs: list[QuantumBit]
        the qubits to apply the gate to
    """
    def apply_gate(self, name: str, params: list[OpenQASMParser.ExpContext], qargs: list[QuantumBit], bound_names: dict[str, float]):
        evaluator = ExpressionEvaluator(bound_names)
        evaluated_params = [evaluator.evaluate(ctx) for ctx in params]

        if name == "U" or name == "CX":
            self.apply_gate_builtin(name, evaluated_params, qargs)
        else:
            gate_declaration = self.gate_declarations[name]
            if gate_declaration:
                self.apply_gate_declaration(gate_declaration, evaluated_params, qargs)
            else:
                raise NotImplementedError("Unknown gate of type: " + name)



    def apply_gate_builtin(self, name: str, params: list[float], qargs: list[QuantumBit]):
        gate = None
        if name == "U":
            if len(qargs) != 1:
                raise RuntimeError(f"Expected 1 qubit for U gate, got {len(qargs)}")
            gate = GateComponent(qargs[0], UnitaryGate("U", params[0], params[1], params[2]))
        elif name == "CX":
            if len(qargs) != 2:
                raise RuntimeError(f"Expected 2 qubits for CX gate, got {len(qargs)}")
            gate = GateComponent(qargs[0], PauliXGate(), { qargs[1] })
        else:
            raise RuntimeError(f"Unknow gate type: {name}")

        if gate:
            self.circuit.add_component(gate)

            if TRACE:
                self.log.debug(f"Added gate: {gate.gate_type.representation}")

    """
    Applies a gate declaration recursively at the current location given a list of parameters
    """
    def apply_gate_declaration(self, gate: "GateDeclaration", params: list[float], qargs: list[QuantumBit]):
        if len(params) != len(gate.param_names) or len(qargs) != len(gate.qarg_names):
            raise RuntimeError(f"Param and qarg length of gate call no not match gate declaration\n"
                               f"params:  given: {len(params)}, required: {len(gate.param_names)}\n"
                               f"qargs:   given: {len(qargs)}, required: {len(gate.qarg_names)}\n")

        # bind specified params and args to their name in the gate declaration
        named_params: dict[str, float] = {}
        named_qargs: dict[str, QuantumBit] = {}
        for i in range(len(params)):
            named_params[gate.param_names[i]] = params[i]
        for i in range(len(qargs)):
            named_qargs[gate.qarg_names[i]] = qargs[i]

        # raise NotImplementedError() # TODO
        if TRACE:
            self.log.debug(f"Applying gate definition: {gate.name}, params: {named_params}")

        # apply the gate ops list
        for entry_ctx in gate.goplist_ctx.goplistentry():
            if entry_ctx.idlist(): # barrier
                raise NotImplementedError("Barriers are not yet implemented")
            elif entry_ctx.uop():
                self.apply_uop(entry_ctx.uop(), named_qargs, named_params)



    """
    Returns all registers bits specified by the given argument, may be multiple in case the bit in the register is not specified
    """
    def __get_registers_bits(self, ctx: OpenQASMParser.ArgumentContext) -> list[RegisterBit]:
        register_name = ctx.ID().getText()
        register = self.registers[register_name]
        if not register:
            raise RuntimeError(f"Register of name {register_name} not found")
        if ctx.NNINTEGER():
            bit_index = int(ctx.NNINTEGER().getText())
            return [ register.bits[bit_index] ]
        else:
            return register.bits

    """
    Returns register bit specified by the given argument, throws an error if index is not specified
    """
    def __get_registers_bit(self, ctx: OpenQASMParser.ArgumentContext) -> RegisterBit:
        register_bits = self.__get_registers_bits(ctx)
        if len(register_bits) != 1:
            raise RuntimeError(f"Expected one register bit, found multiple for: {ctx.getText()}")
        return register_bits[0]

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


"""
    A gate defined by the `gate` statement, only supports numerical parameters and qubit arguments
    Can be recursively applied to a circuit
"""
class GateDeclaration:
    def __init__(self, name: str, param_names: list[str], qarg_names: list[str], goplist_ctx: OpenQASMParser.GoplistContext):
        super().__init__()
        self.name = name
        self.param_names = param_names
        self.qarg_names = qarg_names
        self.goplist_ctx = goplist_ctx


class ExpressionEvaluator:
    def __init__(self, bound_names: dict[str, float]):
        self.bound_names: dict[str, float] = bound_names # the variables with given names (parameters)

    def evaluate(self, ctx: OpenQASMParser.ExpContext):
        if ctx.REAL():
            return float(ctx.REAL().getText())
        elif ctx.NNINTEGER():
            return float(ctx.NNINTEGER().getText())
        elif ctx.PI():
            return math.pi
        elif ctx.ID():
            return self.bound_names[ctx.ID().getText()]

        if ctx.unaryop():
            return self.evaluate_unaryop(ctx)

        if ctx.getText().startswith("("):
            return self.evaluate(ctx.exp(0))

        if ctx.getText().startswith("-"):
            return (-1.0) * self.evaluate(ctx.exp(0))

        return self.evaluate_binary_op(ctx)

    def evaluate_binary_op(self, ctx: OpenQASMParser.ExpContext):
        eval1 = self.evaluate(ctx.exp(0))
        eval2 = self.evaluate(ctx.exp(1))
        text = ctx.getText()
        if "+" in text:
            return eval1 + eval2
        elif "-" in text:
            return eval1 - eval2
        elif "*" in text:
            return eval1 * eval2
        elif "/" in text:
            return eval1 / eval2
        elif "^" in text:
            return eval1 ** eval2

        raise RuntimeError(f"Could not evaluate expression: {ctx.getText()}")



    def evaluate_unaryop(self, ctx: OpenQASMParser.ExpContext):
        funs = {
            "sin": lambda x: math.sin(x),
            "cos": lambda x: math.cos(x),
            "tan": lambda x: math.tan(x),
            "exp": lambda x: math.exp(x),
            "ln": lambda x: math.log(x, math.e),
            "sqrt": lambda x: math.sqrt(x)
        }
        return funs[ctx.unaryop().getText()](self.evaluate(ctx.exp(0)))


if __name__ == "__main__":
    parser = OpenQasmParser()
    circuit = parser.load_file("circuits/teleportation.qasm")