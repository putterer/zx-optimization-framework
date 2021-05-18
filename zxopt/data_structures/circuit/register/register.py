from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from zxopt.data_structures.circuit.circuit import Circuit

class Register:
    circuit: "Circuit"
    bits: list["RegisterBit"]
    name: Optional[str]

    def __init__(self, name: Optional[str] = None):
        self.name = name
        self.circuit = None
        self.bits = []

    def __getitem__(self, index) -> "RegisterBit":
        return self.bits[index]

    def get_bit_index(self, bit: "RegisterBit") -> int:
        return self.bits.index(bit)

class RegisterBit:
    register: Register

    def __init__(self, register: Register):
        self.register = register

    def get_name(self) -> str:
        return f"{self.register.name}[{self.register.get_bit_index(self)}]"