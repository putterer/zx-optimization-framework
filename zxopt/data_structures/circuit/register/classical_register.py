from zxopt.data_structures.circuit.register.register import Register, RegisterBit


class ClassicalRegister(Register):
    def __init__(self, bit_count: int):
        super().__init__()

        for i in range(bit_count):
            self.bits.append(ClassicalBit(self))

class ClassicalBit(RegisterBit):
    def __init__(self, register: ClassicalRegister):
        super().__init__(register)
