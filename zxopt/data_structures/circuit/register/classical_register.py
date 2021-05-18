from typing import Optional

from zxopt.data_structures.circuit.register.register import Register, RegisterBit


class ClassicalRegister(Register):
    def __init__(self, bit_count: int, name: Optional[str] = None):
        super().__init__(name)

        for i in range(bit_count):
            self.bits.append(ClassicalBit(self))

class ClassicalBit(RegisterBit):
    def __init__(self, register: ClassicalRegister):
        super().__init__(register)
