from typing import cast

from zxopt.data_structures.circuit.circuit_component import CircuitComponent
from zxopt.data_structures.circuit.register.classical_register import ClassicalRegister
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister
from zxopt.data_structures.circuit.register.register import RegisterBit, Register
from zxopt.util.toolbox import flat_map


class Circuit:
    def __init__(self):
        self.components: set[CircuitComponent] = set()
        self.quantum_registers: list[QuantumRegister] = []
        self.classical_registers: list[ClassicalRegister] = []

    def add_component(self, component: CircuitComponent):
        component.set_circuit(self)

        last_affected_step = max([c.step for c in self.get_components_affecting_bits(component.affected_bits)], default=-1)
        component.step = last_affected_step + 1

        self.components.add(component)

    def remove_component(self, component: CircuitComponent):
        component.circuit = None
        self.components.remove(component)

    """
    Returns all components that affect any of the specified bits
    """
    def get_components_affecting_bits(self, bits: set[RegisterBit]):
        return set(filter(lambda c: any([bit in c.affected_bits for bit in bits]), self.components))

    def add_register(self, register: Register):
        if isinstance(register, QuantumRegister):
            self.quantum_registers.append(register)
        elif isinstance(register, ClassicalRegister):
            self.classical_registers.append(register)
        else:
            raise NotImplementedError("Unsupported register type")
        register.circuit = self

    def remove_register(self, register: Register):
        if isinstance(register, QuantumRegister):
            self.quantum_registers.remove(register)
        elif isinstance(register, ClassicalRegister):
            self.classical_registers.remove(register)
        else:
            raise NotImplementedError("Unsupported register type")
        register.circuit = self

    def get_registers(self) -> list[Register]:
        return cast(list[Register], self.quantum_registers) + cast(list[Register], self.classical_registers)

    def get_register_bits(self) -> list[RegisterBit]:
        return self.get_quantum_bits() + self.get_classical_bits()

    def get_quantum_bits(self) -> list[RegisterBit]:
        return flat_map(lambda reg: reg.bits, self.quantum_registers)

    def get_classical_bits(self) -> list[RegisterBit]:
        return flat_map(lambda reg: reg.bits, self.classical_registers)

    def get_register_from_bit(self, bit: RegisterBit) -> Register:
        return list(filter(lambda reg: bit in reg, self.get_registers()))[0]

    def step_count(self) -> int:
        return max([c.step for c in self.components]) + 1

    def get_components_by_step(self, step: int) -> list[CircuitComponent]:
        return list(filter(lambda c: c.step == step, self.components))

