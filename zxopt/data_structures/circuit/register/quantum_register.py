from typing import Optional

from zxopt.data_structures.circuit.register.register import Register, RegisterBit


class QuantumRegister(Register):
    def __init__(self, qubit_count: int, name: Optional[str] = None):
        super().__init__(name)

        for i in range(qubit_count):
            self.bits.append(QuantumBit(self))

class QuantumBit(RegisterBit):
    def __init__(self, register: QuantumRegister):
        super().__init__(register)
