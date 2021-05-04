from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from zxopt.data_structures.circuit.circuit import Circuit

class Register:
    def __init__(self):
        self.circuit: "Circuit" = None
        self.bits: list[RegisterBit] = []

    def __getitem__(self, index):
        return self.bits[index]

class RegisterBit:
    def __init__(self, register: Register):
        self.register: Register = register